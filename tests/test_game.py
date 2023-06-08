from klistam.klista import KlistamClass
from klistam.world import HEIGHT, WIDTH
from klistam.world.create_world import World, WorldGenerator, Scene
import numpy as np

from klistam.world.mob import Mob, Prop


def test_klistam_load() -> None:
    wood_idol = KlistamClass.from_yaml("""
id: wood_idol
name: "Wood Idol"
energy_cost: 0.001
description: >-
  The wood idol is the most basic kind of klistam one can meet in the forest.
    """)
    assert wood_idol.sprite_name == "wood_idol"
    assert wood_idol.energy_cost == 0.001


def test_find_free_position() -> None:
    # Create an empty world
    world = World(WorldGenerator.generate())
    # noinspection PyTypeChecker
    world._scenes[0, 0] = Scene(np.full((WIDTH, HEIGHT), world.generator.fields[0]), (0, 0))
    assert np.array_equal(world.find_free_position((5, 5)).coordinates, np.array((5, 5)))
    world.summon(Mob(Prop.Bush, None), (5, 5))
    assert world.get_object_at(np.array((5, 5)))
    assert np.array_equal(world.find_free_position((5, 5)).coordinates, np.array((5, 4)))
    world.summon(Mob(Prop.Bush, None), (5, 5))
    assert np.array_equal(world.find_free_position((5, 5)).coordinates, np.array((4, 4)))
