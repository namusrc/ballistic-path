import curses
from curses.textpad import rectangle
from turtle import left
from constants import CANVAS_WIDTH, CANVAS_HEIGHT, CELL_WIDTH, CELL_HEIGHT, COLOR_MAP
import time 

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

    # Terminal size check, freeze the game if the terminal size is too small.
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
        stdscr.addstr(0, 2, header_str[:max_x - 3], curses.A_REVERSE)
        stdscr.addstr(CANVAS_HEIGHT + 4, 2, engine.status_msg[:max_x - 3])
    except curses.error:
        pass

    stdscr.refresh()
    return True

def render_win_screen(stdscr,total_seconds):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    green = curses.color_pair(4) | curses.A_BOLD #4 representss green
    yellow = curses.color_pair(2) | curses.A_BOLD #2 represents yellow

    lines = [
        ("█   █   ███   █   █    █   █  ███  █   █", green),
        (" █ █   █   █  █   █    █   █   █   ██  █", green),
        ("  █    █   █  █   █    █ █ █   █   █ █ █", green),
        ("  █    █   █  █   █    ██ ██   █   █  ██", green),
        ("  █     ███    ███     █   █  ███  █   █", green),
        ("", 0),
        ("!  All targets destroyed  !", yellow),
        ("", 0),
        ("[Q] Quit", 0),
    ]

    top_margin = (max_y - len(lines)) // 2
    left_margin = (max_x - 40) // 2 


    stdscr.nodelay(True)
    start_time = time.time()
    
    #countdown
    while True:
        #calculate time passed and time remaining
        elapsed_time = time.time() - start_time
        remaining_time = total_seconds - int(elapsed_time)   
        
        #Break to loop if times up
        if remaining_time <= 0:
            break     
        
        # Refresh the screen with remaining time and instructions
        stdscr.clear()
        for i, (line, color) in enumerate(lines):
            stdscr.addstr(top_margin + i, left_margin, line, color)
        stdscr.addstr(top_margin+10, left_margin, f"Window will be closed in: {remaining_time} seconds", curses.A_BOLD)
        stdscr.refresh()

        
        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):  # Q or ESC
            break
        time.sleep(0.1)
        

    
 