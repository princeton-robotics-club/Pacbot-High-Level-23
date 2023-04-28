import sys
sys.path.append("/Users/ernestmccarter/Documents/Princeton/Robotics/Pacbot/Spring23/Pacbot-Comms-23/src/decisionModule/Pacbot_High_Level")

from typing import Callable
import numpy as np
from constants import STAY, MOVE_TICKS, GHOST_MOVE_TICKS, UP, DOWN, LEFT, RIGHT, TURN_TICKS
from algorithms.opt_astar import astar
from algorithms.dijkstra import dijkstra
from algorithms.ghost_logic import ghost_init_dict, edited_respawn_path
from policies.policy import Policy
from rl.grid import grid
from rl.variables import o, O, e


class Ghost:
    def __init__(self, init_dict) -> None:
        self.init_dict = init_dict
        self.reset()

    def update(
        self, actual_move, move_counter, prev_move, pac_pos, red_pos, was_frightened
    ):
        self.next = actual_move  # TODO this may be unnecessary, but we should verify
        if move_counter < len(self.start_path):
            next_move = self.start_path[move_counter][0]
        elif was_frightened and actual_move in ((12, 15), (12, 16)):
            self.respawn(actual_move)
            return
        elif was_frightened and self.respawn_counter < len(edited_respawn_path):
            next_move = edited_respawn_path[self.respawn_counter]
            self.respawn_counter += 1
        else:
            next_move = self.chase_func(
                prev_move, pac_pos, red_pos, self.curr, self.next, self.scatter_pos
            )
        # if move_counter >= len(self.start_path):
        #     next_move = self.chase_func(
        #         prev_move, pac_pos, red_pos, self.curr, self.next, self.scatter_pos
        #     )
        # else:
        #     next_move = self.start_path[move_counter][0]
        self.prev_curr = self.curr
        self.curr = self.next
        self.next = next_move

    def respawn(self, position):
        self.respawn_counter = 0
        self.curr = position
        if position == (12, 15):
            self.next = (12, 16)
        else:
            self.next = (12, 17)
            self.respawn_counter = 1

    def reset(self):
        init_dict = self.init_dict
        self.prev_curr = None
        self.curr = init_dict["init_pos"]
        self.next = init_dict["init_npos"]
        self.chase_func = init_dict["chase_func"]
        self.scatter_pos = init_dict["scatter_pos"]
        self.start_path = init_dict["start_path"]
        self.respawn_counter = len(edited_respawn_path)
    
    def get_start_path(self, move_counter):
        return {position[0] for position in self.start_path[move_counter:]}


class GhostPredict:
    def __init__(self, test, debug) -> None:
        self.test = test
        self.ghost_names = ("r", "o", "p", "b")
        self.ghosts = [Ghost(ghost_init_dict[ghost]) for ghost in self.ghost_names]
        self.prev_pac_pos = (14, 7)
        self.was_frightened = False
        self.move_counter = 0
        self.prev_move = UP
        self.debug = debug

    def dPrint(self, message):
        if self.debug:
            print(message)

    def step(self, state):
        if state["life_lost"]:
            self.move_counter = 0
            self.reset()
            self.prev_pac_pos = (14, 7)
            self.was_frightened = False

        if not self.was_frightened:
            self.was_frightened = (
                state["rf"] or state["bf"] or state["of"] or state["pf"]
            )

        if state["r"] != self.ghosts[0].curr:
            self.dPrint("calced")
            self.dPrint(state["r"])
            self.dPrint(self.ghosts[0].curr)
            self.dPrint(state["pac"])
            self.update(
                state,
                self.move_counter,
                self.prev_move,
                self.prev_pac_pos,
                self.was_frightened,
            )
            self.move_counter += 1
        self.prev_pac_pos = state["pac"]

    def update(self, state, move_counter, prev_move, pac_pos, was_frightened):
        red_pos = state["r"]
        for index, ghost_name in enumerate(self.ghost_names):
            self.ghosts[index].update(
                state[ghost_name],
                move_counter,
                prev_move,
                pac_pos,
                red_pos,
                was_frightened,
            )

    def reset(self):
        for ghost in self.ghosts:
            ghost.reset()

    def get_next_moves(self, state):
        next_moves = {}
        for index, ghost_name in enumerate(self.ghost_names):
            if self.test:
                next_moves[ghost_name] = state[ghost_name]
            else:
                next_moves[ghost_name] = self.ghosts[index].next
        return next_moves
    
    def get_start_squares(self):
        if self.was_frightened:
            return []
        start_squares = set()
        for ghost in self.ghosts:
            start_squares.union(ghost.get_start_path(self.move_counter))
        
        return list(start_squares)


