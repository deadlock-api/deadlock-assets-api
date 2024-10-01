import os

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from deadlock_assets_api.models import colors
from deadlock_assets_api.models.colors import Color
from deadlock_assets_api.models.hero import Hero, load_heroes
from deadlock_assets_api.models.item import Item, ItemSlotType, ItemType, load_items
from deadlock_assets_api.models.languages import Language
from deadlock_assets_api.models.map import Map

IMAGE_BASE_URL = os.environ.get("IMAGE_BASE_URL")
router = APIRouter(prefix="/v1")


@router.get("/heroes", response_model_exclude_none=True)
def get_heroes(request: Request, language: Language = Language.English) -> list[Hero]:
    heroes = load_heroes()
    for hero in heroes:
        hero.set_base_url(
            IMAGE_BASE_URL or str(request.base_url).replace("http://", "https://")
        )
        hero.set_language(language)
    return sorted(heroes, key=lambda x: x.id)


@router.get("/heroes/{id}", response_model_exclude_none=True)
def get_hero(request: Request, id: int, language: Language = Language.English) -> Hero:
    heroes = get_heroes(request, language)
    for hero in heroes:
        if hero.id == id:
            return hero
    raise HTTPException(status_code=404, detail="Hero not found")


@router.get("/heroes/by-name/{name}", response_model_exclude_none=True)
def get_hero_by_name(
    request: Request, name: str, language: Language = Language.English
) -> Hero:
    heroes = get_heroes(request, language)
    for hero in heroes:
        if hero.class_name.lower() == name.lower():
            return hero
    raise HTTPException(status_code=404, detail="Hero not found")


@router.get("/items", response_model_exclude_none=True)
def get_items(request: Request, language: Language = Language.English) -> list[Item]:
    items = load_items()
    for item in items:
        item.set_base_url(
            IMAGE_BASE_URL or str(request.base_url).replace("http://", "https://")
        )
        item.set_language(language)
        item.postfix(items)
    return items


@router.get("/items/{id}", response_model_exclude_none=True)
def get_item(request: Request, id: int, language: Language = Language.English) -> Item:
    items = get_items(request, language)
    for item in items:
        if item.id == id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.get("/items/by-name/{name}", response_model_exclude_none=True)
def get_item_by_name(
    request: Request, name: str, language: Language = Language.English
) -> Item:
    items = get_items(request, language)
    for item in items:
        if name.lower() in [item.name.lower(), item.class_name.lower()]:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.get("/items/by-type/{type}", response_model_exclude_none=True)
def get_items_by_type(
    request: Request, type: ItemType, language: Language = Language.English
) -> list[Item]:
    items = get_items(request, language)
    type = ItemType(type.capitalize())
    return [c for c in items if c.type == type]


@router.get("/items/by-slot-type/{slot_type}", response_model_exclude_none=True)
def get_items_by_type(
    request: Request, slot_type: ItemSlotType, language: Language = Language.English
) -> list[Item]:
    items = get_items(request, language)
    slot_type = ItemSlotType(slot_type.capitalize())
    return [c for c in items if c.item_slot_type == slot_type]


@router.get("/map", response_model_exclude_none=True)
def get_map(request: Request) -> Map:
    dl_map = Map.get_default()
    dl_map.set_base_url(
        IMAGE_BASE_URL or str(request.base_url).replace("http://", "https://")
    )
    return dl_map


@router.get("/colors", response_model_exclude_none=True)
def get_colors() -> dict[str, Color]:
    return colors.get_colors()
