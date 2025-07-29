from dataclasses import dataclass
from typing import Dict, Any

from caibotlite.enums import ServerType


@dataclass
class ServerInfo:
    type: ServerType
    game_version: str
    server_core_version: str
    plugin_version: str
    enable_whitelist: bool
    system: str
    server_name: str
    settings: Dict[str, Any]