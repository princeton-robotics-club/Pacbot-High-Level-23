from heapq import heappush, heappop, heapify
from typing import List, Tuple
from .node import Node

# FOR TESTING
# from node import Node
# import sys

# sys.path.append("../")
from constants import TURN_TICKS, MOVE_TICKS, UP


def dijkstra(maze, start, state):
    start = tuple(start)

    pellets = state["pellets"]

    # Create start and end node
    start_node = Node(None, start, state["orientation"])
    start_node.g = 0

    # Initialize both open and closed list
    open_list: List[Tuple[int, Node]] = []
    closed_list = set()

    # Add the start node
    open_list.append((start_node.g, start_node))

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node with lowest estimated cost
        _, current_node = heappop(open_list)
        closed_list.add((current_node.position, current_node.pacbot_orientation % 2))

        # found nearest neighbor
        if current_node.position in pellets:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        # Generate children
        children: List[Node] = []
        curr_orientation = current_node.pacbot_orientation % 2
        turned = False
        for direction, new_position in enumerate(
            [(-1, 0), (0, -1), (1, 0), (0, 1)]
        ):  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
            )

            # Make sure within range
            if (
                node_position[0] > (len(maze) - 1)
                or node_position[0] < 0
                or node_position[1] > (len(maze[len(maze) - 1]) - 1)
                or node_position[1] < 0
            ):
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            new_node = None
            # Create new node
            if curr_orientation == direction % 2:
                new_node = Node(
                    current_node, node_position, current_node.pacbot_orientation
                )
            elif not turned:
                new_node = Node(current_node, current_node.position, direction)
                turned = True

            # Append
            if new_node:
                children.append(new_node)

        # Loop through children
        for child in children:

            skip = (child.position, child.pacbot_orientation % 2) in closed_list

            # Child is on the closed list
            if skip:
                continue

            # Create the g value
            child.g = current_node.g + (
                MOVE_TICKS
                if child.pacbot_orientation % 2 == curr_orientation
                else TURN_TICKS
            )

            # Child is already in the open list
            on = False
            champ = None
            for index, item in enumerate(open_list):
                _, open_node = item
                if child == open_node:
                    on = True
                    champ = index
                    # possibly need to rework this if heuristic isn't based on distance
                    if child.g > open_node.g:
                        skip = True
            if skip:
                continue

            if on:
                open_list.pop(champ)

            heapify(open_list)
            # Add the child to the open list
            heappush(open_list, (child.g, child))
    return None
