from enum import Enum


class PackageDirection(str, Enum):
    TO_SERVER = "to_server"
    TO_BOT = "to_bot"
