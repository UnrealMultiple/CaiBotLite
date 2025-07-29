from enum import Enum


class ShopItemType(str, Enum):
    COMMAND = "command"
    ITEM = "item"