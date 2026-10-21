import curses
import json
import random
from pathlib import Path
from curses.textpad import rectangle
from dataclasses import dataclass

# IMPORTANT. WATCH.
# https://www.youtube.com/watch?v=dQw4w9WgXcQ

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

# Grid and Aspect Ratio Configuration, will be moved to constants.py
# 12 horizontally and 7 vertically
GRID_COLS = 12
GRID_ROWS = 7

# Terminal character dimensions, each grid cell is represented as a 6x3 characters,
#   because each letter is twice as tall as it is wide in terminal.
CELL_WIDTH = 6
CELL_HEIGHT = 3

CANVAS_WIDTH = GRID_COLS * CELL_WIDTH   # 72 terminal characters
CANVAS_HEIGHT = GRID_ROWS * CELL_HEIGHT # 21 terminal lines

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


@dataclass # Use dataclass library to simpify class init
class ObjectType:
    """Represents a 3x3 object design template loaded from assets/objects/*.json"""
    type_id: int  # type_id of object
    initial_angle: str
    name: str
    design: dict
    designs: dict  # Dict with keys "1" through "9". 0 is not used for now
    is_movable: bool
    is_fragile: bool

    @classmethod
    def load_from_file(cls, filepath):
        data = json.loads(filepath.read_text(encoding="utf-8"))

        type_id = data.get("type_id", Path(filepath).stem)
        initial_angle = data.get("initial_angle", "random")
        name = data.get("name", None )
        design = data.get("design", {})
        designs = data.get("designs", {}) # specially for rotatable objects
        is_movable = data.get("is_movable", False)
        is_fragile = data.get("is_fragile", False)
        return cls(type_id, initial_angle, name, design, designs, is_movable, is_fragile)

@dataclass
class GameObjectInstance:
    """Represent active object on the grid."""
    instance_id: str    # Selection ID (like '1', '2')
    object_type: str    # ObjectType reference
    grid_x: int # Grid X (0..11)
    grid_y: int # Grid Y (0..6)
    angle: str

@dataclass
class Bullet:
    x: int
    y: int
    dx: int
    dy: int