class HighLevelPolicy(Policy):
    def __init__(
        self,
        heuristic: Callable = None,
        debug=True,
        nearby_threshold: int = 5,
        test=False,
        ghost_tracker=None,
    ) -> None:
        super().__init__(debug)
        self.heuristic = heuristic
        self.NT = nearby_threshold
        self.ghost_tracker = (
            ghost_tracker if ghost_tracker else GhostPredict(test, debug)
        )

    # helper method to astar to a ghost, which is technically a barrier in maze
    def astar_ghost(self, maze, start, end, next_move, state=None):
        maze[end] = False
        maze[next_move] = False
        path = astar(maze, start, end, state, self.heuristic, True)
        maze[end] = True
        maze[next_move] = True
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
    #    orientation:   UP, LEFT, RIGHT, DOWN
    #    life_lost:     bool
    def get_action(self, state):

        self.ghost_tracker.step(state)

        obstacles = self.WALLS.copy()

        # stores non frightened ghost positions
        g_positions = []

        # stores frightened ghost positions
        f_positions = []

        # gets next position of ghosts
        next_moves = self.ghost_tracker.get_next_moves(state)

        unfrightened_ghosts = []
        # consider ghosts which are not frightened to be obstacles
        if state["rf"]:
            f_positions.append(state["r"])
        else:
            unfrightened_ghosts.append("r")
        if state["bf"]:
            f_positions.append(state["b"])
        else:
            unfrightened_ghosts.append("b")
        if state["of"]:
            f_positions.append(state["o"])
        else:
            unfrightened_ghosts.append("o")
        if state["pf"]:
            f_positions.append(state["p"])
        else:
            unfrightened_ghosts.append("p")

        for ghost in unfrightened_ghosts:
            g_positions.append((state[ghost], next_moves[ghost]))
            obstacles[state[ghost]] = True
            obstacles[next_moves[ghost]] = True
        
        for coord in self.ghost_tracker.get_start_squares():
            obstacles[coord] = True
        
        self.dPrint("phase: frightened ghosts")

        # target the closest frightened ghost not on pac
        # move to it if it exists and is within dt
        closest_d = None
        closest_path = None
        for f_position in f_positions:
            if obstacles[f_position]:
                continue
            self.dPrint("pathfinding to frightened ghost")
            path = astar(obstacles, state["pac"], f_position, state)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > path[-1].g:
                closest_d = path[-1].g
                closest_path = path
                if closest_d <= 1:
                    break

        # only chases frightened ghost if it's within certain distance
        if closest_d is not None and closest_d <= state["dt"] * TURN_TICKS:
            return self.get_action_from_path(closest_path, chase=True)

        self.dPrint("phase: power pellets")

        # target the closest power pellet not on pac
        # move to it, if it exists and (is further than 1 cell away or a ghost is within NT)
        # wait at it, if it exists and is within 1 cell and a ghost is not within NT cells
        nearby = False
        # closest_ghost_dist = float("inf")
        for g_position, next_pos in g_positions:
            if self.WALLS[g_position]:
                continue
            self.dPrint("pathfinding to ghost")
            path = self.astar_ghost(
                obstacles, state["pac"], g_position, next_pos, state
            )
            if path and path[-1].g <= self.NT * GHOST_MOVE_TICKS:
                nearby = True
                # break
        self.dPrint(f"nearby:{nearby}")
        positions = state["power_pellets"]  # np.argwhere(state["power_pellets"])
        closest_d = None
        closest_path = None
        closest_pellet = None
        for position in positions:
            self.dPrint("pathfinding to power pellet")
            path = astar(obstacles, state["pac"], position, state, self.heuristic)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > path[-1].g:
                closest_d = path[-1].g
                closest_path = path
                closest_pellet = position

        if closest_d is not None:
            # moves towards nearby power pellet
            # TODO potential bug - still moves towards power pellet even if ghost is in path
            if closest_d > MOVE_TICKS or nearby:
                self.dPrint(closest_d)
                return self.get_action_from_path(closest_path, closest_pellet)
            # waits until ghost approaches
            else:
                return STAY, 0

        self.dPrint("phase: pellets")
        # target the closest pellet not on pac
        # move to it if it exists
        #state["pellets"] = set(tuple(coord) for coord in list(state["pellets"]))
        closest_path = dijkstra(obstacles, state["pac"], state, 100)
        if closest_path:
            self.dPrint(closest_path)
            return self.get_action_from_path(closest_path)

        # last ditch attempt to run away from ghosts
        # TODO see if this is even necessary
        dir_sum = np.zeros(2)
        for g_position, next_pos in g_positions:
            diff = np.subtract(state["pac"], next_pos)
            dir_sum += 1 / np.linalg.norm(diff) * diff

        dir_sum_abs = np.abs(dir_sum)
        vert_move = UP if dir_sum[0] < 0 else DOWN
        horiz_move = LEFT if dir_sum[1] < 0 else RIGHT
        if dir_sum_abs[0] > dir_sum_abs[1]:
            new_x, new_y = tuple(np.add(state["pac"], self.ACTIONS[vert_move]))
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[new_x]) and grid[new_x][new_y] in {o, O, e}:
                return vert_move, 1
        else:
            new_x, new_y = tuple(np.add(state["pac"], self.ACTIONS[horiz_move]))
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[new_x]) and grid[new_x][new_y] in {o, O, e}:
                return horiz_move, 1
        
        return STAY, 0
