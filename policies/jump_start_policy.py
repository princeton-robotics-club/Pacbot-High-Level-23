from policies.policy import Policy
from policies.high_level_policy import HighLevelPolicy, GhostPredict

from constants import *


class JumpStartPolicy(Policy):
    def __init__(self, debug=True) -> None:
        super().__init__(debug)

        self.last_pos = (14, 7)

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
        self.ghost_tracker = GhostPredict(False, debug)
        self.alt_policy = HighLevelPolicy(debug=debug, ghost_tracker=self.ghost_tracker)

    def reset(self):
        self.curr_action = 0
        self.still_on_start = True


    def should_move_on(self, state):

        x, y  = state["pac"]
        if self.start_path[self.curr_action]== UP and self.last_pos[0] == x - 1 and self.last_pos[1] == y:
            return True
        elif self.start_path[self.curr_action] == LEFT and self.last_pos[0] == x and self.last_pos[1] == y - 1:
            return True
        elif self.start_path[self.curr_action] == RIGHT and self.last_pos[0] == x and self.last_pos[1] == y + 1:
            return True
        elif self.start_path[self.curr_action] == DOWN and self.last_pos[0] == x + 1 and self.last_pos[1] == y:
            return True
        return False


    def get_action(self, state):
        if self.still_on_start:
            self.ghost_tracker.step()
            action = self.start_path[self.curr_action]
            self.ghost_tracker.prev_move = action
            self.curr_action += 1
            if self.curr_action == len(self.start_path):
                self.still_on_start = False
            return action
        return self.alt_policy.get_action(state)
