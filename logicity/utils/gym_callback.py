from stable_baselines3.common.callbacks import CheckpointCallback
import numpy as np
import os
import logging
logger = logging.getLogger(__name__)

class EvalCheckpointCallback(CheckpointCallback):
    def __init__(self, eval_env, eval_freq=50000, log_dir='./log/', *args, **kwargs):
        super(EvalCheckpointCallback, self).__init__(*args, **kwargs)
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.best_mean_reward = -np.inf

    def on_step(self) -> bool:
        super().on_step()  # Continue with normal checkpointing

        # Perform evaluation at specified intervals
        if self.n_calls % self.eval_freq == 0:
            rewards_list = []
            for episode in range(20):  # Number of episodes for evaluation
                obs = self.eval_env.reset()
                episode_rewards = 0
                done = False
                while not done:
                    action, _states = self.model.predict(obs, deterministic=True)
                    obs, reward, done, _info = self.eval_env.step(action)
                    episode_rewards += reward
                rewards_list.append(episode_rewards)

            mean_reward = np.mean(rewards_list)
            logger.info(f"Step: {self.n_calls} - Mean Reward: {mean_reward}")

            # Log the mean reward
            with open(os.path.join(self.log_dir, "eval_rewards.txt"), "a") as file:
                file.write(f"Step: {self.n_calls} - Mean Reward: {mean_reward}\n")

            # Update the best model if current mean reward is better
            if mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                self.model.save("{}/best_model.zip".format(self.log_dir))

        return True
