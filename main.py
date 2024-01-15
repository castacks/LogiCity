import os
import sys
import yaml
import argparse
import pickle as pkl
from logicity.utils.load import CityLoader
from logicity.utils.logger import setup_logger
from logicity.utils.vis import visualize_city
from logicity.core.config import *
import torch
import torch.nn as nn
import time
import numpy as np
# RL
from logicity.utils.gym_wrapper import GymCityWrapper
from stable_baselines3.common.vec_env import SubprocVecEnv, VecEnv
from logicity.rl_agent.neural import PPO, NeuralNav
from logicity.utils.gym_callback import EvalCheckpointCallback
from stable_baselines3.common.callbacks import CheckpointCallback
from tqdm import trange

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Logic-based city simulation.')

    # Add arguments for grid size, agent start and goal positions, etc.
    parser.add_argument('--map', type=str, default="config/maps/v1.1.yaml", help='YAML path to the map.')
    parser.add_argument('--agents', type=str, default="config/agents/debug.yaml", help='YAML path to the agent definition.')
    parser.add_argument('--rule_type', type=str, default="Z3_Local", help='We support ["LNN", "Z3_Global", "Z3_Local"].')
    parser.add_argument('--rules', type=str, default="config/rules/Z3/easy/easy_rule_local.yaml", help='YAML path to the rule definition.')
    # logger
    parser.add_argument('--log_dir', type=str, default="./log_rl")
    parser.add_argument('--exp', type=str, default="rl_debug")
    parser.add_argument('--vis', type=bool, default=False, help='Visualize the city.')
    parser.add_argument('--max-steps', type=int, default=1000, help='Maximum number of steps for the simulation.')
    parser.add_argument('--seed', type=int, default=1, help='random seed to use.')
    parser.add_argument('--debug', type=bool, default=False, help='In debug mode, the agents are in defined positions.')
    # RL
    parser.add_argument('--use_gym', type=bool, default=True, help='In gym mode, we can use RL alg. to control certain agents.')
    parser.add_argument('--rl_config', default='config/tasks/Nav/RL/config.yaml', help='Configure file for this RL exp.')

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
        s = time.time()
        time_obs = city.update()
        e = time.time()
        logger.info("Time spent: {}".format(e-s))
        # Visualize the current state of the city (optional)
        if args.vis:
            visualize_city(city, 4*WORLD_SIZE, -1, "vis/step_{}.png".format(steps))
        steps += 1
        cached_observation["Time_Obs"][steps] = time_obs

    # Save the cached observation for better rendering
    with open(os.path.join(args.log_dir, "{}.pkl".format(args.exp)), "wb") as f:
        pkl.dump(cached_observation, f)


def main_gym(args, logger): 
    def make_envs(simulation_config): 
        # Unpack arguments from simulation_config and pass them to CityLoader
        city, cached_observation = CityLoader.from_yaml(**simulation_config)
        env = GymCityWrapper(city)
        return env
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    config = load_config(args.rl_config)
    # simulation config
    simulation_config = config["simulation"]
    logger.info("Simulation config: {}".format(simulation_config))
    # RL config
    stable_baselines_config = config['stable_baselines']
    policy_kwargs = stable_baselines_config['policy_kwargs']
    train = stable_baselines_config["train"]
    
    # data rollouts
    if train: 
        # train_env = SubprocVecEnv([make_envs for i in range(1)])
        # debug
        train_env = make_envs(simulation_config)
        eval_env = make_envs(simulation_config)
        train_env.reset()
        model = PPO("MultiInputPolicy", train_env, policy_kwargs=policy_kwargs, verbose=1)
        # RL training mode
        # Create the custom checkpoint and evaluation callback
        eval_checkpoint_callback = EvalCheckpointCallback(
            eval_env=eval_env,
            eval_freq=2000,
            save_freq=2000,
            save_path='./checkpoints/{}'.format(args.exp),
            name_prefix='res18_model_50FOV',
            log_dir='./{}/{}'.format(args.log_dir, args.exp),
        )
        # Train the model
        model.learn(total_timesteps=1000, callback=eval_checkpoint_callback)
        # Save the model
        model.save("res18_model_50FOV")
        return
    
    # Checkpoint evaluation
    rew_list = []
    for ts in range(1, 11): 
        city, cached_observation = CityLoader.from_yaml(args.map, args.agents, args.rules, args.rule_type, True, args.debug)
        env = GymCityWrapper(city)
        model = PPO.load(args.checkpoint, env=env)
        o = env.reset()
        action = model.predict(o)[0]
        sys.stdout = open(os.devnull, 'w')
        ep_rew_list = []
        rew = 0        
        ep_rew = 0
        for steps in trange(500):
            o, r, d, i = env.step(action)
            action = model.predict(o)[0]
            ep_rew_list.append(r)
            rew += r
            cached_observation["Time_Obs"][steps] = i
            if d:
                print(ep_rew_list)
                np.save("log/rew_{}_{}.npy".format(args.exp, ts), np.array(ep_rew_list))
                # np.save('rew.npy', np.array(ep_rew_list))
                break
                # o = env.reset()
                # action = model.predict(o)[0]
        rew_list.append(rew)
        sys.stdout = sys.__stdout__   
        with open(os.path.join(args.log_dir, "{}_{}.pkl".format(args.exp, ts)), "wb") as f:
            pkl.dump(cached_observation, f)
        print(rew_list)

if __name__ == '__main__':
    args = parse_arguments()
    logger = setup_logger(log_dir=args.log_dir, log_name=args.exp)
    if args.use_gym:
        logger.info("Running in RL mode.")
        assert args.rl_config is not None, "Please specify a config file for RL."
        logger.info("Loading RL config from {}.".format(args.rl_config))
        # RL mode, will use gym wrapper to learn and test an agent
        main_gym(args, logger)
    else:
        # Sim mode, will use the logic-based simulator to run a simulation (no learning)
        logger.info("Running in simulation mode.")
        main(args, logger)