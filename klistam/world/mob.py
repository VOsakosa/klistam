"""

"""
import enum
from typing import Literal

from attr import define
import numpy as np
from numpy.typing import NDArray
from typing_extensions import Self

from klistam import world as world_module
from klistam import klista


@define(frozen=True)
class Sprite:
    """The image of an object."""
    name: str
    scope: str = "object"


@define(repr=False)
class Position:
    # Shape (2,) Array of coordinates.
    coordinates: NDArray[np.int32]

    @classmethod
    def from_tuple(cls, coord: tuple[int, int]) -> Self:
        return cls(np.array(coord))

    @property
    def scene_coordinates(self) -> tuple[int, int]:
        """The coordinates inside the scene."""
        return tuple(self.coordinates % np.array((world_module.WIDTH, world_module.HEIGHT)))  # type: ignore

    @property
    def scene(self) -> tuple[int, int]:
        """The scene that this position belongs to."""
        return tuple(self.coordinates // np.array((world_module.WIDTH, world_module.HEIGHT)))  # type: ignore

    def __repr__(self) -> str:
        return f"Position({self.coordinates[0]}, {self.coordinates[1]})"


@define
class Movement:
    """A shown movement of the mob. The position of the mob is changed on the start of the movement, so a movement
    to the right will cause the mob to be shown to the left of its actual position."""
    direction: NDArray[np.int32]
    progress: float = 1.

    @classmethod
    def from_name(cls, name: Literal["right", "left", "up", "down"]):
        if name == "right":
            ans = (1, 0)
        elif name == "left":
            ans = (-1, 0)
        elif name == "up":
            ans = (0, -1)
        elif name == "down":
            ans = (0, 1)
        else:
            raise ValueError(f"Illegal direction name {name}")
        return Movement(np.array(ans, np.int32))

    @property
    def offset(self) -> NDArray[np.float_]:
        return -self.progress * self.direction


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


@define(eq=False)
class Mob:
    """An object that moves on the fields."""
    typ: KlistamEncounter | Prop  # | Building
    sprite: Sprite | None = None
    position: Position | None = None
    movement: Movement | None = None
