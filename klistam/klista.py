"""Defines the Klistam class."""
from pathlib import Path

from attrs import define, field
from typing_extensions import Self
from yaml import CSafeLoader
import yaml
from typing import TextIO, ClassVar, Mapping

assets_folder = Path(__file__).parents[1] / "assets"


@define
class KlistamClass:
    sprite_name: str
    name: str
    description: str = field(repr=False)

    energy_cost: float = 0.003

    _all_classes: ClassVar[dict[str, 'KlistamClass']] = {}

    @classmethod
    def from_yaml(cls, stream: str | TextIO) -> Self:
        dct = yaml.load(stream, CSafeLoader)
        dct["sprite_name"] = dct.pop("id")
        return cls(**dct)

    @staticmethod
    def load_classes() -> Mapping[str, 'KlistamClass']:
        """Load all available classes as a list."""
        if not KlistamClass._all_classes:
            for class_file in (assets_folder / "classes").iterdir():
                if class_file.suffix == ".yml":
                    with class_file.open() as file:
                        klass = KlistamClass.from_yaml(file)
                        KlistamClass._all_classes[klass.sprite_name] = klass
        return KlistamClass._all_classes


@define
class Klistam:
    cls: KlistamClass = field(repr=lambda cls: cls.sprite_name)
    name: str | None = None

    energy: float = 1.
