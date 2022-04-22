from .gym_wrappers import PacBotEnv
from .game_engine.variables import *
import copy
import numpy as np
from .game_engine.grid import grid

def manhattan_dist(pos1, pos2):
    return np.abs((np.array(pos1) - np.array(pos2))).sum()

def evaluate(node):
    pellet_weight = 1
    power_weight = 10
    survival_weight = 100000

    env = node.env
    game_state = node.env.game_state

    pellet_score = -1*(np.array(game_state.grid)[env.PELLET_LOCATIONS != 0] == o).sum()
    power_score = -1*(np.array(game_state.grid)[env.POWER_PELLET_LOCATIONS != 0] == O).sum()

    pac_x, pac_y = game_state.pacbot.pos[0], game_state.pacbot.pos[1]
    # r_x, r_y, r_frightened = game_state.red.pos['current'][0], game_state.red.pos['current'][1], 1 if game_state.red.frightened_counter > 0 else 0
    # p_x, p_y, p_frightened = game_state.pink.pos['current'][0], game_state.pink.pos['current'][1], 1 if game_state.pink.frightened_counter > 0 else 0
    # o_x, o_y, o_frightened = game_state.orange.pos['current'][0], game_state.orange.pos['current'][1], 1 if game_state.orange.frightened_counter > 0 else 0
    # b_x, b_y, b_frightened = game_state.blue.pos['current'][0], game_state.blue.pos['current'][1], 1 if game_state.blue.frightened_counter > 0 else 0
    ghosts = [game_state.red, game_state.pink, game_state.orange, game_state.blue]
    ghosts = [ghost for ghost in ghosts if not ghost.frightened_counter > 0]
    survival_score = 0
    if ghosts:
        survival_score = -1*(np.min([manhattan_dist(game_state.pacbot.pos, ghost.pos['current']) for ghost in ghosts]) < 4)
    
    #survival_score = -1*(env.num_lives != node.prev_lives)
    #survival_score = 0
    return pellet_weight*pellet_score + power_weight*power_score + survival_weight*survival_score

def assign_sensible_actions(node):
    pac_x, pac_y = node.env.game_state.pacbot.pos
    node.sensible_actions = []
    for i in range(node.env.NUM_ACTIONS):
        if i == node.env.UP:
            if not node.env.BAD_LOCATIONS[pac_x - 1, pac_y]:
                node.sensible_actions.append(i)
        elif i == node.env.LEFT:
            if not node.env.BAD_LOCATIONS[pac_x, pac_y - 1]:
                node.sensible_actions.append(i)
        elif i == node.env.STAY:
            if not node.env.BAD_LOCATIONS[pac_x, pac_y]:
                node.sensible_actions.append(i)
        elif i == node.env.RIGHT:
            if not node.env.BAD_LOCATIONS[pac_x, pac_y + 1]:
                node.sensible_actions.append(i)
        elif i == node.env.DOWN:
            if not node.env.BAD_LOCATIONS[pac_x + 1, pac_y]:
                node.sensible_actions.append(i)


class PacBotNode():
    def __init__(self, speed=1):
        self.env = PacBotEnv(speed=speed)
        self.obs = self.env.reset()
        self.done = False
        self.direction = self.env.DOWN
        self.prev_action = self.env.STAY
        self.prev_lives = 3
        self.val = evaluate(self)
        self.depth = 0
        assign_sensible_actions(self)

    def next_node(self, action):
        child = copy.deepcopy(self)
        if action != self.direction and action != self.env.STAY:
            child.direction = action
            action = self.env.STAY    
        child.obs, _, child.done, _ = child.env.step(action)
        child.prev_action = action
        if action != self.env.STAY:
            child.direction = action
        child.prev_lives = self.env.num_lives
        child.val = evaluate(child)
        child.depth += 1
        assign_sensible_actions(child)
        return child

    def __lt__(self, other):
        return self.val < other.val