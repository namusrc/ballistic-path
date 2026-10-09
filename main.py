import curses
import json
from pathlib import Path


# TO-DO:
# 1. Somehow make the boxes' json file fucking load
# 2. Shooting Mechanisms
# 3. Separate files for constants, assets, and main game logic
# 4. Add Mirrors and Gun objects and Target.



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


class ObjectType:
    """Represents a 3x3 object design template loaded from assets/objects/*.json"""
    def __init__(self, type_id, name, design):
        self.type_id = type_id
        self.name = name
        self.design = design  # Dict with keys "1" through "9". 0 is not used for now

    @classmethod
    def load_from_file(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        type_id = data.get("type_id", Path(filepath).stem)
        name = data.get("name", type_id)
        design = data.get("design", {})
        return cls(type_id, name, design)


class GameObjectInstance:
    """Represent active object on the grid."""
    def __init__(self, instance_id, object_type, grid_x, grid_y):
        self.instance_id = str(instance_id)  # Selection ID (like '1', '2')
        self.object_type = object_type        # ObjectType reference
        self.grid_x = grid_x                  # Grid X (0..11)
        self.grid_y = grid_y                  # Grid Y (0..6)


class GameEngine:
    """For checking collisions, movings, and managing game state."""
    def __init__(self):
        self.object_types = {}    # type_id -> ObjectType
        self.objects = {}         # instance_id -> GameObjectInstance
        self.selected_id = None
        self.status_msg = "Use 0-9 to select object | WASD to move | Q to quit"

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

        # Load Level Data (for now only level 1, for some reason I failed to do any more levels, why??)
        if not level_file.exists():
            raise FileNotFoundError(f"Level file not found at {level_file}")

        with open(level_file, 'r', encoding='utf-8') as f:
            level_data = json.load(f)

        for item in level_data.get("objects", []):
            instance_id = str(item["id"])
            type_id = item["type"]
            grid_x = item["x"]
            grid_y = item["y"]

            if type_id in self.object_types:
                obj_instance = GameObjectInstance(
                    instance_id=instance_id,
                    object_type=self.object_types[type_id],
                    grid_x=grid_x,
                    grid_y=grid_y
                )
                self.objects[instance_id] = obj_instance

        # Auto-selection of the first available object
        # If someone read this and is wondering why I did not just select
        #   the first object in the list, it is because I wanted to sort the
        #   keys so that the selection order is always consistent
        #   (e.g., '1', '2', '3', ...), regardless of how they are defined in the JSON file.
        if self.objects:
            self.selected_id = sorted(self.objects.keys())[0]

    def try_move(self, dx, dy):
        if not self.selected_id or self.selected_id not in self.objects:
            self.status_msg = "No object selected!"
            return

        target = self.objects[self.selected_id]
        new_x = target.grid_x + dx
        new_y = target.grid_y + dy

        # Object-to-Boundary Collision Check (12x7 Grid)
        if not (0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS):
            self.status_msg = f"[BLOCKED] Hit grid boundary at ({new_x}, {new_y})"
            return

        # Object-to-Object Collision Check
        for other_id, other_obj in self.objects.items():
            if other_id != self.selected_id:
                if other_obj.grid_x == new_x and other_obj.grid_y == new_y:
                    self.status_msg = f"[BLOCKED] Cell ({new_x}, {new_y}) occupied by Object [{other_id}]"
                    return

        # Horray Move accepted
        target.grid_x = new_x
        target.grid_y = new_y
        self.status_msg = f"Moved Object [{self.selected_id}] to Grid ({new_x}, {new_y})"


# This is so simple why the fuck does it not work??????
def ensure_sample_assets_exist(objects_dir: Path, level_file: Path):
    """Generates default asset directory and JSON files if they do not exist."""
    objects_dir.mkdir(parents=True, exist_ok=True)
    level_file.parent.mkdir(parents=True, exist_ok=True)

    yellow_box_path = objects_dir / "yellow_box.json"
    if not yellow_box_path.exists():
        yellow_box_data = {
            "type_id": "yellow_box",
            "name": "Yellow Box",
            "design": {
                "1": "yellow", "2": "yellow", "3": "yellow",
                "4": "yellow", "5": "id",     "6": "yellow",
                "7": "yellow", "8": "yellow", "9": "yellow"
            }
        }
        with open(yellow_box_path, 'w', encoding='utf-8') as f:
            json.dump(yellow_box_data, f, indent=2)

    red_box_path = objects_dir / "red_box.json"
    if not red_box_path.exists():
        red_box_data = {
            "type_id": "box",
            "name": "Red Box",
            "design": {
                "1": "red", "2": "red", "3": "red",
                "4": "red", "5": "id",  "6": "red",
                "7": "red", "8": "red", "9": "red"
            }
        }
        with open(red_box_path, 'w', encoding='utf-8') as f:
            json.dump(red_box_data, f, indent=2)

    if not level_file.exists():
        level_data = {
            "level_id": 1,
            "name": "Level 1",
            "objects": [
                {"id": "1", "type": "box", "x": 2, "y": 2},
                {"id": "2", "type": "donut", "x": 10, "y": 3},
                {"id": "3", "type": "donut", "x": 16, "y": 5}
            ]
        }
        with open(level_file, 'w', encoding='utf-8') as f:
            json.dump(level_data, f, indent=2)


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
                break
            continue

        offset_y = 2
        offset_x = 2

        # Draw Canvas Outer Border, could use curses.box() or curses.rectangle() but that didn't work
        for y in range(CANVAS_HEIGHT + 2):
            for x in range(CANVAS_WIDTH + 2):
                if y == 0 or y == CANVAS_HEIGHT + 1 or x == 0 or x == CANVAS_WIDTH + 1:
                    try:
                        stdscr.addch(offset_y + y - 1, offset_x + x - 1, '█', curses.color_pair(1))
                    except curses.error:
                        pass

        # Render Object Instances
        for inst_id, obj in engine.objects.items():
            base_screen_x = offset_x + (obj.grid_x * CELL_WIDTH)
            base_screen_y = offset_y + (obj.grid_y * CELL_HEIGHT)

            design = obj.object_type.design
            is_selected = (inst_id == engine.selected_id)
            attr = curses.A_BOLD if is_selected else curses.A_NORMAL

            # Draw 3x3 layout
            for pos in range(1, 10):
                sub_r = (pos - 1) // 3
                sub_c = (pos - 1) % 3

                # Center position (5) dynamically displays the instance ID
                if pos == 5:
                    val = inst_id
                else:
                    val = str(design.get(str(pos), " "))

                screen_y = base_screen_y + sub_r
                screen_x = base_screen_x + (sub_c * 2)  # Step by 2 horizontal chars

                if val in color_pairs:
                    str_to_draw = '██'
                    color_attr = color_pairs[val] | attr
                else:
                    if len(val) == 1:
                        str_to_draw = f" {val}"
                    else:
                        str_to_draw = val[:2].ljust(2)
                    color_attr = curses.color_pair(1) | attr

                try:
                    stdscr.addstr(screen_y, screen_x, str_to_draw, color_attr)
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
        else:
            # Check key press for object selection.....
            try:
                char_key = chr(key)
                if char_key in engine.objects:
                    engine.selected_id = char_key
                    engine.status_msg = f"Selected Object [{char_key}]"
            except ValueError:
                pass


if __name__ == "__main__":
    curses.wrapper(main)