"""
script with terrain information
"""
import random
from collections import Counter
from collections.abc import Iterable
from datetime import datetime
from itertools import count
from pathlib import Path
from typing import Optional, Any

import numpy as np
import scipy  # type: ignore
import yaml
from attrs import define, field
from numpy.typing import NDArray
from typing_extensions import Self

from klistam.klista import Klistam, KlistamClass
from klistam.world import WIDTH, HEIGHT
from klistam.world.mob import Mob, Position, Prop, Sprite, KlistamEncounter

LOAD_RADIUS = 3
ENCOUNTER_TIME = 120 * 30
SPAWN_RATE = 1 / 0x1000


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
    update_time: float = float("-inf")

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

    def remove_mob_idx(self, idx: int):
        del self._mobs[idx]


def to_2tuple(coord_array: NDArray[np.int32]) -> tuple[int, int]:
    assert len(coord_array) == 2
    return tuple(coord_array)  # type: ignore


@define
class World:
    generator: "WorldGenerator"
    _scenes: dict[tuple[int, int], Scene] = field(factory=dict, repr=False)
    player: Mob | None = None
    time: int = 0

    def get_scene(self, coord: tuple[int, int]) -> Scene:
        if coord not in self._scenes:
            self._scenes[coord] = self.generator.get_terrain(coord)
        return self._scenes[coord]

    def get_player_scene(self) -> Scene:
        """Return the Scene that the player is in. If there is no player, the scene at the origin is returned."""
        if self.player and self.player.position:
            return self.get_scene(self.player.position.scene)
        return self.get_scene((0, 0))

    def get_object_at(self, coord: NDArray[np.int32]) -> None | Mob:
        for mob in self.get_scene(Position(coord).scene).mobs:
            if mob.position and np.array_equal(mob.position.coordinates, coord):
                return mob
        return None

    @classmethod
    def generate(cls, seed: int | None = None) -> Self:
        self = cls(WorldGenerator.generate(seed))
        # Place player
        self.player = Mob(sprite=Sprite("gnome_f_behind", scope="player"), typ=Prop.Player)
        self.summon(self.player, (WIDTH // 2, HEIGHT // 2))
        return self

    def summon(self, mob: Mob, position: tuple[int, int] | NDArray[np.int32]) -> None:
        """Summon a mob at a position. If the mob was on the map before, it is correctly removed."""
        self.remove_mob(mob)
        mob.position = self.find_free_position(position)
        scene = self.get_scene(mob.position.scene)
        scene.add_mob(mob)

    def remove_mob(self, mob: Mob) -> None:
        if mob.position:
            old_scene = self.get_scene(mob.position.scene)
            old_scene.remove_mob(mob)
            mob.position = None

    def find_free_position(self, position: tuple[int, int] | NDArray[np.int32]) -> Position:
        """Find a free position to place an object around a position."""
        check_pos = np.array(position)
        if not self.get_object_at(check_pos):
            return Position(check_pos)
        check_dir = np.array((0, -1))
        circulation_matrix = np.array(((0, -1), (1, 0)))  # counter-clockwise
        for segment in count(2):
            for _pos in range(segment // 2):
                check_pos += check_dir
                if not self.get_object_at(check_pos):
                    return Position(check_pos)
            check_dir = check_dir @ circulation_matrix
        raise ValueError("Unreachable code.")

    def tick(self):
        self.time += 1
        for scene in self.get_loaded_scenes():
            self.tick_scene(scene)

    def get_loaded_scenes(self) -> Iterable[Scene]:
        if self.player and self.player.position:
            middle_x, middle_y = self.player.position.scene
            for x in range(middle_x - LOAD_RADIUS - 1, middle_x + LOAD_RADIUS):
                for y in range(middle_y - LOAD_RADIUS - 1, middle_y + LOAD_RADIUS):
                    yield self.get_scene((x, y))

    def tick_scene(self, scene: Scene):
        # Spawning
        time_since_update = min(self.time - scene.update_time, ENCOUNTER_TIME)
        amount = scipy.stats.poisson.rvs(time_since_update * SPAWN_RATE)
        for spawn_x, spawn_y in zip(scipy.stats.randint.rvs(0, WIDTH, size=amount),
                                    scipy.stats.randint.rvs(0, HEIGHT, size=amount)):
            position = np.array((WIDTH, HEIGHT)) * scene.start_coord + (spawn_x, spawn_y)
            if not self.get_object_at(position):
                print(f"Spawn Encounter at {position}")
                start = self.time - scipy.stats.randint.rvs(0, time_since_update)
                self.summon(Mob(
                    typ=KlistamEncounter(Klistam(KlistamClass.load_classes()["wood_idol"]),
                                         start, self.time + ENCOUNTER_TIME),
                    sprite=Sprite("encounter"),
                ), position)

        to_remove = []
        for i, mob in enumerate(scene.mobs):
            if isinstance(mob.typ, KlistamEncounter):
                if mob.typ.end and mob.typ.end < self.time:
                    to_remove.append(i)
                    print(f"Remove encounter at {mob.position}")
        for i in to_remove:
            scene.remove_mob_idx(i)
        scene.update_time = self.time


@define
class WorldGenerator:
    """The entire world of the game."""
    seed: int = 0
    fields: list[Field] = field(factory=list, repr=False)

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
