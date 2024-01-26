from textual.app import App, ComposeResult

from textual.widgets import Header, Static, Footer, Placeholder
from textual.containers import Horizontal, Vertical
from rich_pixels import Pixels

from maze.cell import CardinalDirection


class Map(Static):
    def compose(self):
        yield Placeholder("Map")


class CurrentRoom(Static):
    def compose(self):
        yield Placeholder("Player POV")


class MazeGame(App):
    BINDINGS = [("w", "w"), ("a", "a"), ("s", "s"), ("d", "d")]
    CSS_PATH = "this.tcss"

    def compose(self):
        yield Header(show_clock=True)
        yield Horizontal(
            CurrentRoom(),
            Map(),
        )

    def move(self, direction: CardinalDirection):
        st = self.query_one(Static)
        st.update(f"{direction} {repr(st.size)}")

    def action_w(self):
        self.move("N")

    def action_a(self):
        self.move("W")

    def action_s(self):
        self.move("S")

    def action_d(self):
        self.move("E")


MazeGame().run()
