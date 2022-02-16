from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from gym_simulator.gym_wrapper import PacBotEnv

if __name__ == "__main__":
    SPEED = 1
    NUM_ENVS = 16
    TOTAL_TIMESTEPS = 10000000
    STEPS_PER_CHECKPOINT = max(100000 // NUM_ENVS, 1)
    FINAL_MODEL_NAME = "final_model"

    env = PacBotEnv(speed=SPEED)
    envs = make_vec_env(lambda: env, n_envs=NUM_ENVS) # vectorized env

    try:
        model = PPO.load(FINAL_MODEL_NAME, envs)
    except Exception as e:
        print(str(e))
        print("learning from scratch")
        model = PPO('MlpPolicy', envs, verbose=0, tensorboard_log="logs")

    checkpoint_callback = CheckpointCallback(save_freq=STEPS_PER_CHECKPOINT, save_path="checkpoints", name_prefix="mlp")

    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=checkpoint_callback)
    model.save(FINAL_MODEL_NAME)