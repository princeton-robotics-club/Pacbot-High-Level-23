from gym_simulator.tree_wrappers import PacBotNode
import numpy as np

if __name__ == "__main__":
    DEPTH = 5
    SPEED = 1

    node = PacBotNode(speed=SPEED)
    
    while True:
        node.env.render()

        action_values = [float("-inf") for _ in range(node.env.NUM_ACTIONS)]
        nodes = [node.next_node(action) for action in node.sensible_actions]
        actions = list(node.sensible_actions)
        print(node.sensible_actions)
        
        curr_node = nodes.pop(0)
        curr_action = actions.pop(0)
        while curr_node.depth <= DEPTH:
            action_values[curr_action] = max(action_values[curr_action], curr_node.val)
            for action in curr_node.sensible_actions:
                nodes.append(curr_node.next_node(action))
                actions.append(curr_action)
            curr_node = nodes.pop(0)
            curr_action = actions.pop(0)

        node = node.next_node(np.argmax(action_values))
        node.depth = 0 # need to reset depth in order to setup bfs loop again
        print(action_values)
        input()
