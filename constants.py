"""Defines constants used throughout the application."""

import curses

# Grid and Aspect Ratio Configuration
# 12 horizontally and 7 vertically

GAME_SPEED = 1

GRID_COLS = 12
GRID_ROWS = 7

# Terminal character dimensions, each grid cell is represented as a 6x3 characters,
#   because each letter is twice as tall as it is wide in terminal.
CELL_WIDTH = 6
CELL_HEIGHT = 3

CANVAS_WIDTH = GRID_COLS * CELL_WIDTH   # 72 terminal characters
CANVAS_HEIGHT = GRID_ROWS * CELL_HEIGHT # 21 terminal lines

WIN_TEXT = [
        "█   █   ███   █   █    █   █  ███  █   █",
        " █ █   █   █  █   █    █   █   █   ██  █",
        "  █    █   █  █   █    █ █ █   █   █ █ █",
        "  █    █   █  █   █    ██ ██   █   █  ██",
        "  █     ███    ███     █   █  ███  █   █",
]

LOSE_TEXT = [
        "█   █   ███   █   █    █       ███    ████  █████",
        " █ █   █   █  █   █    █      █   █  █      █    ",
        "  █    █   █  █   █    █      █   █   ███   ████ ",
        "  █    █   █  █   █    █      █   █      █  █    ",
        "  █     ███    ███     █████   ███   ████   █████",
]
