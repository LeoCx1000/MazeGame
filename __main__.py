from blessed import Terminal
import argparse
import unicodedata
from maze import Maze, Player, Size, Theme, DEFAULT_THEME

terminal = Terminal()

maze = Maze(Size((terminal.width // 4) - terminal.width % 2, (terminal.height // 2) - terminal.height % 2 + 2))
key_to_cardinal = {
    "W": "N",
    "A": "W",
    "S": "S",
    "D": "E",
    "\U0000001b\N{LEFT SQUARE BRACKET}\N{LATIN CAPITAL LETTER A}": "N",  # arrow UP
    "\U0000001b\N{LEFT SQUARE BRACKET}\N{LATIN CAPITAL LETTER D}": "W",  # arrow RIGHT
    "\U0000001b\N{LEFT SQUARE BRACKET}\N{LATIN CAPITAL LETTER B}": "S",  # arrow DOWN
    "\U0000001b\N{LEFT SQUARE BRACKET}\N{LATIN CAPITAL LETTER C}": "E",  # arrow LEFT
}


def to_string(chars):
    ret = ""
    for c in chars:
        digit = f"{ord(c):x}"
        name = unicodedata.name(c, None)
        ret += ("\\N{" + name + "}") if name else f"\\U{digit:>08}"
    return ret


def main(full_render: bool, snap: bool):
    terminal = Terminal()

    print(terminal.home + terminal.clear + terminal.move_y(terminal.height // 2))
    print(terminal.black_on_darkkhaki(terminal.center("Generating maze...")))

    dark_theme = Theme(
        wall=terminal.on_black("  "),
        tile=terminal.on_gray23("  "),
        player=terminal.on_gray23(DEFAULT_THEME.player),
        start=terminal.on_red("  "),
        end=terminal.red_on_gray23("❌"),
        up=terminal.black_on_gray23(DEFAULT_THEME.up),
        down=terminal.black_on_gray23(DEFAULT_THEME.down),
        left=terminal.black_on_gray23(DEFAULT_THEME.left),
        right=terminal.black_on_gray23(DEFAULT_THEME.right),
        trail=terminal.on_gray23(DEFAULT_THEME.trail),
    )

    light_theme = Theme(
        wall=terminal.on_white("  "),
        tile=terminal.on_lightskyblue4("  "),
        player=terminal.on_lightskyblue4(DEFAULT_THEME.player),
        start=terminal.on_red("  "),
        end=terminal.red_on_lightskyblue4("❌"),
        up=terminal.black_on_lightskyblue4(DEFAULT_THEME.up),
        down=terminal.black_on_lightskyblue4(DEFAULT_THEME.down),
        left=terminal.black_on_lightskyblue4(DEFAULT_THEME.left),
        right=terminal.black_on_lightskyblue4(DEFAULT_THEME.right),
        trail=terminal.on_lightskyblue4(DEFAULT_THEME.trail),
    )

    maze = Maze(Size((terminal.width // 4) - 1, (terminal.height // 2) - 2))
    maze.generate()

    db = terminal.white_on_dodgerblue4
    lb = terminal.black_on_steelblue1

    original_size = (terminal.width, terminal.height)

    header = terminal.ljust(
        terminal.white_on_blue(terminal.center(f"Maze Game (Size {maze.size.width}x{maze.size.height})"))
        + "\n"
        + "\n".join(
            db(terminal.ljust(line))
            for line in terminal.wrap(
                f"{lb('WASD')} or arrows to move. {lb('Q')} to quit. This is you: {dark_theme.player}. "
                f"{lb('T')} to toggle theme. {lb('R')} to tgl render mode. {lb('E')} to tgl snap mode."
            )
        )
        + "\n"
    )

    with terminal.cbreak(), terminal.hidden_cursor():
        player = Player(maze=maze, theme=dark_theme)
        player.snap = snap

        render_func = player.full_render if full_render else player.render

        print(terminal.home + terminal.clear + header)
        render_func(lpadding="  ")

        while not player.won:
            user_input = terminal.inkey().upper()

            if original_size != (terminal.width, terminal.height):
                print(terminal.home + terminal.clear)
                print(terminal.white_on_red(terminal.center(" ")))
                print(terminal.white_on_red(terminal.center("Terminal window was resized. Try again.")))
                print(terminal.white_on_red(terminal.center(" ")))
                break

            if user_input == "Q":
                print(terminal.home + terminal.clear)
                print(terminal.white_on_red(terminal.center(" ")))
                print(terminal.white_on_red(terminal.center("You quit.")))
                print(terminal.white_on_red(terminal.center(" ")))
                break

            footer = None
            try:
                player.move(key_to_cardinal[user_input])
            except KeyError:
                if user_input == "T":
                    player.theme = light_theme if player.theme == dark_theme else dark_theme
                elif user_input == "R":
                    render_func = player.render if render_func == player.full_render else player.full_render
                elif user_input == "E":
                    player.snap = not player.snap
                else:
                    footer = terminal.black_on_red(terminal.center(f"Unknown key: {to_string(user_input)}"))

            render_func(lpadding="  ", console_clear_sequence=terminal.home + terminal.clear + header)

            if footer:
                print(footer)

        else:
            print(terminal.home + terminal.clear)
            print(terminal.black_on_lime(terminal.center(" ")))
            print(terminal.black_on_lime(terminal.center("Congratulations. You won!")))
            print(terminal.black_on_lime(terminal.center(" ")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="MazeGame", description="A fun little maze game")
    parser.add_argument("-pv", "--partial", action="store_false", help="Pass to start in partial visibility mode.")
    parser.add_argument("-s", "--snap", action="store_true", help="Pass to start with snap movement mode.")
    flags = parser.parse_args()
    main(full_render=flags.partial, snap=flags.snap)
