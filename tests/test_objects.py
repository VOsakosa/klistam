"""Tests for the objects in the game."""
from klistam.world.mob import Movement


def test_movement_offset() -> None:
    movement = Movement.from_name("right")
    assert movement.offset[0] == 1. and movement.offset[1] == 0.
    movement.progress = 0.3
    assert movement.offset[0] == 0.3 and movement.offset[1] == 0.
    movement.progress = 0.
    assert movement.offset[0] == 0. and movement.offset[1] == 0.
