from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from gym_simulator.gym_wrapper import PacBotEnv

import time

def print_state(state):
    grid = PacBotEnv.get_grid_from_state(state)
    for row in grid:
        for cell in row:
            print(cell, end='')
        print()

if __name__ == "__main__":
    env = PacBotEnv(speed=1)
    # wrap env
    env = make_vec_env(lambda: env, n_envs=4)

    model = PPO('MlpPolicy', env, verbose=0)
    model.learn(total_timesteps=10)

    # model.save("model")
    # model = PPO.load("model")

    # testing
    obs = env.reset()
    print_state(obs[0])
    print()
    while True:
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        print_state(obs[0])
        print()
        time.sleep(1)