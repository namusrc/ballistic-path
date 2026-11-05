import curses
from engine import GameEngine
from renderer import (
    init_colors,
    render_frame,
    render_lose_screen,
    render_resize_message,
    render_win_screen,
)
from constants import GAME_SPEED, VIEWPORT_HEIGHT, VIEWPORT_WIDTH
import time

# IMPORTANT. WATCH.
# https://www.youtube.com/watch?v=oHg5SJYRHA0


INTRO_DIALOGUE = (
    "After hours of thinking, I literally have no idea how to make a bank robbery story without making it sound too cliche.",
    "What is wrong with my life?",
    "I should've known that we needed a story in this project. I should have been more careful.",
    "Can I get a good grade for this course?",
    "What happens if I can't even graduate? How will I make a living? How will I survive? How will I pay for my rent?",
    "The answer is simple. I will just have to rob a bank.",
    "Practice makes perfet. Let's practice robbing a bank!"
    
)

LEVEL_DIALOGUES = {
    1: (
        "That shot actually worked.",
        "Maybe this could be my profession.",
        "Let's try something different"
    ),
    2: (
        "Another target down. It's just like studying maths",
        "Except that it actually gives you money",
    ),
    3: (
        "Almost there. I'm almost ready to rob HSBC",
        "I'll be rich.",
    ),
}


def _draw_centered(stdscr, y, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()
    max_y = min(max_y, VIEWPORT_HEIGHT)
    max_x = min(max_x, VIEWPORT_WIDTH)
    if 0 <= y < max_y and max_x > 1:
        x = max(0, (max_x - len(text)) // 2)
        try:
            stdscr.addnstr(y, x, text, max_x - x - 1, attr)
        except curses.error:
            pass


def run_dialogue(stdscr, lines, title="Bank Robbery"):
    line_index = 0
    visible_chars = 0
    elapsed_typing = 0.0
    last_update = time.monotonic()
    character_interval = 0.035
    stdscr.timeout(50 * GAME_SPEED)

    while line_index < len(lines):
        now = time.monotonic()
        max_y, max_x = stdscr.getmaxyx()
        if max_y < VIEWPORT_HEIGHT or max_x < VIEWPORT_WIDTH:
            render_resize_message(stdscr)
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):
                return False
            last_update = time.monotonic()
            continue

        if visible_chars < len(lines[line_index]):
            elapsed_typing += now - last_update
            chars_to_add = int(elapsed_typing / character_interval)
            if chars_to_add:
                visible_chars = min(
                    len(lines[line_index]),
                    visible_chars + chars_to_add,
                )
                elapsed_typing -= chars_to_add * character_interval
        last_update = now

        stdscr.erase()
        max_y = min(max_y, VIEWPORT_HEIGHT)
        _draw_centered(stdscr, max_y // 2 - 3, title, curses.A_BOLD)
        _draw_centered(stdscr, max_y // 2 - 1, lines[line_index][:visible_chars])
        _draw_centered(stdscr, max_y // 2 + 2, f"{line_index + 1} / {len(lines)}")
        if visible_chars == len(lines[line_index]):
            prompt = "[Enter] Next"
        else:
            prompt = "[Enter] Finish line"
        _draw_centered(stdscr, max_y // 2 + 4, f"{prompt}    [Q] Quit", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return False
        if key in (10, 13, curses.KEY_ENTER):
            if visible_chars < len(lines[line_index]):
                visible_chars = len(lines[line_index])
            else:
                line_index += 1
                visible_chars = 0
                elapsed_typing = 0.0
            last_update = time.monotonic()

    return True


def run_intro_dialogue(stdscr):
    return run_dialogue(stdscr, INTRO_DIALOGUE)


def main(stdscr):

    curses.curs_set(0)
    stdscr.keypad(True)
    color_pairs = init_colors()

    if not run_intro_dialogue(stdscr):
        return

    engine = GameEngine()
    engine.load_assets()
    engine.load_level()
    
    stdscr.timeout(50 * GAME_SPEED)
    start_time = time.time()

    while True:
        
        # Render the frame, check if terminal is too small
        success = render_frame(stdscr, engine, color_pairs)
        if not success:
            stdscr.timeout(50 * GAME_SPEED)
            key = stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            continue
        if engine.state == "WIN":
            playtime = time.time() - start_time
            stdscr.timeout(-1)
            render_win_screen(stdscr, playtime)
            if key in (ord('q'), ord('Q'), 27):
                    return
            
        if engine.state == "LOSE":
            curses.beep()
            stdscr.timeout(50 * GAME_SPEED)

            while engine.state == "LOSE":
                max_y, max_x = stdscr.getmaxyx()
                if max_y < VIEWPORT_HEIGHT or max_x < VIEWPORT_WIDTH:
                    render_resize_message(stdscr)
                else:
                    render_lose_screen(stdscr)
                key = stdscr.getch()
                if key in (ord('q'), ord('Q'), 27):
                    return
                elif key in (10, 13, curses.KEY_ENTER):
                    if max_y < VIEWPORT_HEIGHT or max_x < VIEWPORT_WIDTH:
                        continue
                    engine.load_level(engine.level_id)  # Reload the current level
                    engine.state = "RUNNING"
                    stdscr.timeout(50 * GAME_SPEED)
                    break

        # Input Processing
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):  # Q or ESC
            break
        elif key in (ord('w'), ord('W'), curses.KEY_UP):
            engine.try_move(0, -1)
        elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
            engine.try_move(0, 1)
        elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
            engine.try_move(-1, 0)
        elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            engine.try_move(1, 0)
        elif key in (ord('r'), ord('R')):
            engine.try_rotate()
        elif key in (ord('f'), ord('F')):
            engine.shoot()
        elif key == ord('?'):
            engine.debug()
        elif key == ord('n'): # Debug purpose: Skip to next level. Delete before releasing.
            engine.state = "LEVEL_COMPLETE"
        elif key in (10, 13, curses.KEY_ENTER):
            if engine.state == "LEVEL_COMPLETE":
                dialogue = LEVEL_DIALOGUES.get(engine.level_id)
                if dialogue and not run_dialogue(stdscr, dialogue, "BETWEEN LEVELS"):
                    return
                engine.load_next_level()
                stdscr.timeout(50 * GAME_SPEED)
        else:
            try:
                char_key = chr(key)
                if char_key in engine.objects:
                    engine.selected_id = char_key
                    engine.status_msg = f"Selected Object [{char_key}]"
            except ValueError:
                pass

        engine.update_bullets()

if __name__ == "__main__":
    curses.wrapper(main)