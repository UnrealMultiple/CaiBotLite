import asyncio
from typing import Dict, Any

from nonebot import logger

from caibotlite.models import ConnectedServer, Package


class ConnectionManager:
    connected_servers: Dict[str, ConnectedServer] = {}

    @classmethod
    def add_server(cls, connected_server: ConnectedServer):
        cls.connected_servers[connected_server.token] = connected_server

    @classmethod
    def remove_server(cls, token: str):
        if token in cls.connected_servers:
            cls.connected_servers.pop(token)

    @classmethod
    def is_server_online(cls, token: str):
        return token in cls.connected_servers

    @classmethod
    def add_api_result(cls, token: str, server_id: int, package: Package):
        if token not in cls.connected_servers:
            logger.info(f"BOT无法处理服务器[{server_id}]数据包\"{package.type}\"的返回API结果, 目标服务器当前不可用!")
            return
        connected_server = cls.connected_servers[token]

        if package.request_id not in connected_server.request_pool:
            logger.info(f"无法处理服务器[{server_id}]数据包\"{package.type}\"的返回API结果, request_id无效")
            return

        connected_server.request_pool[package.request_id].set_result(package.payload)

    @classmethod
    async def call_api(cls, token: str, package: Package, timeout: float = 10.0) -> Dict[str, Any]:
        if token not in cls.connected_servers:
            raise Exception(f"failed to call '{package.type}', because server({token}) is not available")

        connected_server = cls.connected_servers[token]
        logger.info(f"向服务器[{connected_server.server_id}]发起\"{package.type}\"调用")
        await connected_server.ws.send_text(package.model_dump_json())

        future = asyncio.get_event_loop().create_future()

        connected_server.request_pool[package.request_id] = future
        try:
            result = await asyncio.wait_for(future, timeout)
            return result
        except TimeoutError:
            future.cancel()
            raise
        finally:
            del connected_server.request_pool[package.request_id]

    @classmethod
    async def send_data(cls, token: str, package: Package):
        if token not in cls.connected_servers:
            raise Exception(f"failed to send '{package.type}', because server({token}) is not available")

        connected_server = cls.connected_servers[token]
        logger.info(f"向服务器[{connected_server.server_id}]发送\"{package.type}\"数据包")
        await connected_server.ws.send_text(package.model_dump_json())
