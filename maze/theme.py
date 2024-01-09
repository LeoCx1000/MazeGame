from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .cell import CellType, CardinalDirection

__all__ = ("Theme", "DEFAULT_THEME")


class Theme(NamedTuple):
    wall: str
    tile: str
    player: str
    start: str
    end: str
    up: str
    down: str
    left: str
    right: str
    trail: str

    def get(self, type: CellType):
        return getattr(self, type.name, "")

    def direction(self, direction: CardinalDirection):
        return {
            "N": self.up,
            "S": self.down,
            "E": self.right,
            "W": self.left,
        }[direction]


DEFAULT_THEME = Theme(
    wall="\N{WHITE LARGE SQUARE}",
    tile="\N{LARGE BROWN SQUARE}",
    start="\N{LARGE RED SQUARE}",
    end="\N{LARGE GREEN SQUARE}",
    player="\N{SMILING FACE WITH HORNS}",
    up="⬆️",
    down="⬇️",
    left="⬅️",
    right="➡️",
    trail="🔸",
)
