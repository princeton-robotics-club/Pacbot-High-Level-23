import numpy as np
from simulator.game_engine.grid import grid
from simulator.game_engine.variables import *
from constants import STAY


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

    def get_state(self, env, obs, done, extra):
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
            "life_lost": extra["life_lost"] or done,
        }

    def get_action_from_path(self, path, power_pellet=None, chase=False):
        if len(path) < 2:
            return STAY, 0
        shortened_path = [path[i].position for i in range(min(3, len(path)))]
        movement = tuple(np.subtract(shortened_path[1], shortened_path[0]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                self.ghost_tracker.prev_move = index
                move_dist = 1
                for i in range(2, len(path)):
                    if (
                        tuple(np.subtract(path[i].position, path[i - 1].position))
                        == action
                    ):
                        if path[i].position == power_pellet:
                            break
                        move_dist += 1
                        if chase and path[i] == path[-1]:
                            move_dist += 3
                    else:
                        # Makes pacbot not stop at intersection
                        # does not account for cases where the destination is the intersection
                        if move_dist > 1:
                            move_dist -= 1
                        break
                return (index, move_dist)
        # assume that a turn happened
        if len(path) < 3:
            return (STAY, 0)
        movement = tuple(np.subtract(shortened_path[2], shortened_path[1]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                move_dist = 1
                for i in range(3, len(path)):
                    if (
                        tuple(np.subtract(path[i].position, path[i - 1].position))
                        == action
                    ):
                        move_dist += 1
                    else:
                        if move_dist > 1:
                            move_dist -= 1
                        break
                return (index, move_dist)
        self.dPrint("ERROR: DOUBLE TURN")
        return (STAY, 0)
