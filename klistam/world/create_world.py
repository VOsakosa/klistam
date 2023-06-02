"""
script with terrain information
"""
from datetime import datetime
from typing import Optional, Any
from attrs import define, field
import yaml
import numpy as np
import random
from pathlib import Path
from collections import Counter

from typing_extensions import Self

from klistam.world.mob import Mob


@define(eq=False)
class Field:
    """A single tile in the world."""
    name: str
    walkable: bool = False
    parent: "Field | None" = None
    children: "list[Field] | None" = field(factory=list)  # type: ignore

    def __str__(self):
        return self.name + (f"[{self.parent}]" if self.parent else "")

    @classmethod
    def generate_fields(cls, parent: "Field | None", obj_info: str | dict[str, Any]) -> list["Field"]:
        fields = list()
        if isinstance(obj_info, str):
            fields.append(cls(parent=parent, name=obj_info))
        else:
            assert "name" in obj_info
            walkable = obj_info["walkable"] if "walkable" in obj_info else (parent.walkable if parent else None)
            instance = cls(parent=parent, name=obj_info["name"],
                           walkable=walkable)
            fields.append(instance)
            children = list()
            if "categories" in obj_info:
                for child_info in obj_info["categories"]:
                    children.extend(Field.generate_fields(parent=instance, obj_info=child_info))
            instance.children = children
            fields.extend(children)
        return fields


@define
class Scene:
    """A fixed part of the world that is visible at once and fills the screen."""
    terrain: np.ndarray
    start_coord: tuple[int, int]
    _mobs: list[Mob] = field(factory=list)  # sortedcontainers.SortedKeyList ?

    def get_terrain_file(self, x: int, y: int) -> str:
        the_field: Field = self.terrain[y][x]
        assert the_field
        return the_field.name


@define
class World:
    generator: "WorldGenerator"
    _scenes: dict[tuple[int, int], Scene] = field(factory=dict)

    def get_scene(self, coord: tuple[int, int]) -> Scene:
        if coord not in self._scenes:
            self._scenes[coord] = self.generator.get_terrain(coord)
        return self._scenes[coord]


@define
class WorldGenerator:
    """The entire world of the game."""
    seed: int = 0
    fields: list[Field] = field(factory=list)

    @classmethod
    def generate(cls, seed: Optional[int] = None) -> Self:
        instance = cls(seed or hash(datetime.now()))
        instance.fields = load_field_info()
        return instance

    def get_impact(self, field_type: Field, factor: float) -> dict[Field, float]:
        weight = {f: 0 for f in self.fields}
        weight[field_type] = 1

        def set_weight_down_stream(sub_field, value):
            num_children = len(sub_field.children)
            if num_children == 0:
                weight[sub_field] = value + weight[sub_field]
            else:
                for child in sub_field.children:
                    set_weight_down_stream(child, value / num_children)

        def set_weight_up_stream(sub_field, value):
            set_weight_down_stream(sub_field, value * factor)
            if sub_field.parent:
                set_weight_up_stream(sub_field.parent, value * factor)

        for tfield in self.fields:
            set_weight_down_stream(tfield, 1)

        set_weight_up_stream(field_type, 1)
        norm = sum(weight.values())
        return {key: val / norm for key, val in weight.items()}

    def get_terrain(self, start: tuple[int, int] = (0, 0), height: int = 32, width: int = 32) -> Scene:
        factor = 4 / 5
        random.seed(self.seed)
        terrain = np.empty(shape=(height, width), dtype=Field)
        terrain[0][0] = random.choice(self.fields)

        def get_weight(x, y):
            weights = Counter({key: 0 for key in self.fields})
            for cords in [(x - 1, y - 1), (x - 1, y), (x, y - 1)]:
                if terrain[cords[0]][cords[1]]:
                    weights.update(Counter(self.get_impact(terrain[cords[0]][cords[1]], factor)))

            norm = sum(weights.values())

            return [weights[f] / norm for f in self.fields]

        for i in range(height):
            for j in range(width):
                if i == j == 0:
                    continue
                terrain[i][j] = np.random.choice(self.fields, p=get_weight(i, j))  # type: ignore

        return Scene(terrain, start)


def load_field_info() -> list[Field]:
    with open(f"{Path(__file__).parent.resolve()}/resources/fields.yml", 'r') as file:
        doc = yaml.safe_load(file)
        fields = list()
        for field_info in doc:
            fields.extend(Field.generate_fields(None, field_info))
        return fields


if __name__ == "__main__":
    WIDTH: int = 10
    HEIGHT: int = 8


    def main() -> None:
        test = WorldGenerator.generate(500)

        scene = test.get_terrain((0, 0), HEIGHT, WIDTH)
        for i in range(HEIGHT):
            for j in range(WIDTH):
                print(scene.get_terrain_file(j, i), end=" ")
            print()


    main()
