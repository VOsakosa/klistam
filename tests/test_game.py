from klistam.klistam import KlistamClass


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
