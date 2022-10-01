import numpy as np
from simulator.gym_wrappers import PacBotEnv
from simulator.visualizer import Visualizer
from policies.high_level_policy import HighLevelPolicy
import time
import pygame


def get_state(env: PacBotEnv, obs):
    pellets = np.zeros((env.GRID_HEIGHT, env.GRID_WIDTH))
    power_pellets = np.zeros((env.GRID_HEIGHT, env.GRID_WIDTH))
    pellet_exists = obs[np.array(env.STATE_VALUES) == "pellet"]
    for i in range(len(pellet_exists)):
        if pellet_exists[i]:
            pellets[env.PELLET_LOCATIONS == i + 1] = 1

    power_pellet_exists = obs[np.array(env.STATE_VALUES) == "power_pellet"]
    for i in range(len(power_pellet_exists)):
        if power_pellet_exists[i]:
            power_pellets[env.POWER_PELLET_LOCATIONS == i + 1] = 1
    return {
        "pellets": pellets,
        "power_pellets": power_pellets,
        "pac": (
            int(obs[env.STATE_VALUES.index("pac_x")]),
            int(obs[env.STATE_VALUES.index("pac_y")]),
        ),
        "r": (
            int(obs[env.STATE_VALUES.index("r_x")]),
            int(obs[env.STATE_VALUES.index("r_y")]),
        ),
        "b": (
            int(obs[env.STATE_VALUES.index("b_x")]),
            int(obs[env.STATE_VALUES.index("b_y")]),
        ),
        "o": (
            int(obs[env.STATE_VALUES.index("o_x")]),
            int(obs[env.STATE_VALUES.index("o_y")]),
        ),
        "p": (
            int(obs[env.STATE_VALUES.index("p_x")]),
            int(obs[env.STATE_VALUES.index("p_y")]),
        ),
        "rf": obs[env.STATE_VALUES.index("r_frightened")],
        "bf": obs[env.STATE_VALUES.index("b_frightened")],
        "of": obs[env.STATE_VALUES.index("o_frightened")],
        "pf": obs[env.STATE_VALUES.index("p_frightened")],
        "dt": obs[env.STATE_VALUES.index("frightened_timer")] / 2,
    }


if __name__ == "__main__":
    visualizer = Visualizer()
    env = PacBotEnv(speed=0.8)
    obs = env.reset()
    grid = env.render()
    visualizer.draw_grid(grid)
    policy = HighLevelPolicy()

    done = False
    key = 0

    while key != pygame.K_q:
        state = get_state(env, obs)
        action = policy.get_action(state)
        obs, reward, done, _ = env.step(action)
        grid = env.render()
        visualizer.draw_grid(grid)

        if done:
            env.reset()
            env.render()
        key = visualizer.wait_ai_control()
        time.sleep(0.1)
