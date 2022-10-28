import numpy as np
from simulator.game_engine.grid import grid
from simulator.game_engine.variables import *


class Policy:
    def __init__(self) -> None:
        # o = normal pellet, e = empty space, O = power pellet, c = cherry position
        # I = wall, n = ghost chambers
        self.WALLS = np.logical_or(np.array(grid) == I, np.array(grid) == n, dtype=bool)
        self.ACTIONS = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)]

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
