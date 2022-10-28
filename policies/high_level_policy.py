import numpy as np
from simulator.game_engine.variables import *
from algorithms.astar import astar
from policies.policy import Policy


class HighLevelPolicy(Policy):
    NT = 3

    # helper method to astar to a ghost, which is technically a barrier in maze
    def astar_ghost(self, maze, start, end, state=None):
        maze[end] = False
        path = astar(maze, start, end, state)
        maze[end] = True
        return path

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
            return self.ACTIONS.index(
                tuple(np.subtract(closest_path[1], closest_path[0]))
            )

        print("phase: power pellets")

        # target the closest power pellet not on pac
        # move to it, if it exists and (is further than 1 cell away or a ghost is within NT)
        # wait at it, if it exists and is within 1 cell and a ghost is not within NT cells
        nearby = False
        for g_position in g_positions:
            if self.WALLS[g_position]:
                continue
            print("pathfinding to ghost")
            path = self.astar_ghost(obstacles, state["pac"], g_position, state)
            if not path or len(path) - 1 <= self.NT:
                nearby = True
                # break
        print("nearby:", nearby)
        positions = np.argwhere(state["power_pellets"])
        closest_d = None
        closest_path = None
        for position in positions:
            print("pathfinding to power pellet")
            path = astar(obstacles, state["pac"], position, state)
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
                return self.ACTIONS.index(
                    tuple(np.subtract(closest_path[1], closest_path[0]))
                )
            # waits until ghost approaches
            else:
                return self.ACTIONS.index((0, 0))

        print("phase: pellets")
        # target the closest pellet not on pac
        # move to it if it exists
        positions = np.argwhere(state["pellets"])
        closest_d = None
        closest_path = None
        for position in positions:
            path = astar(obstacles, state["pac"], position, state)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > len(path) - 1:
                closest_d = len(path) - 1
                closest_path = path
                if closest_d <= 1:
                    break
        if closest_d:
            return self.ACTIONS.index(
                tuple(np.subtract(closest_path[1], closest_path[0]))
            )

        return self.ACTIONS.index((0, 0))
