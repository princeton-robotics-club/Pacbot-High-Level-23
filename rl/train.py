from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from simulator.gym_wrappers import PacBotEnv

import sys

if __name__ == "__main__":
    assert len(sys.argv) == 2, "must supply algorithm argument (either DQN or PPO)"

    SPEED = 1
    NUM_ENVS = 16
    ALGORITHM = sys.argv[1]
    assert ALGORITHM in ["DQN", "PPO"], "ALGORITHM must be either DQN or PPO"
    TOTAL_TIMESTEPS = 10000000
    STEPS_PER_CHECKPOINT = max(100000 // NUM_ENVS, 1)
    FINAL_MODEL_NAME = ALGORITHM + "_final_model"

    env = PacBotEnv(speed=SPEED)
    envs = make_vec_env(lambda: env, n_envs=NUM_ENVS)  # vectorized env

    try:
        if ALGORITHM == "DQN":
            model = DQN.load(FINAL_MODEL_NAME, envs)
        elif ALGORITHM == "PPO":
            model = PPO.load(FINAL_MODEL_NAME, envs)
    except Exception as e:
        print(str(e))
        print("learning from scratch")
        if ALGORITHM == "DQN":
            model = DQN("MlpPolicy", envs, verbose=0, tensorboard_log="logs")
        elif ALGORITHM == "PPO":
            model = PPO("MlpPolicy", envs, verbose=0, tensorboard_log="logs")

    checkpoint_callback = CheckpointCallback(
        save_freq=STEPS_PER_CHECKPOINT, save_path="checkpoints", name_prefix="mlp"
    )

    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=checkpoint_callback)
    model.save(FINAL_MODEL_NAME)
