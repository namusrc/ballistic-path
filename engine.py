import random
from pathlib import Path
import json
from constants import GRID_COLS, GRID_ROWS, CELL_HEIGHT, CELL_WIDTH
from models import ObjectType, GameObjectInstance, Bullet

class GameEngine:
    """For checking collisions, movings, and managing game state."""

    def __init__(self):
        self.object_types = {}    # type_id -> ObjectType
        self.objects = {}         # instance_id -> GameObjectInstance
        self.selected_id = None
        self.bullets = []        # List of Bullet instances
        self.status_msg = "Use 0-9 to select object | WASD to move | F to shoot | Q to quit"

    def load_assets(self):
        objects_dir = Path("assets/objects")

        # Load Object Designs
        for json_file in objects_dir.glob("*.json"):
            try:
                obj_type = ObjectType.load_from_file(json_file)
                self.object_types[obj_type.type_id] = obj_type
            except Exception as e:
                print(f"Error loading object template {json_file}: {e}")


    def load_level(self, level=1):
        level_file = Path(f"assets/levels/level_{level}.json")

        # Load Level Data
        if not level_file.exists():
            raise FileNotFoundError(f"Level file not found at {level_file}")

        self.objects.clear()
        self.bullets.clear()
        self.selected_id = None
        
        level_data = json.loads(level_file.read_text(encoding="utf-8"))

        self.level_id = level_data.get("level_id")
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

    def debug(self):
        self.load_level(0)

    def load_next_level(self):
        next_level = self.level_id + 1
        try:
            self.load_level(next_level)
        except FileNotFoundError:
            pass

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

        # Let's make the gun rotatable and let other objects in the outer ring.
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

        if gun.object_type.type_id != "gun":
            self.status_msg = f"Selected object [{self.selected_id}] is not a gun"
            return

        # Because each pixel is 6x3 we need to move 2 pixels per tick when travelling horizontally
        directions = {
            "north": (0, -1),
            "east": (2, 0),
            "south": (0, 1),
            "west": (-2, 0)
        }

        if gun.angle not in directions:
            self.status_msg = f"Gun [{self.selected_id}] has invalid angle {gun.angle}"
            return

        dx, dy = directions[gun.angle]

        # To make bullet spawn at the edge of gun, not center.
        barrel_offsets = {
            "north": (0, - (CELL_HEIGHT // 2)),
            "east":  (CELL_WIDTH // 2, 0),
            "south": (0, CELL_HEIGHT // 2),
            "west":  (- (CELL_WIDTH // 2), 0)
        }

        ox, oy = barrel_offsets.get(gun.angle, (0, 0))
        
        start_px = (gun.grid_x * CELL_WIDTH) + (CELL_WIDTH // 2) + ox
        start_py = (gun.grid_y * CELL_HEIGHT) + (CELL_HEIGHT // 2) + oy

        self.bullets.append(Bullet(px=start_px, py=start_py, dx=dx, dy=dy))
        self.status_msg = f"Shot fired from object [{self.selected_id}]"

    def update_bullets(self):
        remaining = []
        directions = {
            "north": (0, -1),
            "east": (2, 0),
            "south": (0, 1),
            "west": (-2, 0)
        }
        for bullet in self.bullets:

            # Bullet trail on/off
            
            bullet.trail.append((bullet.px, bullet.py)) # For trail, saving last 3 bulet posiotn
        
            if len(bullet.trail) > 3:
                bullet.trail = bullet.trail[-3:]
            
            bullet.px += bullet.dx
            bullet.py += bullet.dy

            current_grid_x = int(bullet.px // CELL_WIDTH)
            current_grid_y = int(bullet.py // CELL_HEIGHT)

            if not (0 <= current_grid_x < GRID_COLS and 0 <= current_grid_y < GRID_ROWS):
                self.status_msg = f"[BLOCKED] Hit grid boundary at ({current_grid_x}, {current_grid_y}"
                continue

            hit_obstacle = False
            
            for other_id, other_obj in self.objects.items():
                centerofobj_x=[other_obj.grid_x*CELL_WIDTH+2,other_obj.grid_x*CELL_WIDTH+3]
                centerofobj_y=[other_obj.grid_y*CELL_HEIGHT+1]
                #the bullet only change direction when it hit the "center" of mirror
                #centerofobj_x and centerofobj_y are the possible two coordinates of "center of mirror"
                if (bullet.px in centerofobj_x) and (bullet.py in centerofobj_y):
                    if other_obj.object_type.is_mirror:
                        original_direction=(bullet.dx,bullet.dy)      
                        if other_obj.angle in ("north", "south"):
                            reflection_map = {
                                directions["north"]: directions["west"],
                                directions["west"]: directions["north"],
                                directions["south"]: directions["east"],
                                directions["east"]: directions["south"],
                            }                                                  
                        elif other_obj.angle in ("west", "east"):
                            reflection_map = {
                                        directions["north"]: directions["east"],
                                        directions["east"]: directions["north"],
                                        directions["south"]: directions["west"],
                                        directions["west"]: directions["south"],
                                    }
                        else:
                                reflection_map = {}
                                
                        if original_direction in reflection_map:
                            bullet.dx, bullet.dy = reflection_map[original_direction]

                    elif other_obj.object_type.is_fragile:
                        pass
                    
                    elif not other_obj.object_type.is_fragile:
                        self.status_msg = f"[BLOCKED] Cell ({current_grid_x}, {current_grid_y}) occupied by Object [{other_id}]"
                        hit_obstacle = True
                        break  # Stop checking other objects

            if hit_obstacle:
                continue
                    
            remaining.append(bullet)

        self.bullets = remaining