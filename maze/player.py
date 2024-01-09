from __future__ import annotations

from collections import deque
from .maze import Maze
from .theme import Theme, DEFAULT_THEME
from itertools import pairwise

from .cell import Cell, CardinalDirection, intersections, CARDINAL_DIRECTIONS, CellType

__all__ = ("Player",)


class Player:
    def __init__(
        self,
        maze: Maze,
        theme: Theme = DEFAULT_THEME,
        look_behind: int | None = None,
        look_ahead: int = 3,
    ):
        start = maze.start.get(maze)
        if not start:
            raise RuntimeError("Passed a non-generated map.")

        self.maze: Maze = maze
        self.cell: Cell = start
        self.snap: bool = True
        self.theme: Theme = theme
        self.look_ahead: int = look_ahead
        self.moves: deque[Cell] = deque(maxlen=look_behind)

    @property
    def won(self):
        """Whether the player is in the final tile."""
        return self.cell.coord == self.maze.end

    def draw_segment(self, display_maze: list[list[str]], current: Cell, next: Cell, character: str):
        x_1, y_1 = current.coord.actual()
        x_2, y_2 = next.coord.actual()

        if x_1 > x_2:
            x_1, x_2 = x_2, x_1

        if y_1 > y_2:
            y_1, y_2 = y_2, y_1

        for x in range(x_1, x_2 + 1):
            for y in range(y_1, y_2 + 1):
                display_maze[y][x] = character

    def draw_possible_paths(self, display_maze: list[list[str]], previous: Cell | None, current: Cell):
        for direction in CARDINAL_DIRECTIONS:
            if current.paths[direction] != previous and current.hallways[direction]:
                _, next_tile = intersections[direction]
                x, y = current.coord.midway(next_tile(current.coord))
                display_maze[y][x] = self.theme.direction(direction)

    def add_paths(self, display_maze: list[list[str]], *, previous: Cell | None, current: Cell, depth: int = 0):
        """Recursively draw paths towards next directions."""
        if depth == self.look_ahead:
            self.draw_possible_paths(display_maze, previous, current)
        else:
            for direction in CARDINAL_DIRECTIONS:
                if (next := current.paths[direction]) and next != previous and next != current:
                    self.draw_segment(display_maze, current, next, self.theme.tile)
                    self.add_paths(display_maze, previous=current, current=next, depth=depth + 1)

    def render(self, lpadding: str = "", console_clear_sequence: str = ""):
        display_maze = [[self.theme.get(CellType.wall) for _ in row] for row in self.maze.grid]

        try:
            previous = self.moves[-2]
        except:
            previous = None

        for prev, curr in pairwise(self.moves):
            self.draw_possible_paths(display_maze, None, curr)
            self.draw_segment(display_maze, prev, curr, self.theme.trail)

        self.add_paths(display_maze, previous=previous, current=self.cell)

        # Render static elements
        x, y = self.maze.start.actual()
        display_maze[y][x] = self.theme.start

        x, y = self.maze.end.actual()
        display_maze[y][x] = self.theme.end

        x, y = self.cell.coord.actual()
        display_maze[y][x] = self.theme.player

        # Print everything.
        if console_clear_sequence:
            print(console_clear_sequence)

        print(lpadding + f"\n{lpadding}".join("".join(x for x in row) for row in display_maze))

    def full_render(self, lpadding: str = "", console_clear_sequence: str = ""):
        display_maze = [[self.theme.get(c.type) for c in row] for row in self.maze.grid]

        # Render static elements
        x, y = self.maze.start.actual()
        display_maze[y][x] = self.theme.start

        x, y = self.maze.end.actual()
        display_maze[y][x] = self.theme.end

        x, y = self.cell.coord.actual()
        display_maze[y][x] = self.theme.player

        # Print everything.
        if console_clear_sequence:
            print(console_clear_sequence)

        print(lpadding + f"\n{lpadding}".join("".join(x for x in row) for row in display_maze))

    def move(self, direction: CardinalDirection | str):
        """Moves the player in one cardinal direction.

        direction: CardinalDirection
            The direction to move towards. non-cardinal directions will be ignored.
        """
        if direction not in CARDINAL_DIRECTIONS:
            return

        if self.snap:
            next = self.cell.paths[direction]

        else:
            if self.cell.hallways[direction]:
                _, getter = intersections[direction]
                next = getter(self.cell.coord).get(self.maze)

                if next:
                    self.moves.append(self.cell)
                    self.cell = next
