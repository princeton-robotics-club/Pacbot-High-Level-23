from gym_simulator.tree_wrappers import PacBotNode
from gym_simulator.visualizer import Visualizer
from gym_simulator.tree_wrappers import manhattan_dist
from gym_simulator.grid import grid
from gym_simulator.variables import *
import numpy as np
import heapq
from math import isinf

CORNERS = [(1, 1), (1, -2), (-2, -2), (-2, 1)]
class PacBotNodeAStar(PacBotNode):
    def __init__(self, speed=1):
        super().__init__(speed)
        
    def next_node(self, action, heuristic):
        next = super().next_node(action)
        next.val += heuristic(self)
        return next

def heuristic(node: PacBotNodeAStar):
    # grid = node.env.game_state.grid
    # valid_corners = [corner for corner in CORNERS if grid[corner[0]][corner[1]] == o]
    
    return 0

if __name__ == "__main__":
    DEPTH = 5
    SPEED = 1
    MAX_SEARCHES = 75
    v_setting = input("Enter v to turn on visualizer.")
    visualizer = Visualizer() if v_setting == "v" else None
    runs = int(input("enter number of runs"))
    node = PacBotNodeAStar(speed=SPEED)
    move = 0
    run = 0
    pellets_remaining = 0
    move_total = 0
    wins = 0
    total_score = 0
    while run < runs:
        if visualizer:
            grid = node.env.render()
            visualizer.draw_grid(grid)
            
        action_values = [float("-inf") for _ in range(node.env.NUM_ACTIONS)]
        open_nodes = []
        for action in node.sensible_actions:
            child = node.next_node(action, heuristic)
            if action_values[action] <= child.val:
                action_values[action] = child.val
                heapq.heappush(open_nodes, (-child.val, child, action))
            
        # my idea to represent "time" to limit how many nodes are searched
        searches = 0
        
        while open_nodes and searches < MAX_SEARCHES:
            _, current_node, root_action = open_nodes.pop(0)
            # add if statement if current node is end of game (all pellets eaten)
            for action in current_node.sensible_actions:
                child = current_node.next_node(action, heuristic)
                if current_node.env.num_lives == child.env.num_lives:
                    action_values[root_action] = max(action_values[root_action],
                                                           child.val)
                    heapq.heappush(open_nodes, (-child.val, child, root_action))
                
            searches += 1
        
        # isolates moves that have largest values
        possible_next_moves = np.argwhere(action_values == np.amax(action_values)).flatten()
        # would prefer pacbot to not keep staying
        if node.direction in possible_next_moves:
            # "momentum" idea, keeps pacbot moving in previous direction
            next_move = node.direction
        else:
            # if there are ties, randomly chooses move
            next_move = np.random.choice(possible_next_moves, size=1)[0]
        
        next_node = node.next_node(next_move, heuristic)

        #node = node.next_node(np.argmax(action_values), heuristic)
        node.depth = 0
        move += 1
        print(move)
        if node.env.num_lives != next_node.env.num_lives:
            print(action_values)
            print(next_move)
            visualizer.wait()
        if next_node.done:
            pellets = np.sum(node.obs[np.array(node.env.STATE_VALUES) == "pellet"])
            print(pellets)
            pellets_remaining += pellets
            if pellets == 1.0:
                wins += 1
            print(action_values)
            print(next_move)
            move_total += move
            move = 0
            run += 1
            total_score += node.env.running_score
        node = next_node
        if visualizer:
            visualizer.wait2()
    print(pellets_remaining / runs)
    print(move_total / runs)
    print(total_score / runs)
    print(wins)
#[-243, -inf, -100280, -100280, -inf]