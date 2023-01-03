import torch
import numpy as np
from grid import grid
from variables import I, n


def load_nnet(filepath: str, nnet, optimizer=None):
    checkpoint = torch.load(filepath)
    nnet.load_state_dict(checkpoint["model_state_dict"])
    if optimizer:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    print(checkpoint.keys())


actions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
max_row = len(grid)
max_col = len(grid[0])


def generate_mask(state):
    pac_x = state[0]
    pac_y = state[1]
    orientation = state[2] % 2
    mask = np.ones(9, dtype=np.int64)
    mask[-1 * orientation + 1] = 0
    mask[-1 * orientation + 3] = 0
    mask[orientation + 4] = 0
    mask[orientation + 6] = 0
    for index, action in enumerate(actions):
        new_x = pac_x + action[0]
        new_y = pac_y + action[1]
        if (
            new_x < 0
            or new_x >= max_row
            or new_y < 0
            or new_y >= max_col
            or grid[new_x][new_y] in (I, n)
        ):
            if orientation == index % 2:
                mask[index] = 0
            else:
                mask[index + 4] = 0
    return mask
