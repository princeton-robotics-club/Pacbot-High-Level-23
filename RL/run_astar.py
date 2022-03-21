from gym_simulator.tree_wrappers import PacBotNode
from gym_simulator.visualizer import Visualizer
import numpy as np
import heapq
from math import isinf

class PacBotNodeAStar(PacBotNode):
    def __init__(self, visualizer, speed=1):
        super().__init__(visualizer, speed)
        
    def next_node(self, action, heuristic):
        next = super().next_node(action)
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
        open_nodes = []
        for action in node.sensible_actions:
            child = node.next_node(action, heuristic)
            action_values[action] = max(action_values[action], child.val)
            heapq.heappush(open_nodes, (-child.val, child, action))
            
        # my idea to represent "time" to limit how many nodes are searched
        searches = 0
        
        while searches < MAX_SEARCHES:
            _, current_node, root_action = open_nodes.pop(0)
            # add if statement if current node is end of game (all pellets eaten)
            for action in current_node.sensible_actions:
                child = current_node.next_node(action, heuristic)
                action_values[root_action] = max(action_values[root_action],
                                                           child.val)
                heapq.heappush(open_nodes, (-child.val, child, root_action))
                
            searches += 1
        print(action_values)
        
        # if there are ties, randomly chooses move
        # probably unecessary but prevents pacman from just staying still
        next_move = np.random.choice(np.argwhere(action_values == np.amax(action_values)).flatten(), size=1)[0]
        print(next_move)
        node = node.next_node(next_move, heuristic)
        #node = node.next_node(np.argmax(action_values), heuristic)
        node.depth = 0
        visualizer.wait2()
