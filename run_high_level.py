import numpy as np
from simulator.gym_wrappers import PacBotEnv
from simulator.visualizer import Visualizer
from policies.high_level_policy import HighLevelPolicy
import time
import pygame
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s", help="Turn on slow mode", action="store_true")
    args = parser.parse_args()

    visualizer = Visualizer()
    env = PacBotEnv(speed=0.8)
    obs = env.reset()
    grid = env.render()
    visualizer.draw_grid(grid, env.orientation)
    policy = HighLevelPolicy()

    done = False
    key = 0
    trials = 0
    total_score = 0
    while key != pygame.K_q:
        state = policy.get_state(env, obs)
        pre = time.time()
        action = policy.get_action(state)
        print(f"CALC TIME: {time.time() - pre}")
        obs, reward, done, _ = env.step(action)
        grid = env.render()
        visualizer.draw_grid(grid, env.orientation)

        if done:
            trials += 1
            total_score += env.running_score
            obs = env.reset()
            env.render()
        key = visualizer.wait_ai_control()
        if args.s:
            time.sleep(0.1)
    print(f"Average score per run: {total_score / trials}")
    print(f"Number of trials: {trials}")
