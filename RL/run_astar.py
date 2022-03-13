from gym_simulator.tree_wrappers import PacBotNode
from gym_simulator.visualizer import Visualizer
import numpy as np
import heapq
from math import isinf

class PacBotNodeAStar(PacBotNode):
    def __init__(self, visualizer, speed=1):
        super().__init__(visualizer, speed)
        # represents action from "root" node
        self.root_action = None
        
    def next_node(self, action, heuristic, root):
        next = super().next_node(action)
        if not root:
            if self.root_action is None:
                next.root_action = action
            else:
                next.root_action = self.root_action
        next.val += heuristic()
        return next

# need to figure out heuristic and inputs later
def heuristic():
    return 0

if __name__ == "__main__":
    DEPTH = 5
    SPEED = 1
    MAX_SEARCHES = 200
    visualizer = Visualizer()
    node = PacBotNodeAStar(visualizer=visualizer, speed=SPEED)
    
    while True:
        node.env.render()

        action_values = [float("-inf") for _ in range(node.env.NUM_ACTIONS)]
        open_nodes = [(0, node)]
        
        # my idea to represent "time" to limit how many nodes are searched
        searches = 0
        
        while searches < MAX_SEARCHES:
            current_node = open_nodes.pop(0)[1]
            # add if statement if current node is end of game (all pellets eaten)
            children_nodes = [current_node.next_node(action, heuristic, False) for action in current_node.sensible_actions]
            for child in children_nodes:
                action_values[child.root_action] = max(action_values[child.root_action],
                                                           child.val)
                heapq.heappush(open_nodes, (-child.val, child))
                
                # this implementation stopped adding to heap if
                # depth of nodes reached DEPTH
                # while open_nodes and searches < MAX_SEARCHES
                # ...
                # if child.depth == DEPTH:
                #     action_values[child.root_action] = max(action_values[child.root_action],
                #                                            child.val)
                # else:
                #     heapq.heappush(open_nodes, (-child.val, child))
                
            searches += 1
        print(action_values)
        
        # messy code in an attempt to turn moves into probability distribution
        # action_values = [[action, val] for action, val in enumerate(action_values) if not isinf(val)]
        # action_values = action_values - np.array([0, np.min(action_values, axis=0)[1] - 1])
        # action_values = action_values / np.array([1, np.sum(action_values, axis=0)[1]])
        # next_move = np.random.choice(action_values[:,0], 1, p=action_values[:,1])[0]
        # node = node.next_node(next_move, heuristic, True)
        # print(next_move)
        
        # if there are ties, randomly chooses move
        # probably unecessary but prevents pacman from just staying still
        next_move = np.random.choice(np.argwhere(action_values == np.amax(action_values)).flatten(), size=1)[0]
        print(next_move)
        node = node.next_node(next_move, heuristic, True)
        #node = node.next_node(np.argmax(action_values), heuristic, True)
        node.depth = 0
        visualizer.wait()
