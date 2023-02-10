from analysis import Analysis
from simulator.gym_wrappers import PacBotEnv
from simulator.visualizer import Visualizer
from policies.high_level_policy import HighLevelPolicy
import time
import pygame
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s", help="Turn on slow mode", action="store_true")
    parser.add_argument("--o", help="Output file name", type=str)
    parser.add_argument("--t", help="Number of trials", type=int, default=5)
    args = parser.parse_args()

    visualizer = Visualizer()
    env = PacBotEnv(speed=0.8)
    obs = env.reset()
    grid = env.render()
    visualizer.draw_grid(grid, env.orientation)
    policy = HighLevelPolicy()
    analysis = Analysis(args.o)

    done = False
    key = 0
    trials = 0

    while key != pygame.K_q and trials < args.t:
        state = policy.get_state(env, obs)
        pre = time.time()
        action = policy.get_action(state)
        analysis.log_calc(time.time() - pre)
        obs, reward, done, _ = env.step(action)
        grid = env.render()
        visualizer.draw_grid(grid, env.orientation)

        if done:
            analysis.log_endgame(env)
            trials += 1
            policy.reset()
            obs = env.reset()
            env.render()
        key = visualizer.wait_ai_control()
        if args.s:
            time.sleep(0.1)
    analysis.write()
