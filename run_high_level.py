from analysis import Analysis
from simulator.gym_wrappers import PacBotEnv
from simulator.visualizer import Visualizer
from simulator.game_engine.variables import up, down, left
from constants import UP, DOWN, LEFT, RIGHT
from policies.high_level_policy import HighLevelPolicy
import time
import pygame
import argparse


def convert_direction(direction):
    if direction == up:
        return RIGHT
    if direction == down:
        return LEFT
    if direction == left:
        return UP
    return DOWN


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s", help="Turn on slow mode", action="store_true")
    parser.add_argument("--o", help="Output file name", type=str)
    parser.add_argument("--t", help="Number of trials", type=int, default=5)
    parser.add_argument("--d", help="Toggle debug", action="store_false")
    args = parser.parse_args()

    visualizer = Visualizer()
    env = PacBotEnv(speed=0.8)
    obs = env.reset()
    grid = env.render()
    visualizer.draw_grid(grid, env.orientation)
    policy = HighLevelPolicy(debug=args.d)
    analysis = Analysis(args.o)

    done = False
    key = 0
    trials = 0
    extra = {"life_lost": False}
    done = False

    game_agents = [
        env.game_state.red,
        env.game_state.orange,
        env.game_state.pink,
        env.game_state.blue,
    ]

    while key != pygame.K_q and trials < args.t:
        state = policy.get_state(env, obs, done, extra)
        analysis.log_replay(env, state)
        pre = time.time()
        action = policy.get_action(state)
        analysis.log_calc(time.time() - pre)
        obs, reward, done, extra = env.step(action)
        grid = env.render()
        visualizer.draw_grid(grid, env.orientation)

        if done:
            analysis.log_endgame(env)
            trials += 1
            # if not env.game_state._are_all_pellets_eaten():
            analysis.write_replay(env)

            analysis.reset()
            policy.reset()
            obs = env.reset()
            env.render()
        key = visualizer.wait_ai_control()
        if args.s:
            time.sleep(0.1)
    analysis.write()
