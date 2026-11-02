import curses
from engine import GameEngine
from renderer import init_colors, render_frame, render_win_screen, render_lose_screen, rectangle
from constants import GAME_SPEED
import time

# IMPORTANT. WATCH.
# https://www.youtube.com/watch?v=oHg5SJYRHA0


def main(stdscr):

    curses.curs_set(0)
    stdscr.keypad(True)
    color_pairs = init_colors()

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