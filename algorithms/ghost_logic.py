from constants import UP, DOWN, LEFT, RIGHT
from simulator.game_engine.grid import grid
from simulator.game_engine.variables import I, n
import math
from .ghostpaths import *


def get_next_blue_chase_move(
    pacbot_dir, pacbot_pos, red_pos, curr_pos, next_pos, scatter_pos
):
    pacbot_target = (0, 0)
    if pacbot_dir == RIGHT:
        pacbot_target = (
            pacbot_pos[0] - 2,
            pacbot_pos[1] + 2,
        )
    elif pacbot_dir == LEFT:
        pacbot_target = (
            pacbot_pos[0],
            pacbot_pos[1] - 2,
        )
    elif pacbot_dir == UP:
        pacbot_target = (
            pacbot_pos[0] - 2,
            pacbot_pos[1],
        )
    elif pacbot_dir == DOWN:
        pacbot_target = (
            pacbot_pos[0] + 2,
            pacbot_pos[1],
        )
    x = pacbot_target[0] + (pacbot_target[0] - red_pos[0])
    y = pacbot_target[1] + (pacbot_target[1] - red_pos[1])

    return get_move_based_on_target((x, y), curr_pos, next_pos)


def get_next_pink_chase_move(
    pacbot_dir, pacbot_pos, red_pos, curr_pos, next_pos, scatter_pos
):
    (x, y) = (0, 0)

    if pacbot_dir == RIGHT:
        x = pacbot_pos[0] - 4
        y = pacbot_pos[1] + 4
    elif pacbot_dir == LEFT:
        x = pacbot_pos[0]
        y = pacbot_pos[1] - 4
    elif pacbot_dir == UP:
        x = pacbot_pos[0] - 4
        y = pacbot_pos[1]
    elif pacbot_dir == DOWN:
        x = pacbot_pos[0] + 4
        y = pacbot_pos[1]

    return get_move_based_on_target((x, y), curr_pos, next_pos)


def get_next_red_chase_move(
    pacbot_dir, pacbot_pos, red_pos, curr_pos, next_pos, scatter_pos
):
    return get_move_based_on_target(pacbot_pos, curr_pos, next_pos)


def get_next_orange_chase_move(
    pacbot_dir, pacbot_pos, red_pos, curr_pos, next_pos, scatter_pos
):
    if get_euclidian_distance(curr_pos, pacbot_pos) < 8:
        return get_next_scatter_move(scatter_pos, curr_pos, next_pos)
    return get_move_based_on_target(pacbot_pos, curr_pos, next_pos)


def get_next_scatter_move(scatter_pos, curr_pos, next_pos):
    return get_move_based_on_target(scatter_pos, curr_pos, next_pos)


def get_euclidian_distance(pos_a, pos_b):
    return math.hypot(int(pos_a[0]) - int(pos_b[0]), int(pos_a[1]) - int(pos_b[1]))


# not exactly how the game engine works
# will need to keep track of previous position to make this work
def is_move_legal(position, curr_pos):
    return position != curr_pos and grid[position[0]][position[1]] not in (
        I,
        n,
    )


ghost_no_up_tiles = set(((12, 19), (15, 19), (12, 7), (15, 7)))

# same comment as is_move_legal
def find_possible_moves(curr_pos, next_pos):
    x, y = next_pos
    possible = []
    if is_move_legal((x + 1, y), curr_pos):
        possible.append((x + 1, y))
    if is_move_legal((x, y + 1), curr_pos) and (x, y) not in ghost_no_up_tiles:
        possible.append((x, y + 1))
    if is_move_legal((x - 1, y), curr_pos):
        possible.append((x - 1, y))
    if is_move_legal((x, y - 1), curr_pos):
        possible.append((x, y - 1))
    if possible == []:
        possible.append(curr_pos)
    return possible


def get_move_based_on_target(target, curr_pos, next_pos):
    possible = find_possible_moves(curr_pos, next_pos)
    distances = [get_euclidian_distance(target, tile) for tile in possible]
    # possibly change this
    (min_distance, index) = min(
        (min_distance, index) for (index, min_distance) in enumerate(distances)
    )

    return possible[index]


ghost_funcs = {
    "r": get_next_red_chase_move,
    "b": get_next_blue_chase_move,
    "o": get_next_orange_chase_move,
    "p": get_next_pink_chase_move,
}

scatter_positions = {"r": (25, 32), "b": (27, -1), "o": (0, -1), "p": (2, 32)}

edited_respawn_path = [
    (12, 17),
    (12, 16),
    (12, 15),
    (13, 15),
    (13, 16),
    (13, 17),
    (13, 18),
    (13, 19),
]

ghost_init_dict = {
    "r": {
        "chase_func": get_next_red_chase_move,
        "scatter_pos": (25, 32),
        "init_pos": red_init_pos,
        "init_npos": red_init_npos,
        "start_path": [],
    },
    "b": {
        "chase_func": get_next_blue_chase_move,
        "scatter_pos": (27, -1),
        "init_pos": blue_init_pos,
        "init_npos": blue_init_npos,
        "start_path": blue_start_path,
    },
    "o": {
        "chase_func": get_next_orange_chase_move,
        "scatter_pos": (0, -1),
        "init_pos": orange_init_pos,
        "init_npos": orange_init_npos,
        "start_path": orange_start_path,
    },
    "p": {
        "chase_func": get_next_pink_chase_move,
        "scatter_pos": (2, 32),
        "init_pos": pink_init_pos,
        "init_npos": pink_init_npos,
        "start_path": pink_start_path,
    },
}
