import time
import numpy as np
from gym_simulator.tree_wrappers import PacBotNode
from gym_simulator.variables import *

def evaluate(node):
    pellet_weight = 1
    power_weight = 1
    survival_weight = 1

    env = node.env
    game_state = node.env.game_state

    pellet_score = -1*(np.array(game_state.grid)[env.PELLET_LOCATIONS != 0] == o).sum()
    power_score = -1*(np.array(game_state.grid)[env.POWER_PELLET_LOCATIONS != 0] == O).sum()

    pac_x, pac_y = game_state.pacbot.pos[0], game_state.pacbot.pos[1]
    r_x, r_y, r_frightened = game_state.red.pos['current'][0], game_state.red.pos['current'][1], 1 if game_state.red.frightened_counter > 0 else 0
    p_x, p_y, p_frightened = game_state.pink.pos['current'][0], game_state.pink.pos['current'][1], 1 if game_state.pink.frightened_counter > 0 else 0
    o_x, o_y, o_frightened = game_state.orange.pos['current'][0], game_state.orange.pos['current'][1], 1 if game_state.orange.frightened_counter > 0 else 0
    b_x, b_y, b_frightened = game_state.blue.pos['current'][0], game_state.blue.pos['current'][1], 1 if game_state.blue.frightened_counter > 0 else 0
    survival_score = -1*(
        (pac_x == r_x and pac_y == r_y and not r_frightened) or 
        (pac_x == p_x and pac_y == p_y and not p_frightened) or 
        (pac_x == o_x and pac_y == o_y and not o_frightened) or 
        (pac_x == b_x and pac_y == b_y and not b_frightened)
    )

    return pellet_weight*pellet_score + power_weight*power_score + survival_weight*survival_score


if __name__ == "__main__":
    SPEED = 1

    node = PacBotNode(speed=SPEED)
    