import curses
from engine import GameEngine
from renderer import init_colors, render_frame, render_win_screen, render_lose_screen, rectangle

# IMPORTANT. WATCH.
# https://www.youtube.com/watch?v=dQw4w9WgXcQ
#DID I SERIOUSLY GET RICKROLLED IN THR BIG 26

# TO-DO:
# 1. Make the boxes' json file load (done)
# 2. Add Shooting Mechanisms - Ethan
# 3. Separate files for constants, assets, and main game logic
# 4. Add Mirrors and Gun objects and Target. (done)
# 5. Add rotation for mirrors and gun - Chen

# FEATURES
# Every object has is_fragile tag   
# Every object has is_movable tag   
# Every object has color tag
# Every object has a type tag
# Every object has a zone tag, that object can only move in specific zone


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    color_pairs = init_colors()

    engine = GameEngine()
    engine.load_assets()
    engine.load_level(1)

    stdscr.timeout(50)

    while True:
        # Render the frame, check if terminal is too small
        success = render_frame(stdscr, engine, color_pairs)
        if not success:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            continue

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