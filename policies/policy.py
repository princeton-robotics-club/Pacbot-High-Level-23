import numpy as np
from simulator.game_engine.grid import grid
from simulator.game_engine.variables import *


class Policy:
    def __init__(self, debug=True) -> None:
        # o = normal pellet, e = empty space, O = power pellet, c = cherry position
        # I = wall, n = ghost chambers
        self.WALLS = np.logical_or(np.array(grid) == I, np.array(grid) == n, dtype=bool)
        self.ACTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        self.debug = debug

    # state is a dict with keys:
    #    pellets:       height x width
    #    power_pellets: height x width
    #    pac:           (row, col)
    #    r:             (row, col)
    #    b:             (row, col)
    #    o:             (row, col)
    #    p:             (row, col)
    #    rf:            bool
    #    bf:            bool
    #    of:            bool
    #    pf:            bool
    #    dt:            distance threshold (in cells)
    def get_action(self, state):
        raise NotImplementedError()

    def dPrint(self, message):
        if self.debug:
            print(message)

    def reset(self):
        pass

    def get_state(self, env, obs):
        # relic of the past - would fill 2D grid with T/F values where pellets were/weren't
        # pellets = np.zeros((env.GRID_HEIGHT, env.GRID_WIDTH))
        # power_pellets = np.zeros((env.GRID_HEIGHT, env.GRID_WIDTH))
        # pellet_exists = obs[np.array(env.STATE_VALUES) == "pellet"]
        # for i in range(len(pellet_exists)):
        #     if pellet_exists[i]:
        #         pellets[env.PELLET_LOCATIONS == i + 1] = 1
        # power_pellet_exists = obs[np.array(env.STATE_VALUES) == "power_pellet"]
        # for i in range(len(power_pellet_exists)):
        #     if power_pellet_exists[i]:
        #         power_pellets[env.POWER_PELLET_LOCATIONS == i + 1] = 1
        return {
            "pellets": np.argwhere(np.array(env.game_state.grid) == o),
            "power_pellets": np.argwhere(np.array(env.game_state.grid) == O),
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
            "dt": obs[
                env.STATE_VALUES.index("frightened_timer")
            ],  # number of scared moves left
            "orientation": obs[env.STATE_VALUES.index("orientation")],
        }
