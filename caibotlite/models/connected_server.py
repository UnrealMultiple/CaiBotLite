import asyncio
from datetime import datetime
from typing import Dict, Optional

from fastapi import WebSocket

from caibotlite.enums import ServerType
from caibotlite.models.server_info import ServerInfo


class ConnectedServer:

    def __init__(self, server_id: int, real_ip: str, ip: str, port: int, token: str, group_open_id: str,
                 server_type: ServerType,
                 ws: WebSocket):
        self.server_id: int = server_id
        self.real_ip: str = real_ip
        self.ip: str = ip
        self.port: int = port
        self.token: str = token
        self.group_open_id: str = group_open_id
        self.ws: WebSocket = ws
        self.type: ServerType = server_type
        self.server_info: Optional[ServerInfo] = None
        self.connected_at: datetime = datetime.now()
        self.request_pool: Dict[str, asyncio.Future] = {}
