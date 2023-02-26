import torch
import numpy as np
from .grid import grid
from .variables import I, n


def load_nnet(filepath: str, nnet, optimizer=None):
    checkpoint = torch.load(filepath)
    nnet.load_state_dict(checkpoint["model_state_dict"])
    if optimizer:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    print(checkpoint.keys())


actions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
max_row = len(grid)
max_col = len(grid[0])
