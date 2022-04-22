import numpy as np
import copy
from .game_engine.grid import grid
from .gym_wrappers import PacBotEnv

# intended for A-star
# usage:
#    node = PacBotNode(target, speed) # where target is (pac_x, pac_y)
# useful attributes:
#    node.val               # value of node to use with A-star (a function of target)
#    node.is_target         # boolean indicating whether the node is the target node
#    node.sensible_actions  # list of actions which are sensible
#    node.next_node(action) # returns child node
#    node.render()      # returns grid which can be used with Visualizer
class PacBotNode():
    def _set_val(self):
        self.val = self._target_dists[pac_x, pac_y]

    def _set_is_target(self):
        pac_x, pac_y = self._env.game_state.pacbot.pos
        self.is_target = (self._target == np.array(self._env.game_state.pacbot.pos)).all()

    def _set_sensible_actions(self):
        pac_x, pac_y = self._env.game_state.pacbot.pos
        self.sensible_actions = []
        for i in range(self._env.NUM_ACTIONS):
            if i == self._env.UP:
                if not self._env.BAD_LOCATIONS[pac_x - 1, pac_y]:
                    self.sensible_actions.append(i)
            elif i == self._env.LEFT:
                if not self._env.BAD_LOCATIONS[pac_x, pac_y - 1]:
                    self.sensible_actions.append(i)
            elif i == self._env.STAY:
                if not self._env.BAD_LOCATIONS[pac_x, pac_y]:
                    self.sensible_actions.append(i)
            elif i == self._env.RIGHT:
                if not self._env.BAD_LOCATIONS[pac_x, pac_y + 1]:
                    self.sensible_actions.append(i)
            elif i == self._env.DOWN:
                if not self._env.BAD_LOCATIONS[pac_x + 1, pac_y]:
                    self.sensible_actions.append(i)

    def __init__(self, target, speed=1):
        # assign tree-common attributes
        self._target_dists = np.fill(float("inf"), np.array(grid).shape)

        # assign internal attributes
        self._env = PacBotEnv(speed=speed)
        self._env.reset()
        assert target[0] >= 0 and target[0] < self._env.GRID_HEIGHT and target[1] >= 0 and target[1] < self._env.GRID_WIDTH, "target must be (row, col)"
        self._target = target
        self._direction = self._env.UP
        self._prev_action = self._env.STAY

        # assign public attributes
        self._set_val()
        self._set_is_target()
        self._set_sensible_actions()
        
        
        assign_sensible_actions(self)

    def next_node(self, action):
        child = copy.deepcopy(self)
        if action != self._direction and action != self._env.STAY:
            child._direction = action
            action = self._env.STAY    
        child.obs, _, child.done, _ = child._env.step(action)
        child._prev_action = action
        if action != self._env.STAY:
            child._direction = action
        child.val = evaluate(child)
        child.depth += 1
        assign_sensible_actions(child)
        return child

    def render(self):
        return self._env.render()