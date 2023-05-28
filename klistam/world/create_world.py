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


@define(eq=False)
class Field:
    name: str
    walkable: bool = False
    parent: "Field | None" = None
    children: "list(Field) | None" = field(factory=list)

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
    terrain: np.array
    start_cord: tuple[int, int]

    def get_terrain_file(self, x, y):
        tfield = self.terrain[y][x]
        assert tfield
        return tfield.name


@define
class World:
    seed: int = 0
    fields: list[Field] = field(factory=list)

    @classmethod
    def generate(cls, seed: Optional[int] = None):
        instance = cls(seed or hash(datetime.now()))
        instance.fields = load_field_info()
        return instance

    def get_impact(self, field_type: Field, factor: float):
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

    def get_terrain(self, start: tuple[int, int] = (0, 0), height=32, width=32):
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
                terrain[i][j] = np.random.choice(self.fields, p=get_weight(i, j))

        return Scene(terrain, start)


def load_field_info():
    with open(f"{Path(__file__).parent.resolve()}/ressources/fields.yml", 'r') as file:
        doc = yaml.safe_load(file)
        fields = list()
        for field_info in doc:
            fields.extend(Field.generate_fields(None, field_info))
        return fields


if __name__ == "__main__":
    test = World.generate(500)
    WIDTH = 10
    HEIGHT = 8

    scene = test.get_terrain((0, 0), HEIGHT, WIDTH)
    for i in range(HEIGHT):
        for j in range(WIDTH):
            print(scene.get_terrain_file(j, i), end=" ")
        print()
