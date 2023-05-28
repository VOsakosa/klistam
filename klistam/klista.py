"""Defines the Klistam class."""
from attrs import define
from typing_extensions import Self
from yaml import CSafeLoader
import yaml
from typing import TextIO


@define
class KlistamClass:
    sprite_name: str
    name: str
    description: str

    energy_cost: float = 0.003

    @classmethod
    def from_yaml(cls, stream: str | TextIO) -> Self:
        dct = yaml.load(stream, CSafeLoader)
        dct["sprite_name"] = dct.pop("id")
        return cls(**dct)


@define
class Klistam:
    cls: KlistamClass
    name: str | None = None

    energy: float = 1.
