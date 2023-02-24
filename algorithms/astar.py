from typing import List
from .node import Node

# FOR TESTING
# from node import Node
# import sys

# sys.path.append("../")
from constants import TURN_TICKS, MOVE_TICKS, UP

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
def astar(maze, start, end, state=None, heuristic=None):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    start = tuple(start)
    end = tuple(end)

    # Create start and end node
    start_node = Node(None, start, state["orientation"])
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list: List[Node] = []
    closed_list = []

    # Add the start node to open_list; oth index is g, 1st is h (heuristic), third is s
    # f=g+h
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node with lowest estimated cost
        # On first iteration, open_list is 1; it will increase in future iterations
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node) #closed_list is the list of "relaxed nodes"

        # Found the goal -> Essentially done at end, when we reach the end goal; ignored until then
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path <- Is this the final return

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

            # Make sure walkable terrain (i.e. check if it is a wall or not)
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

            skip = False

            # Checks if child is on the closed list; this helps prevent recalculating something we already did
            for closed_node in closed_list:
                if closed_node == child:
                    skip = True
                    break

            if skip:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + (
                MOVE_TICKS
                if child.pacbot_orientation % 2 == curr_orientation
                else TURN_TICKS
            )
            # current heuristic is euclidean distance
            child.h = (
                heuristic(child, end_node)
                if heuristic
                else ((child.position[0] - end_node.position[0]) ** 2)
                + ((child.position[1] - end_node.position[1]) ** 2)
            )
            child.f = child.g + child.h

            # Child is already in the open list
            on = False
            for open_node in open_list:
                if child == open_node:
                    on = True
                    # possibly need to rework this if heuristic isn't based on distance
                    if child.g > open_node.g:
                        skip = True
            if skip:
                continue #skip is a boolean; if true it goes to next iteration in for-loop

            if on:
                open_list.remove(child)

            # Add the child to the open list
            open_list.append(child)
    return []


def main():

    maze = [
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    ]

    start = (0, 0)
    end = (9, 6)
    path = astar(maze, start, end, {"orientation": UP})
    print(path)
    maze = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 1, 1, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 1, 1, 0, 0, 1, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    ]
    path = astar(maze, start, end, {"orientation": UP})
    print(path)


if __name__ == "__main__":
    main()
