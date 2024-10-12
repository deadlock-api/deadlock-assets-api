import json
from typing import Annotated, Union

from pydantic import Field

from deadlock_assets_api import utils
from deadlock_assets_api.models.v2.api_ability import Ability
from deadlock_assets_api.models.v2.api_upgrade import Upgrade
from deadlock_assets_api.models.v2.api_weapon import Weapon
from deadlock_assets_api.models.v2.raw_ability import RawAbility
from deadlock_assets_api.models.v2.raw_hero import RawHero
from deadlock_assets_api.models.v2.raw_upgrade import RawUpgrade
from deadlock_assets_api.models.v2.raw_weapon import RawWeapon

Item = Annotated[Union[Ability, Weapon, Upgrade], Field(discriminator="type")]


def test_parse():
    def get_raw_heroes():
        with open("res/raw_heroes.json") as f:
            raw_heroes = json.load(f)
        return [
            RawHero(class_name=k, **v)
            for k, v in raw_heroes.items()
            if k.startswith("hero_")
            and "base" not in k
            and "generic" not in k
            and "dummy" not in k
        ]

    def get_raw_items():
        def parse(class_name, data) -> RawWeapon | RawUpgrade | RawAbility:
            name = utils.strip_prefix(class_name, "citadel_").lower()
            first_word = name.split("_")[0]
            if first_word == "ability":
                return RawAbility(class_name=class_name, **data)
            elif first_word == "upgrade":
                return RawUpgrade(class_name=class_name, **data)
            elif first_word == "weapon":
                return RawWeapon(class_name=class_name, **data)

            hero_list = [
                "astro",
                "atlas",
                "bebop",
                "bomber",
                "cadence",
                "chrono",
                "dynamo",
                "forge",
                "ghost",
                "gigawatt",
                "gunslinger",
                "haze",
                "hornet",
                "inferno",
                "kali",
                "kelvin",
                "krill",
                "lash",
                "mirage",
                "nano",
                "orion",
                "rutger",
                "shiv",
                "slork",
                "synth",
                "tengu",
                "thumper",
                "tokamak",
                "viscous",
                "warden",
                "wraith",
                "wrecker",
                "yakuza",
                "yamato",
            ]
            if first_word in hero_list:
                return RawAbility(class_name=class_name, **data)
            print(f"Unknown class name: {class_name}")
            return None

        with open("res/raw_items.json") as f:
            raw_items = json.load(f)
        raw_items = [
            parse(k, v)
            for k, v in raw_items.items()
            if "base" not in k
            and "dummy" not in k
            and ("generic" not in k or "citadel" in k)
            and isinstance(v, dict)
        ]
        return [item for item in raw_items if item is not None]

    raw_heroes = get_raw_heroes()
    raw_items = get_raw_items()

    localization = {}
    with open("res/localization/citadel_gc_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_main_english.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_gc_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_heroes_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])
    with open("res/localization/citadel_main_german.json") as f:
        localization.update(json.load(f)["lang"]["Tokens"])

    def item_from_raw_item(
        raw_item: RawUpgrade | RawAbility | RawWeapon,
        raw_hero: list[RawHero],
        localization,
    ) -> Item:
        if raw_item.type == "ability":
            return Ability.from_raw_item(raw_item, raw_hero, localization)
        elif raw_item.type == "upgrade":
            return Upgrade.from_raw_item(raw_item, raw_hero, localization)
        elif raw_item.type == "weapon":
            return Weapon.from_raw_item(raw_item, raw_hero, localization)
        else:
            raise ValueError(f"Unknown item type: {raw_item.type}")

    items = [
        item_from_raw_item(raw_item, raw_heroes, localization) for raw_item in raw_items
    ]

    with open("test.json", "w") as f:
        json.dump([item.model_dump(exclude_none=True) for item in items], f, indent=2)


if __name__ == "__main__":
    test_parse()