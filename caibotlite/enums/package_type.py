from enum import Enum


class PackageType(str, Enum):
    HELLO = "hello"
    WHITELIST = "whitelist"
    PLAYER_LIST = "player_list"
    PROGRESS = "progress"
    LOOK_BAG = "look_bag"
    WORLD_FILE = "world_file"
    MAP_FILE = "map_file"
    MAP_IMAGE = "map_image"
    SELF_KICK = "self_kick"
    CALL_COMMAND = "call_command"
    UNBIND_SERVER = "unbind_server"
    HEARTBEAT = "heartbeat"
    PLUGIN_LIST = "plugin_list"
    RANK_DATA = "rank_data"
    SHOP_BUY = "shop_buy"
    SHOP_CONDITION = "shop_condition"
    UNKNOWN = "unknown"

    @classmethod
    def from_value(cls, package_type: str):
        try:
            return cls(package_type.lower())
        except ValueError:
            return PackageType.UNKNOWN

    def get_version(self):
        match self:
            case PackageType.WHITELIST:
                return "2025.12.18"
            case PackageType.SELF_KICK:
                return "2025.7.18"
            case PackageType.HELLO:
                return "2025.7.18"
            case PackageType.PLAYER_LIST:
                return "2025.7.18"
            case PackageType.PROGRESS:
                return "2025.7.18"
            case PackageType.LOOK_BAG:
                return "2025.7.18"
            case PackageType.WORLD_FILE:
                return "2025.7.18"
            case PackageType.MAP_FILE:
                return "2025.7.18"
            case PackageType.MAP_IMAGE:
                return "2025.7.18"
            case PackageType.MAP_IMAGE:
                return "2025.7.18"
            case PackageType.SELF_KICK:
                return "2025.7.18"
            case PackageType.CALL_COMMAND:
                return "2025.7.18"
            case PackageType.HEARTBEAT:
                return "2025.7.25"
            case PackageType.PLUGIN_LIST:
                return "2025.7.25"
            case PackageType.RANK_DATA:
                return "2025.7.25"

            case PackageType.SHOP_BUY:
                return "2025.7.25"
            case PackageType.SHOP_CONDITION:
                return "2025.7.25"
            case PackageType.UNKNOWN:
                return "2007.5.24"

        return "2025.7.18"
