from __future__ import annotations


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None, orientation=None):
        self.parent = parent
        self.position = position

        # estimated cost of getting to this node
        self.g = 0
        # estimated cost of getting to destination from this node
        self.h = 0
        # estimated cost of entire path
        self.f = 0

        self.pacbot_orientation = orientation

    def __eq__(self, other: Node):
        return self.position == other.position and (
            self.pacbot_orientation is None
            or other.pacbot_orientation is None
            or self.pacbot_orientation % 2 == other.pacbot_orientation % 2
        )
