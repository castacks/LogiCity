import os
import argparse
import pickle as pkl
from utils.load import CityLoader
from utils.logger import setup_logger
from utils.vis import visualize_city
from core.config import *
import torch
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(description='Logic-based city simulation.')

    # Add arguments for grid size, agent start and goal positions, etc.
    parser.add_argument('--map', type=str, default="config/maps/v1.1.yaml", help='YAML path to the map.')
    parser.add_argument('--agents', type=str, default="config/agents/v0.yaml", help='YAML path to the agent definition.')
    parser.add_argument('--rule_type', type=str, default="LNN", help='We support ["LNN"].')
    parser.add_argument('--rules', type=str, default="config/rules/LNN/medium/medium_rule.yaml", help='YAML path to the rule definition.')
    # logger
    parser.add_argument('--log_dir', type=str, default="./log")
    parser.add_argument('--exp', type=str, default="train_10k")
    parser.add_argument('--vis', type=bool, default=False, help='Visualize the city.')
    parser.add_argument('--max-steps', type=int, default=100000, help='Maximum number of steps for the simulation.')
    parser.add_argument('--seed', type=int, default=18, help='random seed to use.')
    parser.add_argument('--debug', type=bool, default=False, help='In debug mode, the agents are in defined positions.')

    return parser.parse_args()

def main(args, logger):
    logger.info("Starting city simulation with random seed {}... Debug mode: {}".format(args.seed, args.debug))
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    # Create a city instance with a predefined grid
    city, cached_observation = CityLoader.from_yaml(args.map, args.agents, args.rules, args.rule_type, args.debug)
    visualize_city(city, 4*WORLD_SIZE, -1, "vis/init.png")

    # Main simulation loop
    steps = 0
    while steps < args.max_steps:
        logger.info("Simulating Step_{}...".format(steps))
        time_obs = city.update()
        # Visualize the current state of the city (optional)
        if args.vis:
            visualize_city(city, 4*WORLD_SIZE, -1, "vis/step_{}.png".format(steps))
        steps += 1
        cached_observation["Time_Obs"][steps] = time_obs

    # Save the cached observation for better rendering
    with open(os.path.join(args.log_dir, "{}.pkl".format(args.exp)), "wb") as f:
        pkl.dump(cached_observation, f)

if __name__ == '__main__':
    args = parse_arguments()
    logger = setup_logger(log_dir=args.log_dir, log_name=args.exp)
    main(args, logger)
