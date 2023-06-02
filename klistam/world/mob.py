"""

"""
import enum

from attr import define
import numpy as np
from numpy.typing import NDArray

from klistam import klista


@define
class Sprite:
    """The image of an object."""
    name: str


@define
class Position:
    # Shape (2,) Array of coordinates.
    coordinates: NDArray[np.int32]


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


@define
class Mob:
    """An object that moves on the fields."""
    sprite: Sprite | None
    position: Position | None
    typ: KlistamEncounter | Prop  # | Building
