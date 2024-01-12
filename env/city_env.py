# reward definition
# 1) absolute distance to the goal
# 2) penalty off street (different agent different reward...1 agent first)
# 3) penalty of not stopping at the stopsign? 

import numpy as np
import torch

from core.city import City
import gym
from core.config import *
from utils.vis import visualize_city
from utils.gym_wrapper import GymCityWrapper
from utils.gen import gen_occ

WRAPPER = {
    "easy": GymCityWrapper,
    "medium": GymCityWrapper,
}


class CityEnv(City):
    def __init__(self, grid_size, local_planner, rule_file=None):
        super().__init__(grid_size, local_planner, rule_file)


    def update(self, action=None, idx=None):
        current_obs = {}
        # state at time t
        current_obs["World"] = self.city_grid.clone()
        current_obs["Agent_actions"] = []
        action_idx = None
        if action is not None:
            action_idx = torch.where(action)[0][0]
                
        new_matrix = torch.zeros_like(self.city_grid)
        current_world = self.city_grid.clone()
        # first do local planning based on city rules
        agent_action_dist = self.local_planner.plan(current_world, self.intersection_matrix, self.agents, \
                                                    self.layer_id2agent_list_id)
        # Then do global action taking acording to the local planning results
        # input((action_idx, idx))
        
        for agent in self.agents:
            # re-initialized agents may update city matrix as well
            agent_name = "{}_{}".format(agent.type, agent.layer_id)
            empty_action = agent.action_dist.clone()
            # local reasoning-based action distribution
            local_action_dist = agent_action_dist[agent_name]
            # get local occupancy map
            local_world = self.city_grid[:, agent.pos[0]-OCC_CHECK_RANGE//2:agent.pos[0]+OCC_CHECK_RANGE//2, \
                                            agent.pos[1]-OCC_CHECK_RANGE//2:agent.pos[1]+OCC_CHECK_RANGE//2].clone()
            local_occ_map = gen_occ(torch.cat([local_world[BASIC_LAYER:agent.layer_id], local_world[agent.layer_id+1:]]))
            occ_map = torch.zeros_like(self.city_grid[0])
            occ_map[agent.pos[0]-OCC_CHECK_RANGE//2:agent.pos[0]+OCC_CHECK_RANGE//2, \
                    agent.pos[1]-OCC_CHECK_RANGE//2:agent.pos[1]+OCC_CHECK_RANGE//2] = local_occ_map
            # global trajectory-based action or sampling from local action distribution
            if action is not None and agent.layer_id == idx: 
                current_obs["Agent_actions"].append(action)
            else:
                local_action, new_matrix[agent.layer_id] = agent.get_next_action(self.city_grid, local_action_dist, occ_map)
                # save the current action in the action
                empty_action[local_action] = 1.0    
                current_obs["Agent_actions"].append(empty_action)
            
            if agent.reach_goal:
                continue
            if action is not None and agent.layer_id == idx: 
                # print("update with: ", agent.pos, np.where(self.city_grid[agent.layer_id] == self.type2label[agent.type]))
                next_layer = agent.move(action_idx, self.city_grid[agent.layer_id].clone())
            else: 
                next_layer = agent.move(local_action, new_matrix[agent.layer_id])
            # print(torch.nonzero(next_layer), np.unique(next_layer), torch.nonzero((next_layer==8.0).float())[0])
            new_matrix[agent.layer_id] = next_layer
        # Update city grid after all the agents make decisions
        self.city_grid[BASIC_LAYER:] = new_matrix[BASIC_LAYER:]
        return current_obs
