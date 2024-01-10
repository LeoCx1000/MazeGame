from blessed import Terminal
import argparse
from maze import Maze, Player, Size, Theme, DEFAULT_THEME

terminal = Terminal()

maze = Maze(Size((terminal.width // 4) - terminal.width % 2, (terminal.height // 2) - terminal.height % 2 + 2))
key_to_cardinal = {"W": "N", "A": "W", "S": "S", "D": "E"}


def main(full_render: bool, snap: bool):
    terminal = Terminal()

    print(terminal.home + terminal.clear + terminal.move_y(terminal.height // 2))
    print(terminal.black_on_darkkhaki(terminal.center("Generating maze...")))

    theme = Theme(
        wall=terminal.on_black("  "),
        tile=terminal.on_green("  "),
        player=terminal.on_green(DEFAULT_THEME.player),
        start=terminal.on_red("  "),
        end=terminal.red_on_green("❌"),
        up=terminal.black_on_green(DEFAULT_THEME.up),
        down=terminal.black_on_green(DEFAULT_THEME.down),
        left=terminal.black_on_green(DEFAULT_THEME.left),
        right=terminal.black_on_green(DEFAULT_THEME.right),
        trail=terminal.on_green(DEFAULT_THEME.trail),
    )

    maze = Maze(Size((terminal.width // 4) - 1, (terminal.height // 2) - 2))
    maze.generate()

    header = terminal.ljust(
        terminal.white_on_blue(terminal.center(f"Maze Game (Size {maze.size.width}x{maze.size.height})"))
        + "\n"
        + terminal.white_on_dodgerblue4(terminal.ljust(f"Use WASD to move. X to exit. This is you: {theme.player}"))
        + "\n"
    )

    with terminal.cbreak(), terminal.hidden_cursor():
        player = Player(maze=maze, theme=theme)
        player.snap = snap

        render_func = player.full_render if full_render else player.render

        print(terminal.home + terminal.clear + header)
        render_func(lpadding="  ")

        user_input = None
        while (not user_input or user_input.lower() != "x") and not player.won:
            user_input = terminal.inkey().upper()
            if user_input in ["W", "A", "S", "D"]:
                player.move(key_to_cardinal[user_input])
                render_func(lpadding="  ", console_clear_sequence=terminal.home + terminal.clear + header)

        if player.won:
            print(terminal.home + terminal.clear)
            print(terminal.black_on_lime(terminal.center(" ")))
            print(terminal.black_on_lime(terminal.center("Congratulations. You won!")))
            print(terminal.black_on_lime(terminal.center(" ")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="MazeGame", description="A fun little maze game")
    parser.add_argument("-f", "--full", action="store_true")
    parser.add_argument("-s", "--snap", action="store_true")
    flags = parser.parse_args()
    main(full_render=flags.full, snap=flags.snap)
