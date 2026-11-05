import curses
from engine import GameEngine
from renderer import init_colors, render_frame, render_win_screen, render_lose_screen
from constants import GAME_SPEED
import time

# IMPORTANT. WATCH.
# https://www.youtube.com/watch?v=oHg5SJYRHA0


INTRO_DIALOGUE = (
    "Ah-ee-ah-ee-ah! Wah-wah-wah!",
    "\"Looks like I'm a shotgunner of the West in 1863!\"",
    "You've bet all ya money on that a puzzle your friend gave you would be EZ.",
    "You have one shot. Make it count.",
    "Bum Bum Dara Bum Bum Dara Bum Bum Dara",
)


def _draw_centered(stdscr, y, text, attr=0):
    max_y, max_x = stdscr.getmaxyx()
    if 0 <= y < max_y and max_x > 1:
        x = max(0, (max_x - len(text)) // 2)
        stdscr.addnstr(y, x, text, max_x - x - 1, attr)


def run_intro_dialogue(stdscr):
    line_index = 0
    visible_chars = 0
    elapsed_typing = 0.0
    last_update = time.monotonic()
    character_interval = 0.035
    stdscr.timeout(50 * GAME_SPEED)

    while line_index < len(INTRO_DIALOGUE):
        now = time.monotonic()
        if visible_chars < len(INTRO_DIALOGUE[line_index]):
            elapsed_typing += now - last_update
            chars_to_add = int(elapsed_typing / character_interval)
            if chars_to_add:
                visible_chars = min(
                    len(INTRO_DIALOGUE[line_index]),
                    visible_chars + chars_to_add,
                )
                elapsed_typing -= chars_to_add * character_interval
        last_update = now

        stdscr.erase()
        max_y, _ = stdscr.getmaxyx()
        _draw_centered(stdscr, max_y // 2 - 3, "BALLISTIC PATH", curses.A_BOLD)
        _draw_centered(stdscr, max_y // 2 - 1, INTRO_DIALOGUE[line_index][:visible_chars])
        _draw_centered(stdscr, max_y // 2 + 2, f"{line_index + 1} / {len(INTRO_DIALOGUE)}")
        if visible_chars == len(INTRO_DIALOGUE[line_index]):
            prompt = "[Enter] Next"
        else:
            prompt = "[Enter] Finish line"
        _draw_centered(stdscr, max_y // 2 + 4, f"{prompt}    [Q] Quit", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return False
        if key in (10, 13, curses.KEY_ENTER):
            if visible_chars < len(INTRO_DIALOGUE[line_index]):
                visible_chars = len(INTRO_DIALOGUE[line_index])
            else:
                line_index += 1
                visible_chars = 0
                elapsed_typing = 0.0
            last_update = time.monotonic()

    return True


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
            stdscr.timeout(-1)
            render_lose_screen(stdscr)

            while engine.state == "LOSE":
                key = stdscr.getch()
                if key in (ord('q'), ord('Q'), 27):
                    return
                elif key in (10, 13, curses.KEY_ENTER):
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
                engine.load_next_level()
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