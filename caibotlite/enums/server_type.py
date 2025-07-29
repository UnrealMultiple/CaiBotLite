from enum import Enum


class ServerType(str, Enum):
    TSHOCK = "tshock"
    TMODLOADER = "tModLoader"
    BUKKIT = "bukkit"
    UNKNOWN = "unknown"

    @classmethod
    def from_value(cls, server_type: str):
        try:
            return cls(server_type)
        except ValueError:
            return ServerType.UNKNOWN

    def __str__(self):
        return self.value.upper()
