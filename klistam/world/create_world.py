"""
script with terrain information
"""
from typing import Optional, Any
from attrs import define, field
import yaml
import random


@define
class Field:
    name: str
    walkable: bool = False
    parent: "Field | None" = None

    def __str__(self):
        return self.name + (f"[{self.parent}]" if self.parent else "")

    @classmethod
    def generate_fields(cls, parent: "Field | None", obj_info: [str | dict[str, Any]]) -> list["Field"]:
        fields = list()
        if isinstance(obj_info, str):
            fields.append(cls(parent=parent, name=obj_info))
        else:
            assert "name" in obj_info
            walkable = obj_info["walkable"] if "walkable" in obj_info else (parent.walkable if parent else None)
            instance = cls(parent=parent, name=obj_info["name"],
                           walkable=walkable)
            fields.append(instance)
            if "categories" in obj_info:
                for child_info in obj_info["categories"]:
                    fields.extend(Field.generate_fields(parent=instance, obj_info=child_info))
        return fields


@define
class World:
    seed: int = None
    fields: list[Field] = field(factory=list)

    @classmethod
    def generate(cls, seed: Optional[int]=None):
        instance = cls()
        instance.fields = load_field_info()
        return instance


def load_field_info():
    with open('ressources/fields.yml', 'r') as file:
        doc = yaml.safe_load(file)
        fields = list()
        for field in doc:
            fields.extend(Field.generate_fields(None, field))
        return fields


world = World.generate()
for field in world.fields:
    print(field)