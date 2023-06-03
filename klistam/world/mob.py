"""

"""
import enum

from attr import define
import numpy as np
from numpy.typing import NDArray
from typing_extensions import Self

from klistam import klista
from klistam.world import create_world


@define(frozen=True)
class Sprite:
    """The image of an object."""
    name: str
    scope: str = "object"


@define
class Position:
    # Shape (2,) Array of coordinates.
    coordinates: NDArray[np.int32]

    @classmethod
    def from_tuple(cls, coord: tuple[int, int]) -> Self:
        return cls(np.array(coord))

    @property
    def scene_coordinates(self) -> tuple[int, int]:
        """The coordinates inside the scene."""
        return tuple(self.coordinates % np.array((create_world.WIDTH, create_world.HEIGHT)))  # type: ignore

    @property
    def scene(self) -> tuple[int, int]:
        """The scene that this position belongs to."""
        return tuple(self.coordinates // np.array((create_world.WIDTH, create_world.HEIGHT)))  # type: ignore


@define
class KlistamEncounter:
    """An object on the map indicating a "dark klistam" lurking at a place, ready to pry on the player if they
    move to close. They sporadically pop out and vanish."""
    klistam: klista.Klistam
    start: float
    end: float | None


class Prop(enum.Enum):
    """A static object, not moving and not containing any information other than its type."""
    Oak = 0x101
    Birch = 0x102
    Fir = 0x105

    Stone = 0x121
    BigStone = 0x122

    Bush = 0x140

    # Should this really be here?
    Player = 0x800


@define
class Mob:
    """An object that moves on the fields."""
    typ: KlistamEncounter | Prop  # | Building
    sprite: Sprite | None = None
    position: Position | None = None
