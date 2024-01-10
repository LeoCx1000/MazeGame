from __future__ import annotations

from collections import deque
import random
from typing import NamedTuple

from .cell import Cell, Point, CellType

__all__ = ("Size", "Maze")


class Size(NamedTuple):
    width: int
    height: int


class Maze:
    def __init__(self, size: Size) -> None:
        self.size = size

        # The actual grid will be double the size:
        # Even indices will be tiles.
        # Odd indices will be walls and joining corridors.
        self._actual_size = Size(
            width=(size.width * 2) - 1,
            height=(size.height * 2) - 1,
        )
        self.grid: list[list[Cell]] = []

        self.start = Point(random.randint(0, self.size.width - 1), 0)
        self.end = Point(random.randint(0, self.size.width - 1), self.size.height - 1)

    @property
    def generated(self):
        """:class:`bool` Whether the bot has been generated."""
        return not not self.grid

    def generate(self):
        """Generates the maze using a randomized depth-first algorithm.

        https://en.wikipedia.org/wiki/Maze_generation_algorithm

        How it works:
        First, you have a stack of cells. Initially
        it only contains the starting point.

        - Visit the last cell of the stack.
        - Find a random neighbour that has not been visited.
          - if found, push neighbour to stack and draw
            a path to it, thus marking it as visited.
          - else, backtrack (pop from stack) and goto point 1.

        The algorithm finishes when the stack is exhausted."""
        self.grid = [
            [Cell(type=CellType.wall, point=Point(x, y, is_actual=True)) for x in range(self._actual_size.width)]
            for y in range(self._actual_size.height)
        ]

        self.start.set(self, CellType.start)

        stack: deque[Cell] = deque()
        start = self.start.get(self)

        if start:
            stack.append(start)

        while stack:
            current = stack[-1]

            neighbours = current.empty_neighbours(self)

            if not neighbours:
                stack.pop()
                continue

            next, direction = random.choice(neighbours)
            next.type = CellType.tile
            x, y = current.coord.midway(next.coord)
            midway = self.grid[y][x]
            midway.type = CellType.tile

            # Set the directions that we can go towards.
            match direction:
                case "N":
                    current.hallways.N = True
                    next.hallways.S = True
                    midway.hallways.N = True
                    midway.hallways.S = True

                case "S":
                    current.hallways.S = True
                    next.hallways.N = True
                    midway.hallways.N = True
                    midway.hallways.S = True

                case "W":
                    current.hallways.W = True
                    next.hallways.E = True
                    midway.hallways.W = True
                    midway.hallways.E = True

                case "E":
                    current.hallways.E = True
                    next.hallways.W = True
                    midway.hallways.W = True
                    midway.hallways.E = True

            stack.append(next)

        self.end.set(self, CellType.end)

        for row in self.grid:
            for tile in row:
                tile.fill_paths(self)
