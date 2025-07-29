from http import HTTPStatus

import nonebot
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from nonebot import logger

from caibotlite.database import async_session
from caibotlite.enums import ServerType
from caibotlite.enums.package_type import PackageType
from caibotlite.enums.whitelist_result import WhitelistResult
from caibotlite.managers.connection_manager import ConnectionManager
from caibotlite.managers.group_manager import GroupManager
from caibotlite.managers.login_manager import LoginManager
from caibotlite.managers.server_manager import ServerManager
from caibotlite.managers.token_mannager import TokenManager
from caibotlite.managers.user_manager import UserManager
from caibotlite.models.connected_server import ConnectedServer
from caibotlite.models.package import Package
from caibotlite.models.server_info import ServerInfo
from caibotlite.services import Statistics
from caibotlite.services.package_writer import PackageWriter

app: FastAPI = nonebot.get_app()


# app = FastAPI()


@app.get("/server/token/{init_code}")
async def handle_get_token(init_code: int):
    token_info = TokenManager.try_get_token(init_code)

    if token_info is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Not found available token")

    response = {
        "token": token_info.token,
        "group_open_id": token_info.group_open_id
    }

    return response


@app.websocket("/server/ws/{group_open_id}/{server_type}/")
async def handle_websocket(websocket: WebSocket, group_open_id: str, server_type: ServerType):
    await websocket.accept()

    headers = websocket.headers
    token = headers.get("authorization") or headers.get("Authorization")

    if not token:
        logger.warning("验证服务器失败: 缺失认证令牌!")
        await websocket.close(code=1008, reason="缺失认证令牌!")
        return

    if not token.startswith("Bearer "):
        logger.warning("验证服务器失败: 认证令牌格式错误!")
        await websocket.close(code=1008, reason="认证令牌格式错误!")
        return

    server_token = token.split(" ")[1]
    if not ServerManager.is_valid_token(server_token):
        logger.warning("验证服务器失败: 无效认证令牌!")
        await websocket.close(code=4003, reason="无效认证令牌!")
        return

    server_type_enum = ServerType.from_value(server_type)
    if server_type_enum == ServerType.UNKNOWN:
        logger.warning("不支持此服务器类型!")
        await websocket.close(code=1008, reason="不支持此服务器类型!")
        return
    async with async_session() as session:
        server = await ServerManager.get_server_by_token(session, server_token)
    if server is None:
        logger.warning("无匹配此令牌的服务器!")
        await websocket.close(code=4003, reason="无匹配此令牌的服务器!")
        return

    if server.group_open_id != group_open_id:
        logger.warning("群OpenID与此服务器不匹配!")
        await websocket.close(code=4003, reason="群OpenID与此服务器不匹配!")
        return

    group = server.group
    connected_server = ConnectedServer(server.id, websocket.client.host, server.ip, server.port, server_token,
                                       group.open_id,
                                       server_type, websocket)
    ConnectionManager.add_server(connected_server)
    try:
        await websocket_loop(connected_server)
    except WebSocketDisconnect:
        logger.info(f"服务器[{server.id}]已断开连接~")
    except Exception as ex:
        logger.error(f"服务器[{server.id}]发生异常: {ex}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(1011, "服务器内部错误")
        ConnectionManager.remove_server(connected_server.token)


async def websocket_loop(connected_server: ConnectedServer):
    ws = connected_server.ws
    token = connected_server.token
    server_id = connected_server.server_id

    while True:
        msg = await ws.receive_text()
        package = Package.model_validate_json(msg)

        logger.info(
            f"收到服务器[{server_id}]的\"{package.type}\"数据包 (request: {package.is_request})")

        if package.type.get_version() != package.version:
            logger.warning(
                f"服务器[{server_id}]发送了一个过期\"{package.type}\"数据包 (v{package.version} < v{package.type.get_version()})")

        if package.is_request:
            ConnectionManager.add_api_result(token, server_id, package)
            continue

        await handle_general_message(connected_server, package)


async def handle_general_message(connected_server: ConnectedServer, package: Package):
    payload = package.payload
    match package.type:
        case PackageType.HELLO:
            server_info = ServerInfo(
                connected_server.type,
                payload['game_version'],
                payload['server_core_version'],
                payload['plugin_version'],
                payload['enable_whitelist'],
                payload['system'],
                payload['server_name'],
                payload['settings'],
            )
            connected_server.server_info = server_info

        case PackageType.WHITELIST:
            name = payload['player_name']
            uuid = payload['player_uuid']
            ip = payload['player_ip']
            async with async_session() as session:
                user = await UserManager.get_user_by_name(session, connected_server.group_open_id, name)
                group = await GroupManager.get_group_by_open_id(session, connected_server.group_open_id)
                Statistics.whitelist_check += 1
                package_writer = PackageWriter(PackageType.WHITELIST, False)
                package_writer.write("player_name", name)
                whitelist_result: WhitelistResult
                if user is None:
                    package_writer.write("whitelist_result", WhitelistResult.NOT_IN_WHITELIST)
                elif user.open_id in group.black_list:
                    package_writer.write("whitelist_result", WhitelistResult.In_GROUP_BLACKLIST)
                elif not LoginManager.try_login_ok(session, user, uuid, ip):
                    package_writer.write("whitelist_result", WhitelistResult.NEED_LOGIN)
                else:
                    package_writer.write("whitelist_result", WhitelistResult.ACCEPT)

                await ConnectionManager.send_data(connected_server.token, package_writer.build())


def init_api():
    logger.success("CaiBotAPI初始化完成~")
