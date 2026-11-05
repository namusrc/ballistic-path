import curses
from curses.textpad import rectangle
from textwrap import wrap
from constants import (
    CELL_HEIGHT,
    CELL_WIDTH,
    LOSE_TEXT,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
    WIN_TEXT,
)

COLOR_MAP = {
    "yellow": curses.COLOR_YELLOW,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "blue": curses.COLOR_BLUE,
    "cyan": curses.COLOR_CYAN,
    "magenta": curses.COLOR_MAGENTA,
    "white": curses.COLOR_WHITE,
    "black": curses.COLOR_BLACK
}

def init_colors():
    curses.start_color()
    curses.use_default_colors()

    color_pairs = {}
    # Pair 1: Default Border / Canvas Frame / Text
    curses.init_pair(1, curses.COLOR_WHITE, -1)

    # Dynamic pairs for colors defined in COLOR_MAP
    idx = 2
    for name, curses_color in COLOR_MAP.items():
        curses.init_pair(idx, curses_color, -1)
        color_pairs[name] = curses.color_pair(idx)
        idx += 1

    return color_pairs


def render_resize_message(stdscr):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    available_width = max_x - 1
    lines = []
    if max_y > 0 and available_width > 0:
        requirement = wrap("Need 80 x 24", available_width)
        quit_prompt = wrap("Q to quit", available_width)
        lines = requirement
        if max_y > len(lines):
            lines.extend(quit_prompt)
        if max_y > len(lines):
            lines = wrap("Terminal too small", available_width) + lines

    top = max(0, (max_y - len(lines)) // 2)
    for row, text in enumerate(lines):
        if top + row >= max_y or max_x <= 1:
            break
        x = max(0, (max_x - len(text)) // 2)
        try:
            stdscr.addnstr(top + row, x, text, max_x - x - 1)
        except curses.error:
            pass
    stdscr.refresh()


def render_frame(stdscr, engine, color_pairs):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    if max_y < VIEWPORT_HEIGHT or max_x < VIEWPORT_WIDTH:
        render_resize_message(stdscr)
        return False  # Signals window too small

    offset_y = 1
    offset_x = 2

    rectangle(stdscr, 1, 0, 22, 75)

    # Render Object Instances
    for inst_id, obj in engine.objects.items():
        base_screen_x = offset_x + (obj.grid_x * CELL_WIDTH)
        base_screen_y = offset_y + (obj.grid_y * CELL_HEIGHT)

        if obj.object_type.designs:
            design = obj.object_type.designs.get(str(obj.angle))
        else:
            design = obj.object_type.design
            
        is_selected = (inst_id == engine.selected_id)
        attr = curses.A_BOLD if is_selected else curses.A_DIM

        for pos in range(1, 19):
            sub_r = (pos - 1) // 6
            sub_c = (pos - 1) % 6


            # Show IDs of Objects, only for those that are interactable.
            if pos == 10 and (obj.object_type.is_movable or obj.object_type.is_rotatable):
                val = inst_id
            elif pos == 9 and (obj.object_type.is_movable or obj.object_type.is_rotatable):
                val = " "
            else:
                val = design.get(str(pos), " ")[0]

            screen_y = base_screen_y + sub_r
            screen_x = base_screen_x + sub_c

            if val in color_pairs:
                str_to_draw = design.get(str(pos), " ")[1]
                color_attr = color_pairs[val] | attr
            else:
                str_to_draw = f"{val}"
                color_attr = curses.color_pair(1) | attr

            try:
                stdscr.addstr(screen_y, screen_x, str_to_draw, color_attr)
            except curses.error:
                pass

    # Render Bullets
    for bullet in engine.bullets:
        screen_x = offset_x + int(bullet.px)
        screen_y = offset_y + int(bullet.py)

        for t_px, t_py in bullet.trail:
            try:
                stdscr.addstr(offset_y + t_py, offset_x + t_px, "□", curses.A_DIM)
            except curses.error:
                pass

        try:
            stdscr.addstr(screen_y, screen_x, "■", curses.A_BOLD)
        except curses.error:
            pass

    # Header and Status Bar
    try:
        active_ids = sorted(engine.objects.keys())
        header_str = f" Selected: Object [{engine.selected_id}] | Active Objects: {active_ids} "
        stdscr.addnstr(0, 2, header_str, VIEWPORT_WIDTH - 3, curses.A_REVERSE)
        stdscr.addnstr(VIEWPORT_HEIGHT - 1, 2, engine.status_msg, VIEWPORT_WIDTH - 3)
    except curses.error:
        pass

    stdscr.refresh()
    return True

def _draw_centered_lines(stdscr, lines):
    max_y, max_x = stdscr.getmaxyx()
    max_y = min(max_y, VIEWPORT_HEIGHT)
    max_x = min(max_x, VIEWPORT_WIDTH)
    top = max(0, (max_y - len(lines)) // 2)

    for row, (text, color) in enumerate(lines):
        y = top + row
        if y >= max_y:
            break

        left = max(0, (max_x - len(text)) // 2)
        available_width = max_x - left - 1
        if available_width > 0:
            stdscr.addnstr(y, left, text, available_width, color)

def render_win_screen(stdscr, playtime):
    stdscr.erase()
    green = curses.color_pair(4) | curses.A_BOLD
    yellow = curses.color_pair(2) | curses.A_BOLD
    plain = curses.color_pair(1)

    lines = (
        [(line, green) for line in WIN_TEXT]
        + [
            ("", plain),
            ("!  You are the greatest thief  !", yellow),
            ("", plain),
            ("[Q] Quit", plain),
            ("[Enter] Restart Game", plain),
            ("", plain),
            (f"Playtime: {playtime:.2f} seconds", plain),
        ]
    )
    _draw_centered_lines(stdscr, lines)
    stdscr.refresh()

def render_lose_screen(stdscr):
    stdscr.erase()
    red = curses.color_pair(3) | curses.A_BOLD
    yellow = curses.color_pair(2) | curses.A_BOLD
    plain = curses.color_pair(1)

    lines = (
        [(line, red) for line in LOSE_TEXT]
        + [
            ("", plain),
            ("! You have been defeated !", yellow),
            ("", plain),
            ("[Q] Quit", plain),
            ("[Enter] Restart Level", plain),
        ]
    )
    _draw_centered_lines(stdscr, lines)
    stdscr.refresh()
