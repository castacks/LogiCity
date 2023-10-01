from .basic import Agent
import torch
import torch.nn.functional as F
from torch.distributions import Categorical
from utils.find import find_nearest_building, find_building_mask
from utils.sample import sample_start_goal, sample_start_goal_vh, sample_determine_start_goal
from planners import GPlanner_mapper, LPlanner_mapper
from core.city import LABEL_MAP
import logging
# import cv2
# import numpy as np
# # vis quick tool
# vis = np.zeros((250, 250, 3))
# vis[self.movable_region] = [255, 0, 0]
# vis[self.goal[0], self.goal[1]] = [0, 255, 255]
# vis[self.start[0], self.start[1]] = [0, 255, 0]
# vis[self.midline_matrix] = [0, 0, 255]
# cv2.imwrite("test.png", vis)

logger = logging.getLogger(__name__)

TYPE_MAP = {v: k for k, v in LABEL_MAP.items()}

class Car(Agent):
    def __init__(self, type, size, id, world_state_matrix, global_planner, local_planner, rule_file=None):
        self.start_point_list = None
        self.goal_point_list = None
        self.global_planner_type = global_planner
        self.local_planner = LPlanner_mapper[local_planner](rule_file, world_matrix=world_state_matrix)
        super().__init__(type, size, id, world_state_matrix)
        # Actions: ["left_1", "right_1", "up_1", "down_1", "left_2", "right_2", "up_2", "down_2", "stop"]
        self.action_space = torch.tensor(range(9))
        self.action_to_move = {
            self.action_space[0].item(): torch.tensor((0, -1)),
            self.action_space[1].item(): torch.tensor((0, 1)),
            self.action_space[2].item(): torch.tensor((-1, 0)),
            self.action_space[3].item(): torch.tensor((1, 0)),
            self.action_space[4].item(): torch.tensor((0, -2)),
            self.action_space[5].item(): torch.tensor((0, 2)),
            self.action_space[6].item(): torch.tensor((-2, 0)),
            self.action_space[7].item(): torch.tensor((2, 0))
        }
        self.action_dist = torch.zeros_like(self.action_space).float()
        self.action_mapping = {
            0: "Left_1", 
            1: "Right_1", 
            2: "Up_1", 
            3: "Down_1", 
            4: "Left_2", 
            5: "Right_2", 
            6: "Up_2", 
            7: "Down_2",
            8: "Stop"
            }

    def init(self, world_state_matrix):
        Traffic_STREET = 2
        CROSSING_STREET = -1
        # self.start = torch.tensor(self.get_start(world_state_matrix))
        self.start, self.goal = sample_determine_start_goal(self.type, self.id)
        self.pos = self.start.clone()
        # self.goal = torch.tensor(self.get_goal(world_state_matrix, self.start))
        # specify the occupacy map
        self.movable_region = (world_state_matrix[2] == Traffic_STREET) | (world_state_matrix[2] == CROSSING_STREET)
        self.midline_matrix = (world_state_matrix[2] == Traffic_STREET+0.5)
        self.global_planner = GPlanner_mapper[self.global_planner_type](self.movable_region, self.midline_matrix, 2)
        # get global traj on the occupacy map
        self.global_traj = self.global_planner.plan(self.start, self.goal)
        logger.info("{}_{} initialization done!".format(self.type, self.id))

    def get_start(self, world_state_matrix):
        # Define the labels for different entities
        GAS = 4
        GARAGE = 6
        building = [GAS, GARAGE]
        # Find cells that are walking streets and have a house or office around them
        desired_locations = sample_start_goal_vh(world_state_matrix, 2, building, kernel_size=9)
        self.start_point_list = torch.nonzero(desired_locations).tolist()
        random_index = torch.randint(0, len(self.start_point_list), (1,)).item()
        
        # Fetch the corresponding location
        start_point = self.start_point_list[random_index]

        # Return the indices of the desired locations
        return start_point

    def get_goal(self, world_state_matrix, start_point):
        # Define the labels for different entities
        GAS = 4
        GARAGE = 6
        STORE = 7
        building = [GAS, GARAGE, STORE]

        # Find cells that are walking streets and have a house, office, or store around them
        self.desired_locations = sample_start_goal_vh(world_state_matrix, 2, building, kernel_size=9)
        desired_locations = self.desired_locations.detach().clone()

        # Determine the nearest building to the start point
        nearest_building = find_nearest_building(world_state_matrix, start_point)
        start_block = world_state_matrix[0][nearest_building[0], nearest_building[1]]

        # Get the mask for the building containing the nearest_building position
        # building_mask = find_building_mask(world_state_matrix, nearest_building)
        building_mask = world_state_matrix[0] == start_block
        
        # Create a mask to exclude areas around the building. We'll dilate the building mask.
        exclusion_radius = 7  # Excludes surrounding 3 grids around the building
        expanded_mask = F.max_pool2d(building_mask[None, None].float(), exclusion_radius, stride=1, padding=(exclusion_radius - 1) // 2) > 0
        
        desired_locations[expanded_mask[0, 0]] = False

        # Return the indices of the desired locations
        goal_point_list = torch.nonzero(desired_locations).tolist()
        random_index = torch.randint(0, len(goal_point_list), (1,)).item()
        
        # Fetch the corresponding location
        goal_point = goal_point_list[random_index]

        # Return the indices of the desired locations
        return goal_point

    def get_action(self, world_state_matrix):
        self.local_action = self.local_planner.plan(world_state_matrix, self.layer_id, \
            self.type, self.action_dist, self.action_mapping)
        if not torch.any(self.local_action):
            return self.get_global_action()
        else:
            # sample from the local planner
            normalized_action_dist = self.local_action / self.local_action.sum()
            dist = Categorical(normalized_action_dist)
            # Sample an action index from the distribution
            action_index = dist.sample()
            # Get the actual action from the action space using the sampled index
            return self.action_space[action_index]

    def get_next_action(self, world_state_matrix):
        # for now, just reckless take the global traj
        # reached goal
        if not self.reach_goal:
            if torch.all(self.pos == self.goal):
                # self.reach_goal = True
                logger.info("{}_{} reached goal! Will change goal in the next step!".format(self.type, self.id))
                return self.action_space[-1], world_state_matrix[self.layer_id]
            else:
                return self.get_action(world_state_matrix), world_state_matrix[self.layer_id]
        else:
            logger.info("Generating new goal and gloabl plans for {}_{}...".format(self.type, self.id))
            self.start = self.goal.clone()
            desired_locations = self.desired_locations.detach().clone()

            # Determine the nearest building to the start point
            nearest_building = find_nearest_building(world_state_matrix, self.start)

            # Get the mask for the building containing the nearest_building position
            building_mask = find_building_mask(world_state_matrix, nearest_building)
            
            # Create a mask to exclude areas around the building. We'll dilate the building mask.
            exclusion_radius = 7  # Excludes surrounding 3 grids around the building
            expanded_mask = F.max_pool2d(building_mask[None, None].float(), exclusion_radius, stride=1, padding=(exclusion_radius - 1) // 2) > 0
            
            desired_locations[expanded_mask[0, 0]] = False

            # Return the indices of the desired locations
            goal_point_list = torch.nonzero(desired_locations).tolist()
            random_index = torch.randint(0, len(goal_point_list), (1,)).item()
            
            # Fetch the corresponding location
            self.goal = torch.tensor(goal_point_list[random_index])
            self.global_traj = self.global_planner.plan(self.start, self.goal)
            logger.info("Generating new goal and gloabl plans for {}_{} done!".format(self.type, self.id))
            self.reach_goal = False
            # delete past traj
            world_state_matrix[self.layer_id] *= 0
            world_state_matrix[self.layer_id][self.goal[0], self.goal[1]] = TYPE_MAP[self.type] + 0.3
            for way_points in self.global_traj[1:-1]:
                world_state_matrix[self.layer_id][way_points[0], way_points[1]] \
                    = TYPE_MAP[self.type] + 0.1
            world_state_matrix[self.layer_id][self.start[0], self.start[1]] = TYPE_MAP[self.type]

            return self.get_action(world_state_matrix), world_state_matrix[self.layer_id]

    def get_global_action(self):
        next_pos = self.global_traj[0]
        self.global_traj.pop(0)
        del_pos = next_pos - self.pos
        if del_pos[1] < 0:
            # left
            return self.action_space[0] if torch.abs(del_pos[1]) == 1 else self.action_space[4]
        elif del_pos[1] > 0:
            # right
            return self.action_space[1] if torch.abs(del_pos[1]) == 1 else self.action_space[5]
        elif del_pos[0] < 0:
            # up
            return self.action_space[2] if torch.abs(del_pos[0]) == 1 else self.action_space[6]
        elif del_pos[0] > 0:
            # down
            return self.action_space[3] if torch.abs(del_pos[0]) == 1 else self.action_space[7]
        else:
            return self.action_space[-1]

    def move(self, action, ped_layer):
        curr_pos = torch.nonzero((ped_layer==TYPE_MAP[self.type]).float())[0]
        assert torch.all(self.pos == curr_pos)
        next_pos = self.pos.clone()
        # becomes walked grid
        ped_layer[self.pos[0], self.pos[1]] -= 0.1
        next_pos += self.action_to_move.get(action.item(), torch.tensor((0, 0)))
        self.pos = next_pos.clone()
        # Update Agent Map
        ped_layer[self.start[0], self.start[1]] = TYPE_MAP[self.type] - 0.2
        ped_layer[self.goal[0], self.goal[1]] = TYPE_MAP[self.type] + 0.3
        ped_layer[self.pos[0], self.pos[1]] = TYPE_MAP[self.type]
        return ped_layer