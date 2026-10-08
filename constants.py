"""Defines constants used throughout the application."""

import curses


WIDTH = 80
HEIGHT = 24

GRID_WIDTH = 20
GRID_HEIGHT = 7

STYLES = {
    "title": curses.A_BOLD, "X": curses.A_BOLD, "O": curses.A_BOLD,
    "success": curses.A_BOLD, "warning": curses.A_BOLD, "muted": curses.A_DIM,
}