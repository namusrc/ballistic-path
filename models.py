import json
from dataclasses import dataclass
from pathlib import Path


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
    is_rotatable: bool

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
        is_rotatable = data.get("is_rotatable", True)
        return cls(type_id, initial_angle, name, design, designs, is_movable, is_fragile, is_rotatable)

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