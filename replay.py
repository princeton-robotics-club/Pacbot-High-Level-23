from simulator.visualizer import Visualizer
from simulator.gym_wrappers import PacBotEnv
import os
import numpy as np
from pygame import K_q, K_RIGHT, K_LEFT, K_SPACE, K_1, K_2, K_3


def draw_replay(filepath):
    moves = []
    info_dict = {}
    with open(filepath, "r") as f:
        lines = f.readlines()
        score = lines[0].rstrip()
        ticks = lines[1].rstrip()
        pellets_remaining = lines[2].rstrip()
        info_dict["score"] = score
        info_dict["ticks"] = ticks
        info_dict["pellets"] = pellets_remaining
        lines = lines[3:]
        while lines:
            coords_line = lines[0].rstrip().split()
            pellets_line = lines[1].rstrip().split()
            power_pellets_line = lines[2].rstrip().split()
            moves.append([coords_line, pellets_line, power_pellets_line])
            lines = lines[3:]
    return moves, info_dict


visualizer = Visualizer()
moves, info_dict = draw_replay(os.path.join("replay", "replay.txt"))

base_grid = np.zeros((PacBotEnv.GRID_HEIGHT, PacBotEnv.GRID_WIDTH), dtype=str)
base_grid[PacBotEnv.WALL_LOCATIONS != 0] = "#"


grids = []

ghosts = ["r", "b", "o", "p"]

death_checkpoints = []

for positions, pellets, power_pellets in moves:
    grid = np.copy(base_grid)
    for i in range(0, len(pellets), 2):
        grid[int(pellets[i]), int(pellets[i + 1])] = "-"
    for i in range(0, len(power_pellets), 2):
        grid[int(power_pellets[i]), int(power_pellets[i + 1])] = "%"
    grid[int(positions[0]), int(positions[1])] = "a"
    for index, ghost in enumerate(ghosts):
        index += 1
        grid[int(positions[index * 2]), int(positions[index * 2 + 1])] = (
            "f" if bool(float(positions[index + 10])) else ghost
        )
    orientation = int(float(positions[10]))
    just_died = bool(float(positions[-3]))
    state = int(positions[-2])
    lives = int(positions[-1])
    if just_died:
        death_checkpoints.append(len(grids) - 1)
    grids.append((grid, orientation, state, lives))

key = 0
current_frame = 0


def clamp(frame_count):
    if frame_count < 0:
        frame_count = 0
    elif frame_count >= len(grids):
        frame_count = len(grids) - 1
    return frame_count


while key != K_q:
    grid, orientation, game_state, lives = grids[current_frame]
    visualizer.draw_grid(grid, orientation, game_state, lives)
    key = visualizer.wait_manual_control()
    if key == K_SPACE:
        current_frame += 5
    elif key == K_RIGHT:
        current_frame += 1
    elif key == K_LEFT:
        current_frame -= 1
    elif key == K_1:
        current_frame = death_checkpoints[0]
    elif key == K_2:
        current_frame = death_checkpoints[1]
    elif key == K_3:
        current_frame = len(grids) - 1
    current_frame = clamp(current_frame)
