import random
from math import floor, ceil
from enum import Enum
from typing import NamedTuple
from rich.color import Color
from rich import pretty

pretty.install()


class Tile(Enum):
    wall = "#"
    hallway = "X"
    door = "D"
    tile = " "
    chest = "C"


class Size(NamedTuple):
    width: int
    height: int


class Position(NamedTuple):
    x: int
    y: int


_POSITIONS: dict[int, dict[int, Position]] = {}


def pos(x: int, y: int):
    try:
        return _POSITIONS[x][y]
    except KeyError:
        position = Position(x, y)
        _POSITIONS.setdefault(x, {})
        _POSITIONS[x][y] = position
        return position


class Chest:
    ...


class Room:
    SIZE: Size = Size(20, 20)

    # Door settings.
    MIN_DOORS: int = 1
    MAX_DOORS: int = 4
    DOOR_WEIGHTS_START: int = 0
    DOOR_WEIGHTS_STEP: int = 0

    # Chest settings.
    MIN_CHESTS: int = 0
    MAX_CHESTS: int = 0
    CHEST_WEIGHTS_START: int = 0
    CHEST_WEIGHTS_STEP: int = 0
    CHEST_CLASSES: list[type[Chest]] = []

    def __init__(self):
        self.render_cache: dict[tuple[Position | None, bool], list[str]] = {}
        self.grid: list[list[Tile]] = []

        self.door_count, *_ = random.choices(
            range(self.MIN_DOORS, max(self.MAX_DOORS, self.MIN_DOORS) + 1),
            weights=range(
                self.DOOR_WEIGHTS_START,
                self.DOOR_WEIGHTS_STEP * (self.MAX_DOORS - self.MIN_DOORS + 1) + self.DOOR_WEIGHTS_START,
                self.DOOR_WEIGHTS_STEP,
            )
            if self.DOOR_WEIGHTS_STEP
            else None,
        )

        if self.MAX_CHESTS and not self.CHEST_CLASSES:
            raise RuntimeError(f"Class {type(self).__name__!r} has MAX_CHESTS={self.MAX_CHESTS} with no chest classes.")

        self.chest_count, *_ = random.choices(
            range(self.MIN_CHESTS, max(self.MIN_CHESTS, self.MAX_CHESTS) + 1),
            weights=range(
                self.CHEST_WEIGHTS_START,
                self.CHEST_WEIGHTS_STEP * (self.MAX_CHESTS - self.MIN_CHESTS + 1) + self.CHEST_WEIGHTS_START,
                self.CHEST_WEIGHTS_STEP,
            )
            if self.CHEST_WEIGHTS_STEP
            else None,
        )

        self.construct()
        self.opened_chests: dict[Position, Chest] = {}
        self.put_chests()

    def construct(self):
        ...

    def put_chests(self):
        ...

    def pprint(self):
        for row in self.grid:
            print("".join(x.value for x in row))

    def render(self, player: Position | None = None, zoomed: bool = False) -> list[str]:
        if c := self.render_cache.get((player, zoomed), None):
            return c


class StarterChest(Chest):
    ...


class StartingRoom(Room):
    MIN_DOORS = 4
    MIN_CHESTS = 1
    MAX_CHESTS = 2
    CHEST_CLASSES = [StarterChest]
    CHEST_WEIGHTS_START = 2
    CHEST_WEIGHTS_STEP = -1

    def construct(self):
        self.grid = grid = [
            [Tile.wall for _ in range(self.SIZE.width)],
            *[[Tile.wall] + ([Tile.tile] * (self.SIZE.width - 2)) + [Tile.wall] for _ in range(self.SIZE.height - 2)],
            [Tile.wall for _ in range(self.SIZE.width)],
        ]
        midway = self.SIZE.width / 2
        even = self.SIZE.width % 2 == 0
        grid[0][floor(midway) - even : ceil(midway) + 1 + even] = [Tile.hallway] * len(
            range(floor(midway) - even, ceil(midway) + 1 + even)
        )
        grid[-1][floor(midway) - even : ceil(midway) + 1 + even] = [Tile.hallway] * len(
            range(floor(midway) - even, ceil(midway) + 1 + even)
        )

        # print("before")
        # self.pprint()
        # midway = self.SIZE.height / 2
        # for i in range(floor(midway) - 1, ceil(midway) + 1):
        #     print(f"setting grid[{i}][0] to hallway")
        #     grid[i][0] = Tile.hallway
        #     grid[i][-1] = Tile.hallway

        self.grid = grid


class Room22(StartingRoom):
    SIZE = Size(21, 21)


room = StartingRoom()
room.pprint()
room2 = Room22()
room2.pprint()
