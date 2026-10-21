import curses
from curses.textpad import rectangle
from constants import CANVAS_WIDTH, CANVAS_HEIGHT, CELL_WIDTH, CELL_HEIGHT, COLOR_MAP


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

def render_frame(stdscr, engine, color_pairs):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    req_width = CANVAS_WIDTH + 6
    req_height = CANVAS_HEIGHT + 6

    # Terminal size check
    if max_y < req_height or max_x < req_width:
        try:
            stdscr.addstr(
                0, 0,
                f"Terminal window too small!\n"
                f"Current: {max_x}x{max_y} | Required: {req_width}x{req_height}\n"
                f"Please enlarge your terminal or press 'Q' to exit."
            )
        except curses.error:
            pass
        stdscr.refresh()
        return False  # Signals window too small

    offset_y = 2
    offset_x = 2

    rectangle(stdscr, 1, 0, 23, 75)

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

            if pos == 10 and obj.object_type.is_movable:
                val = inst_id
            elif pos == 9 and obj.object_type.is_movable:
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
        base_screen_x = offset_x + bullet.x * CELL_WIDTH
        base_screen_y = offset_y + bullet.y * CELL_HEIGHT

        screen_x = base_screen_x + 2
        screen_y = base_screen_y + 1

        try:
            stdscr.addstr(screen_y, screen_x, "*", curses.A_BOLD)
        except curses.error:
            pass

    # Header and Status Bar
    try:
        active_ids = sorted(engine.objects.keys())
        header_str = f" Selected: Object [{engine.selected_id}] | Active Objects: {active_ids} "
        stdscr.addstr(0, 2, header_str[:max_x - 3], curses.A_REVERSE)
        stdscr.addstr(CANVAS_HEIGHT + 4, 2, engine.status_msg[:max_x - 3])
    except curses.error:
        pass

    stdscr.refresh()
    return True