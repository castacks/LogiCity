import torch

class Agent:
    def __init__(self, type, size, id, world_state_martix):
        self.size = size
        self.type = type
        self.id = id
        # Actions: ["left", "right", "up", "down", "stop"]
        self.action_space = torch.tensor(range(5))
        self.start = None
        self.goal = None
        self.pos = None
        self.init(world_state_martix)

    def init(self, world_state_martix, global_planner=None, local_planner=None):
        # init global planner, global traj, local planner, start and goal point
        pass

    def get_start(self, world_state_martix):
        pass

    def get_goal(self, world_state_martix):
        pass
        
    def move(self, action):
        pass
        
    def get_next_action(self, world_state_martix):
        pass

    def get_movable_area(self, world_state_martix):
        pass