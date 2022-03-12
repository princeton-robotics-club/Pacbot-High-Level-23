from .gym_wrappers import PacBotEnv
import copy

class PacBotNode():
    def __init__(self, speed=1):
        self.env = PacBotEnv(speed=speed)
        self.obs = self.env.reset()
        self.done = False

    def next_node(self, action):
        child = copy.deepcopy(self)
        child.obs, _, child.done, _ = child.env.step(action)
        return child