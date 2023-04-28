from algorithms.dijkstra import dijkstra
from algorithms.opt_astar import astar
from policies.policy import Policy
from constants import STAY

import numpy as np
from random import choice


class DijkstraPolicy(Policy):
    def __init__(self, debug=True) -> None:
        super().__init__(debug)
        self.curr_target = None

    def get_action(self, state):
        obstacles = self.WALLS.copy()
        # consider ghosts which are not frightened to be obstacles
        if not state["rf"]:
            obstacles[state["r"]] = True
        if not state["bf"]:
            obstacles[state["b"]] = True
        if not state["of"]:
            obstacles[state["o"]] = True
        if not state["pf"]:
            obstacles[state["p"]] = True

        positions = state["pellets"].union(state["power_pellets"]) #np.concatenate((list(state["pellets"]), list(state["power_pellets"])))

        # coords = [tuple(coord) for coord in positions.tolist()]
        # state["pellets"] = set(coords)
        # coords = list(state["pellets"])

        if self.curr_target not in positions:
            closest_path = dijkstra(obstacles, state["pac"], state, 20)
            if closest_path:
                return self.get_action_from_path(closest_path)
            self.dPrint("dijkstra returned")
            if len(positions) > 0:
                # print(coords)
                self.curr_target = choice(positions)
            else:
                self.dPrint("no coords")
                return STAY, 0
        self.dPrint(self.curr_target)
        path = astar(obstacles, state["pac"], self.curr_target, state)
        return self.get_action_from_path(path)
