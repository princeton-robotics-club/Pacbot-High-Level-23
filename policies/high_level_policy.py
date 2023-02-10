from typing import Callable
import numpy as np
from constants import STAY
from simulator.game_engine.variables import *
from algorithms.opt_astar import astar
from policies.policy import Policy


class HighLevelPolicy(Policy):
    NT = 3

    def __init__(self, heuristic: Callable = None) -> None:
        super().__init__()
        self.heuristic = heuristic

    # helper method to astar to a ghost, which is technically a barrier in maze
    def astar_ghost(self, maze, start, end, state=None):
        maze[end] = False
        path = astar(maze, start, end, state, self.heuristic)
        maze[end] = True
        return path

    def get_action_from_path(self, path):
        movement = tuple(np.subtract(path[1], path[0]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                return index
        # assume that a turn happened
        if len(path) < 3:
            return STAY
        movement = tuple(np.subtract(path[2], path[1]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                return index + 4
        print("ERROR: DOUBLE TURN")
        return STAY

    # state is a dict with keys:
    #    pellets:       height x width
    #    power_pellets: height x width
    #    pac:           (row, col)
    #    r:             (row, col)
    #    b:             (row, col)
    #    o:             (row, col)
    #    p:             (row, col)
    #    rf:            bool
    #    bf:            bool
    #    of:            bool
    #    pf:            bool
    #    dt:            distance threshold (in cells)
    #    orientation:   UP, LEFT, RIGHT, DOWN
    def get_action(self, state):

        obstacles = self.WALLS.copy()

        # stores non frightened ghost positions
        g_positions = []

        # stores frightened ghost positions
        f_positions = []

        # consider ghosts which are not frightened to be obstacles
        if state["rf"]:
            f_positions.append(state["r"])
        else:
            g_positions.append(state["r"])
            obstacles[state["r"]] = True
        if state["bf"]:
            f_positions.append(state["b"])
        else:
            g_positions.append(state["b"])
            obstacles[state["b"]] = True
        if state["of"]:
            f_positions.append(state["o"])
        else:
            g_positions.append(state["o"])
            obstacles[state["o"]] = True
        if state["pf"]:
            f_positions.append(state["p"])
        else:
            g_positions.append(state["p"])
            obstacles[state["p"]] = True

        print("phase: frightened ghosts")

        # target the closest frightened ghost not on pac
        # move to it if it exists and is within dt
        closest_d = None
        closest_path = None
        for f_position in f_positions:
            print("pathfinding to frightened ghost")
            path = self.astar_ghost(obstacles, state["pac"], f_position, state)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > len(path) - 1:
                closest_d = len(path) - 1
                closest_path = path
                if closest_d <= 1:
                    break

        # only chases frightened ghost if it's within certain distance
        if closest_d and closest_d <= state["dt"]:
            return self.get_action_from_path(closest_path)

        print("phase: power pellets")

        # target the closest power pellet not on pac
        # move to it, if it exists and (is further than 1 cell away or a ghost is within NT)
        # wait at it, if it exists and is within 1 cell and a ghost is not within NT cells
        nearby = False
        closest_ghost_dist = float("inf")
        for g_position in g_positions:
            if self.WALLS[g_position]:
                continue
            print("pathfinding to ghost")
            path = self.astar_ghost(obstacles, state["pac"], g_position, state)
            # TODO see if -2 is better since beginning and end node are included
            closest_ghost_dist = min(closest_ghost_dist, max(len(path) - 1, 0))
            if not path or len(path) - 1 <= self.NT:
                nearby = True
                # break
        print("nearby:", nearby)
        positions = np.argwhere(state["power_pellets"])
        closest_d = None
        closest_path = None
        for position in positions:
            print("pathfinding to power pellet")
            path = astar(obstacles, state["pac"], position, state, self.heuristic)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > len(path) - 1:
                closest_d = len(path) - 1
                closest_path = path
                if closest_d <= 1:
                    break
        if closest_d:
            # moves towards nearby power pellet
            # potential bug - still moves towards power pellet even if ghost is in path
            if closest_d > 1 or nearby:
                return self.get_action_from_path(closest_path)
            # waits until ghost approaches
            else:
                return STAY

        print("phase: pellets")
        # target the closest pellet not on pac
        # move to it if it exists
        positions = np.argwhere(state["pellets"])
        closest_d = None
        closest_path = None
        for position in positions:
            path = astar(obstacles, state["pac"], position, state, self.heuristic)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > len(path) - 1:
                closest_d = len(path) - 1
                closest_path = path
                if closest_d <= 1:
                    break
        if closest_d:
            return self.get_action_from_path(closest_path)

        return STAY
