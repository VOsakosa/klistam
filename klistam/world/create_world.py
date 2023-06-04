"""
script with terrain information
"""
from collections.abc import Iterable
from datetime import datetime
from typing import Optional, Any
from attrs import define, field
import yaml
import numpy as np
import random
from pathlib import Path
from collections import Counter

from typing_extensions import Self

from klistam.world import WIDTH, HEIGHT
from klistam.world.mob import Mob, Position, Prop, Sprite


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
    _mobs: list[Mob] = field(factory=list)  # sortedcontainers.SortedKeyList ? -> Mob must be freezed.

    def get_terrain_file(self, x: int, y: int) -> str:
        the_field: Field = self.terrain[y][x]
        assert the_field
        return the_field.name

    @property
    def mobs(self) -> Iterable[Mob]:
        """Iterate over all mobs in the scene."""
        return self._mobs

    def add_mob(self, mob: Mob):
        assert mob not in self._mobs
        self._mobs.append(mob)

    def remove_mob(self, mob: Mob):
        self._mobs.remove(mob)


@define
class World:
    generator: "WorldGenerator"
    _scenes: dict[tuple[int, int], Scene] = field(factory=dict)
    player: Mob | None = None

    def get_scene(self, coord: tuple[int, int]) -> Scene:
        if coord not in self._scenes:
            self._scenes[coord] = self.generator.get_terrain(coord)
        return self._scenes[coord]

    def get_player_scene(self) -> Scene:
        """Return the Scene that the player is in. If there is no player, the scene at the origin is returned."""
        if self.player and self.player.position:
            return self.get_scene(self.player.position.scene)
        return self.get_scene((0, 0))

    @classmethod
    def generate(cls, seed: int | None = None) -> Self:
        self = cls(WorldGenerator.generate(seed))
        # Place player
        self.player = Mob(sprite=Sprite("gnome_f_behind", scope="player"), typ=Prop.Player)
        self.summon(self.player, (WIDTH // 2, HEIGHT // 2))
        return self

    def summon(self, mob: Mob, position: tuple[int, int]) -> None:
        if mob.position:
            old_scene = self.get_scene(mob.position.scene)
            old_scene.remove_mob(mob)
        mob.position = self.find_free_position(position)
        scene = self.get_scene(mob.position.scene)
        scene.add_mob(mob)

    def find_free_position(self, position: tuple[int, int]) -> Position:
        # TODO: Find free position
        return Position.from_tuple(position)


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

        for the_field in self.fields:
            set_weight_down_stream(the_field, 1)

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

    def main() -> None:
        test = WorldGenerator.generate(500)

        scene = test.get_terrain((0, 0), HEIGHT, WIDTH)
        for i in range(HEIGHT):
            for j in range(WIDTH):
                print(scene.get_terrain_file(j, i), end=" ")
            print()


    main()