class GameEngine:
    """For checking collisions, movings, and managing game state."""

    def __init__(self):
        self.object_types = {}    # type_id -> ObjectType
        self.objects = {}         # instance_id -> GameObjectInstance
        self.selected_id = None
        self.bullets = []        # List of Bullet instances
        self.status_msg = "Use 0-9 to select object | WASD to move | F to sho12f12ot11 1| Q to quit"

    def load_assets_and_level(self):
        objects_dir = Path("assets/objects")
        level_file = Path("assets/levels/level_1.json")

        # Load Object Designs
        for json_file in objects_dir.glob("*.json"):
            try:
                obj_type = ObjectType.load_from_file(json_file)
                self.object_types[obj_type.type_id] = obj_type
            except Exception as e:
                print(f"Error loading object template {json_file}: {e}")



        # Load Level Data
        if not level_file.exists():
            raise FileNotFoundError(f"Level file not found at {level_file}")
        
        level_data = json.loads(level_file.read_text(encoding="utf-8"))


        for item in level_data.get("objects", []):
            instance_id = str(item["id"])
            type_id = item["type"]
            grid_x = item["x"]
            grid_y = item["y"]

            if type_id in self.object_types:
                obj_type = self.object_types[type_id]

                angle = item.get("initial_angle", obj_type.initial_angle)

                # Random angle for rotatable objects, if not specified in level file
                if not angle or angle == "random":
                    angle = random.choice(["north", "east", "south", "west"])  

                obj_instance = GameObjectInstance(
                    instance_id = instance_id,
                    object_type = self.object_types[type_id],
                    grid_x = grid_x,
                    grid_y = grid_y,
                    angle = angle
                )
                self.objects[instance_id] = obj_instance

        # Auto-selection of the first available object
        if self.objects:
            self.selected_id = sorted(self.objects.keys())[0]

    def try_move(self, dx, dy):
        if self.bullets:
            self.status_msg = "Cannot move while bullet is in motion"
            return
        
        if not self.selected_id or self.selected_id not in self.objects:
            self.status_msg = "No object selected!"
            return
        
        selected_object = self.objects[self.selected_id]
        new_x = selected_object.grid_x + dx
        new_y = selected_object.grid_y + dy


        if not selected_object.object_type.is_movable:
            self.status_msg = f"[BLOCKED] Object [{self.selected_id}] is not movable"
            return



        # Object-to-Boundary Collision Check (12x7 Grid)
        if selected_object.object_type.type_id == "gun":
            if (0 < new_x < GRID_COLS-1 and 0 < new_y < GRID_ROWS-1) or \
                (new_x < 0 or new_x > GRID_COLS-1 or new_y < 0 or new_y > GRID_ROWS-1):
                self.status_msg = f"[BLOCKED] Hit grid boundary at ({new_x}, {new_y})"
                return
            
        elif selected_object.object_type.type_id != "gun":
            if (new_x < 0 or new_x > GRID_COLS-1 or new_y < 0 or new_y > GRID_ROWS-1):
                self.status_msg = f"[BLOCKED] Hit grid boundary at ({new_x}, {new_y})"
                return

        # Let's make the gun rotatable.
        """
        else: # gun can only move in the outer ring
            if new_x == 0:
                selected_object.angle = "south"
            if new_y == 6:
                selected_object.angle = "east"
            if new_x == 11:
                selected_object.angle = "west"
            if new_y == 0:
                selected_object.angle = "north"
        """

        
        # Object-to-Object Collision Check
        for other_id, other_obj in self.objects.items():
            if other_id != self.selected_id:
                if other_obj.grid_x == new_x and other_obj.grid_y == new_y:
                    self.status_msg = f"[BLOCKED] Cell ({new_x}, {new_y}) occupied by Object [{other_id}]"
                    return

        # Horray Move accepted
        selected_object.grid_x = new_x
        selected_object.grid_y = new_y
        self.status_msg = f"Moved Object [{self.selected_id}] to Grid ({new_x}, {new_y})"

    # Clockwise rotation
    def try_rotate(self):
        if self.bullets:
            self.status_msg = "Cannot rotate while bullet is in motion"
            return

        if not self.selected_id or self.selected_id not in self.objects:
            self.status_msg = "No object selected"
            return
        
        selected_object = self.objects[self.selected_id]
        if selected_object.angle == "north":
            self.status_msg = f"Rotated Object [{self.selected_id}]"
            selected_object.angle = "east"
        elif selected_object.angle == "east":
            self.status_msg = f"Rotated Object [{self.selected_id}]"
            selected_object.angle = "south"
        elif selected_object.angle == "south":
            self.status_msg = f"Rotated Object [{self.selected_id}]"
            selected_object.angle = "west"
        elif selected_object.angle == "west":
            self.status_msg = f"Rotated Object [{self.selected_id}]"
            selected_object.angle = "north"
        else:
            pass

    def shoot(self):
        if self.bullets:
            self.status_msg = "Bullet already in motion"
            return

        if self.selected_id not in self.objects:
            self.status_msg = "No object selected"
            return

        gun = self.objects[self.selected_id]

        if str(gun.object_type.type_id) != "gun":
            self.status_msg = f"Selected object [{self.selected_id}] is not a gun"
            return

        directions = {
            "north": (0, -1),
            "east": (1, 0),
            "south": (0, 1),
            "west": (-1, 0)
        }

        if gun.angle not in directions:
            self.status_msg = f"Gun [{self.selected_id}] has invalid angle {gun.angle}"
            return

        dx, dy = directions[gun.angle]

        self.bullets.append(Bullet(x=gun.grid_x, y=gun.grid_y, dx=dx, dy=dy))

    def update_bullets(self):
        remaining = []

        for bullet in self.bullets:
            next_x = bullet.x + bullet.dx
            next_y = bullet.y + bullet.dy

            if not 0 <= next_x < GRID_COLS and 0 <= next_y < GRID_ROWS:
                self.status_msg = f"[BLOCKED] Hit grid boundary at ({next_x}, {next_y})"
                continue

            bullet.x = next_x
            bullet.y = next_y
            remaining.append(bullet)

        self.bullets = remaining

            
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


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    color_pairs = init_colors()

    engine = GameEngine()
    engine.load_assets_and_level()

    stdscr.timeout(150)

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        # Minimum terminal size check, not specifically 80*24
        req_width = CANVAS_WIDTH + 6   # ~72 characters
        req_height = CANVAS_HEIGHT + 6 # ~27 lines

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
            key = stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                exit()
            continue

        offset_y = 2
        offset_x = 2

        rectangle(stdscr, 1, 0, 23, 75)

        # Render Object Instances
        for inst_id, obj in engine.objects.items():
            base_screen_x = offset_x + (obj.grid_x * CELL_WIDTH)
            base_screen_y = offset_y + (obj.grid_y * CELL_HEIGHT)

            if obj.object_type.designs:
                design = obj.object_type.designs.get(str(obj.angle))
            else :
                design = obj.object_type.design
            is_selected = (inst_id == engine.selected_id)
            attr = curses.A_BOLD if is_selected else curses.A_DIM

            # Draw 6x3 layout
            for pos in range(1, 19): #3 rows and 6 columns make a block, 18 characters in total
                sub_r = (pos - 1) // 6
                sub_c = (pos - 1) % 6

                # Center position (10) dynamically displays the instance ID
                if pos == 10 and obj.object_type.is_movable:
                    val = inst_id
                elif pos == 9 and obj.object_type.is_movable:
                    val = " "
                else:
                    val = design.get(str(pos), " ")[0]   #get the color of the character, val is string
                    

                screen_y = base_screen_y + sub_r
                screen_x = base_screen_x + sub_c  

                if val in color_pairs:
                    str_to_draw = design.get(str(pos), " ")[1] #get the string to draw
                    color_attr = color_pairs[val] | attr
                else:
                    str_to_draw = f"{val}"
                    color_attr = curses.color_pair(1) | attr

                try:
                    stdscr.addstr(screen_y, screen_x, str_to_draw, color_attr)
                except curses.error:
                    pass

        # render bullets
        for bullet in engine.bullets:
            base_screen_x = offset_x + bullet.x * CELL_WIDTH
            base_screen_y = offset_y + bullet.y * CELL_HEIGHT

            screen_x = base_screen_x + 2
            screen_y = base_screen_y + 1

        try:
            stdscr.addstr(
                screen_y,
                screen_x,
                "*",
                curses.A_BLINK
            )
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
        else:
            # Check key press for object selection.....
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