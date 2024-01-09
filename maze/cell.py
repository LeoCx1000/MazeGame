from __future__ import annotations

from enum import Enum
from typing import NamedTuple, Literal, TypeAlias, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .maze import Maze

CardinalDirection: TypeAlias = Literal["N", "S", "E", "W"]
CARDINAL_DIRECTIONS: list[CardinalDirection] = ["N", "S", "E", "W"]

# fmt: off
intersections: dict[CardinalDirection,tuple[tuple[CardinalDirection, CardinalDirection], Callable[[Point], Point]]] = {
    "N": (("W", "E"), lambda p: Point(p.x, p.y - (1 + p.is_actual), is_actual=p.is_actual)),
    "S": (("E", "W"), lambda p: Point(p.x, p.y + (1 + p.is_actual), is_actual=p.is_actual)),
    "W": (("S", "N"), lambda p: Point(p.x - (1 + p.is_actual), p.y, is_actual=p.is_actual)),
    "E": (("N", "S"), lambda p: Point(p.x + (1 + p.is_actual), p.y, is_actual=p.is_actual))
}

# fmt: on


class CellType(Enum):
    start = 0
    end = 1
    tile = 2
    wall = 3


class Point(NamedTuple):
    x: int
    y: int
    is_actual: bool = False

    def actual(self):
        if self.is_actual:
            return self.x, self.y
        return self.x * 2, self.y * 2

    def get(self, maze: Maze):
        x, y = self.actual()
        try:
            if x < 0 or y < 0:
                return None
            return maze.grid[y][x]
        except:
            return None

    def set(self, maze: Maze, type: CellType):
        cell = self.get(maze)
        if cell:
            cell.type = type

    def midway(self, point: Point):
        this_x, this_y = self.actual()
        that_x, that_y = point.actual()
        return (this_x + that_x) // 2, (this_y + that_y) // 2

    def __repr__(self):
        return f"{type(self).__name__}({self.x//(self.is_actual + 1)}, {self.y//(self.is_actual + 1)})"

    def __eq__(self, other: object):
        return isinstance(other, type(self)) and other.actual() == self.actual()


class Hallways:
    __slots__ = ("N", "S", "E", "W")

    def __init__(self):
        self.N: bool = False
        self.S: bool = False
        self.E: bool = False
        self.W: bool = False

    def __setitem__(self, *args):
        return self.__setattr__(*args)

    def __getitem__(self, direction: CardinalDirection) -> bool:
        return getattr(self, direction)


class Paths:
    __slots__ = ("N", "S", "E", "W")

    def __init__(self):
        self.N: Cell | None = None
        self.S: Cell | None = None
        self.E: Cell | None = None
        self.W: Cell | None = None

    def __setitem__(self, key: CardinalDirection, value: Cell | None):
        return self.__setattr__(key, value)

    def __getitem__(self, direction: CardinalDirection) -> Cell | None:
        return getattr(self, direction)


class Cell:
    __slots__ = ("type", "coord", "hallways", "paths")

    def __init__(self, type: CellType, point: Point):
        self.type = type
        self.coord = point
        self.hallways = Hallways()
        self.paths = Paths()

    def empty_neighbours(self, maze: Maze) -> list[tuple[Cell, CardinalDirection]]:
        x, y = self.coord.actual()
        dirs: list[CardinalDirection] = ["N", "S", "W", "E"]
        return [
            (cell, dirs[index])
            for index, cell in enumerate(
                [
                    Point(x, y - 2, is_actual=True).get(maze),
                    Point(x, y + 2, is_actual=True).get(maze),
                    Point(x - 2, y, is_actual=True).get(maze),
                    Point(x + 2, y, is_actual=True).get(maze),
                ]
            )
            if cell and cell.type == CellType.wall
        ]

    def fill_path_towards(self, maze: Maze, direction: CardinalDirection):
        if self.paths[direction] is not None:
            return self

        if not self.hallways[direction]:
            # Dead end
            self.paths[direction] = self
            return

        (left, right), next_func = intersections[direction]
        current = self.coord
        while next := next_func(current).get(maze):
            if next.hallways[left] or next.hallways[right] or next.type == CellType.end:
                self.paths[direction] = next
                break

            if not next.hallways[direction]:
                # Dead end.
                self.paths[direction] = next
                break

            current = next.coord
        else:
            # Dead end.
            self.paths[direction] = next

    def fill_paths(self, maze: Maze):
        if self.type is CellType.wall:
            return
        self.fill_path_towards(maze, "N")
        self.fill_path_towards(maze, "S")
        self.fill_path_towards(maze, "E")
        self.fill_path_towards(maze, "W")

    def __str__(self):
        if self.type is CellType.start:
            return "\N{LARGE RED SQUARE}"
        elif self.type is CellType.end:
            return "\N{LARGE GREEN SQUARE}"
        elif self.type is CellType.wall:
            return "\N{WHITE LARGE SQUARE}"
        else:
            return "\N{LARGE BROWN SQUARE}"

    def __repr__(self):
        return f"<{type(self).__name__} at {self.coord}>"

    def __eq__(self, other: object):
        return isinstance(other, type(self)) and other.coord == self.coord
