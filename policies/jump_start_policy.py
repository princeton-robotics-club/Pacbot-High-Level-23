from policies.policy import Policy
from policies.high_level_policy import HighLevelPolicy

from constants import *


class JumpStartPolicy(Policy):
    def __init__(self, debug=True) -> None:
        super().__init__(debug)

        self.start_path = [
            UP,
            UP,
            UP,
            UP,
            UP,
            UP,
            UP,
            UP,
            FACE_LEFT,
            LEFT,
            LEFT,
            LEFT,
            FACE_UP,
            UP,
            UP,
            UP,
            UP,
            UP,
            FACE_LEFT,
            LEFT,
            LEFT,
            LEFT,
            FACE_DOWN,
        ]
        for _ in range(25):
            self.start_path.append(DOWN)
        self.curr_action = 0
        self.still_on_start = True
        self.alt_policy = HighLevelPolicy(debug=debug)

    def reset(self):
        self.curr_action = 0
        self.still_on_start = True

    def get_action(self, state):
        if self.still_on_start:
            action = self.start_path[self.curr_action]
            self.curr_action += 1
            if self.curr_action == len(self.start_path):
                self.still_on_start = False
            return action
        return self.alt_policy.get_action(state)
