from typing import Callable
import numpy as np
from constants import STAY, MOVE_TICKS, GHOST_MOVE_TICKS, UP
from algorithms.opt_astar import astar
from algorithms.dijkstra import dijkstra
from algorithms.ghost_logic import ghost_init_dict, edited_respawn_path
from policies.policy import Policy


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


class HighLevelPolicy(Policy):
    def __init__(
        self,
        heuristic: Callable = None,
        debug=True,
        nearby_threshold: int = 2,
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
        path = astar(maze, start, end, state, self.heuristic)
        maze[end] = True
        maze[next_move] = True
        return path

    def get_action_from_path(self, path):
        if len(path) < 2:
            return STAY
        path = [path[i].position for i in range(min(3, len(path)))]
        movement = tuple(np.subtract(path[1], path[0]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                self.ghost_tracker.prev_move = index
                move_dist = 1
                for i in range(2, len(path)):
                    if (
                        tuple(np.subtract(path[i].position, path[i - 1].position))
                        == action
                    ):
                        move_dist += 1
                    else:
                        # Makes pacbot not stop at intersection
                        # does not account for cases where the destination is the intersection
                        move_dist -= 1
                        break
                return (index, move_dist)
        # assume that a turn happened
        if len(path) < 3:
            return STAY
        movement = tuple(np.subtract(path[2], path[1]))
        for index, action in enumerate(self.ACTIONS):
            if action == movement:
                move_dist = 1
                for i in range(3, len(path)):
                    if (
                        tuple(np.subtract(path[i].position, path[i - 1].position))
                        == action
                    ):
                        move_dist += 1
                return (index, move_dist)
        self.dPrint("ERROR: DOUBLE TURN")
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

        # consider ghosts which are not frightened to be obstacles
        if state["rf"]:
            f_positions.append(state["r"])
        else:
            g_positions.append((state["r"], next_moves["r"]))
            obstacles[state["r"]] = True
            obstacles[next_moves["r"]] = True
        if state["bf"]:
            f_positions.append(state["b"])
        else:
            g_positions.append((state["b"], next_moves["b"]))
            obstacles[state["b"]] = True
            obstacles[next_moves["b"]] = True
        if state["of"]:
            f_positions.append(state["o"])
        else:
            g_positions.append((state["o"], next_moves["o"]))
            obstacles[state["o"]] = True
            obstacles[next_moves["o"]] = True
        if state["pf"]:
            f_positions.append(state["p"])
        else:
            g_positions.append((state["p"], next_moves["p"]))
            obstacles[state["p"]] = True
            obstacles[next_moves["p"]] = True

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
        if closest_d is not None and closest_d <= state["dt"] * MOVE_TICKS:
            return self.get_action_from_path(closest_path)

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
            if not path or path[-1].g <= self.NT * GHOST_MOVE_TICKS:
                nearby = True
                # break
        self.dPrint(f"nearby:{nearby}")
        positions = state["power_pellets"]  # np.argwhere(state["power_pellets"])
        closest_d = None
        closest_path = None
        for position in positions:
            self.dPrint("pathfinding to power pellet")
            path = astar(obstacles, state["pac"], position, state, self.heuristic)
            if not path or len(path) < 2:
                continue
            if closest_d is None or closest_d > path[-1].g:
                closest_d = path[-1].g
                closest_path = path
                if closest_d <= 1:
                    break
        if closest_d is not None:
            # moves towards nearby power pellet
            # TODO potential bug - still moves towards power pellet even if ghost is in path
            if closest_d > MOVE_TICKS or nearby:
                return self.get_action_from_path(closest_path)
            # waits until ghost approaches
            else:
                return STAY

        self.dPrint("phase: pellets")
        # target the closest pellet not on pac
        # move to it if it exists
        state["pellets"] = set(tuple(coord) for coord in state["pellets"].tolist())
        closest_path = dijkstra(obstacles, state["pac"], state)
        if closest_path:
            return self.get_action_from_path(closest_path)

        return STAY
