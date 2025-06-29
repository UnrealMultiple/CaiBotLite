﻿import asyncio
import base64
import datetime
import gzip
import io
import json
import traceback
import uuid

import nonebot
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketException
from nonebot.adapters.qq import Bot
from nonebot.adapters.qq import MessageSegment
from nonebot.log import logger
from starlette.websockets import WebSocketDisconnect


from src.models import statistics
from src.models.group import Group
from src.models.login_request import LoginRequest
from src.models.server import Server
from src.models.server_connection_manager import ServerConnectionManager
from src.models.user import User
from src.utils.bag_png_helper import get_bag_png
from src.utils.file import create_upload_link
from src.utils.process_png_helper import get_process_png
from src.utils.sensitive_words_filter import SensitiveWordsFilter
from src.utils.text_handler import TextHandle

app = nonebot.get_app()
app: FastAPI

server_connection_manager = ServerConnectionManager()
tokens = {}
online_request = {}
cmd_request = {}
last_connection_time = {}
login_attempts = {}
login_requests = {}
last_sent_warning_times = {}


def decompress_base64_gzip(base64_string):
    compressed_data = base64.b64decode(base64_string)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gzip_file:
        decompressed_data = gzip_file.read()

    return decompressed_data.decode('utf-8')


def compare_versions(version1: str, version2: str) -> bool:
    """
    比较两个版本号的大小。

    :param version1: 第一个版本号字符串（例如 "5.2.3"）。
    :param version2: 第二个版本号字符串（例如 "5.1.0"）。
    :return:
        - 如果 version1 > version2，返回 1。
        - 如果 version1 < version2，返回 -1。
        - 如果 version1 == version2，返回 0。
        - 如果版本号格式错误，返回 None。
    """
    try:
        # 将版本号字符串拆分为整数元组
        v1 = tuple(map(int, version1.split('.')))
        v2 = tuple(map(int, version2.split('.')))

        # 比较两个元组
        if v1 > v2:
            return True
        elif v1 < v2:
            return False
        else:
            return True
    except (ValueError, AttributeError):
        # 如果版本号格式错误，返回 None
        return True



def is_valid_guid(guid):
    try:
        uuid.UUID(guid, version=4)
        return True
    except ValueError:
        return False


async def wait_for_online(group_id: str, servers: list[Server]):
    cmd = {
        "type": "online",
    }
    result  = []
    tasks = []
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
            if server.token in online_request:
                online_request.pop(server.token)
            task = asyncio.create_task(server_connection_manager.send_data(server.token, cmd, group_id))
            tasks.append(task)

    await asyncio.gather(*tasks)
    count = 0
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
            timeout = False
            while server.token not in online_request:
                if count == 200:
                    result.append(f"๑{index + 1}๑❌服务器连接超时")
                    timeout = True
                    break
                await asyncio.sleep(0.01)
                count += 1
            if not timeout:
                result.append(online_request.pop(server.token))
        else:
            result.append(f"๑{index + 1}๑❌服务器处于离线状态")
    return result


async def wait_for_cmd(group_id: str, cmd, servers: list[Server]):
    result = []
    tasks = []
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
            if server.token in cmd_request:
                cmd_request.pop(server.token)
            cmd_request[server.token] = ""
            task = asyncio.create_task(server_connection_manager.send_data(server.token, cmd, group_id))
            tasks.append(task)

    await asyncio.gather(*tasks)
    count = 0
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
            timeout = False
            while not cmd_request[server.token]:
                if count == 1000:
                    result.append(f"#️⃣服务器[{index+1}]指令执行超时!")
                    timeout = True
                    break
                await asyncio.sleep(0.01)
                count += 1
            if not timeout:
                result.append(cmd_request.pop(server.token))
        else:
            result.append(f"❌服务器[{index+1}]处于离线状态!")
    return result







@app.get("/bot/get_token")
async def get_token(code: int):
    current_time = datetime.datetime.now()
    if code in tokens:
        server, expiry_time = tokens[code]
        if current_time < expiry_time:  # 5分钟过期
            server.add_self_server()
            tokens.pop(code)
            logger.warning(f"服务器({server.token})被动绑定成功!")  # “怎么有种我是男的的感觉” ---张芷睿大人 (24.12.22)
            return {"status": 200, "token": server.token}
        else:
            tokens.pop(code)
            raise HTTPException(status_code=418, detail="token已失效!")
    else:
        raise HTTPException(status_code=418, detail="token获取失败!")


def add_token(code: int, server: Server, timeout: int):
    expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    tokens[code] = (server, expiry_time)


@app.websocket("/bot/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):

    if not is_valid_guid(token):
        raise WebSocketException(4000,"无效TOKEN")
    await websocket.accept()
    logger.info(f"[CaiBotAPI]{websocket.client.host}:{websocket.client.port}正在连接...")
    await server_connection_manager.add_server_connection(token, websocket)
    try:
        server = Server.get_server(token)
        if server is None:
            logger.warning(f"服务器断开连接: {token},原因：不属于任何群的服务器")
            disconnect_info = {
                "type": "delserver"
            }
            await websocket.send_json(disconnect_info)
            raise WebSocketException(4000, "不属于任何群的服务器")

        group = Group.get_group_through_server(server)
        if group.open_id != server.owner:
            logger.warning(f"服务器断开连接: {token},原因：服务器拥有群已成为子群，自动解绑")
            disconnect_info = {
                "type": "delserver"
            }
            await websocket.send_json(disconnect_info)
            raise WebSocketException(4000, "服务器拥有群已成为子群，自动解绑")


        await websocket.send_text(json.dumps({"type": "hello", "group": group.open_id}))
        logger.success(f"群服务器已连接:{group.open_id}({token})")
        while True:
            data = await websocket.receive_text()
            if not server_connection_manager.server_available(token):
                raise WebSocketDisconnect(4000, "无效连接")
            # noinspection PyBroadException
            try:
                await handle_message(data, group, token, server, websocket)
            except Exception:
                logger.error(f"群服务器{group.open_id}({token}):{traceback.format_exc()}")
    except WebSocketDisconnect as e:
        logger.warning(f"服务器断开连接: {token},原因：{str(e)}")
    except Exception as e:
        logger.warning(f"服务器断开连接: {token},原因：{str(e)}")
        await websocket.close()
    finally:
        server_connection_manager.del_server_connection(token)





async def handle_message(data: str, group: Group, token: str, server: Server, websocket) -> None:
    data = json.loads(data)
    if data['type'] != 'HeartBeat':
        logger.info(f"收到来自{group.open_id}({token})的数据: {data['type']}")
    if data['type'] == "hello":
        websocket.tshock_version = data['tshock_version']
        websocket.plugin_version = data['plugin_version']
        websocket.terraria_version = data['terraria_version']
        websocket.whitelist = data['cai_whitelist']
        websocket.world = SensitiveWordsFilter.replace(data['world'])
        websocket.os = data['os']
        server_connection_manager.connections[token] = websocket
        logger.success(f"获取到{group.open_id}({token})的服务器信息: \n"
                       f"CaiBot版本: {data['plugin_version']}, TShock版本: {data['tshock_version']}, Cai白名单: {data['cai_whitelist']}, 系统:{data['os']}")
    bot: Bot
    try:
        bot = nonebot.get_bot()
    except ValueError:
        return

    if 'group' in data:
        group = group.get_group(data['group'])
        group_id = data['group']
    else:
        group = group.get_group(group.open_id)
        group_id = group.open_id
    if 'msg_id' in data:
        msg_id = data['msg_id']
    else:
        msg_id = None
    index = server.get_server_index(group.open_id)

    if data['type'] == "cmd":
        if token in cmd_request:
            if cmd_request[token]:
                del cmd_request[token]
            else:
                if data['result']:
                    cmd_request[token] =f"#️⃣服务器[{index}]返回结果:\n" \
                                        f"{SensitiveWordsFilter.replace(TextHandle.all(data['result']))}"
                else:
                    cmd_request[token] = f"#️⃣服务器[{index}]返回结果"
                return
        if data['result']:
            await bot.send_to_group(group_id, MessageSegment.text(f"\n『远程指令』\n"
                                                                   f"服务器[{index}]返回结果:\n" +
                                                                   f"{SensitiveWordsFilter.replace(TextHandle.all(data['result']))}"),
                                    msg_id=msg_id)
        else:
            await bot.send_to_group(group_id, MessageSegment.text(f"\n『远程指令』\n"
                                                                  f"服务器[{index}]返回了个寂寞"), msg_id=msg_id)
    elif data['type'] == "online":
        if websocket.tshock_version != "None":
            if not compare_versions(websocket.tshock_version,"5.2.3.0"):
                data['result'] = data['result']+ "\n⚠️不支持此TShock版本,请升级到TShock v5.2.3+"
            if compare_versions(websocket.tshock_version, "5.2.3.0") and not compare_versions(websocket.plugin_version,"2025.3.10.1"):
                data['result'] = data['result']+ "\n⚠️不支持此适配插件版本,请升级到CaiBotLite v2025.04.26+"
            if websocket.plugin_version == "2025.4.12.1":
                data['result'] = data['result']+ "\n⚠️此适配插件版本有严重安全漏洞,请升级到CaiBotLite v2025.04.26+"

        result = SensitiveWordsFilter.replace(f"๑{index}๑⚡{data['worldname']} 「{data['process']}」\n" + data['result'])
        online_request[token] = result
        websocket.world = SensitiveWordsFilter.replace(data['worldname'])
        server_connection_manager.connections[token] = websocket

    elif data['type'] == "process":
        progress_img = get_process_png(data)
        byte_arr = io.BytesIO()
        progress_img.save(byte_arr, format='PNG')
        byte_value = byte_arr.getvalue()
        await bot.send_to_group(group_id, MessageSegment.file_image(byte_value), msg_id=msg_id)

    elif data['type'] == "process_text":
        await bot.send_to_group(group_id,
                                MessageSegment.text(f"\n『进度查询』\n" + SensitiveWordsFilter.replace(data['process'])),
                                msg_id=msg_id)

    elif data['type'] == "whitelistV2":
        name = data['name']
        plr_uuid = data['uuid']
        ip = data['ip']
        user = User.get_user_by_name(group.open_id, name)
        # noinspection PyBroadException
        try:
            statistics.Statistics.add_check_whitelist()
        except:
            pass
        if plr_uuid is None or not is_valid_guid(plr_uuid):
            return
        if user is None:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 404
            }
            await server_connection_manager.send_data(token, re, None)
            return
        if user.open_id in group.black_list:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 403
            }
            await server_connection_manager.send_data(token, re, None)
            return
        safe_uuid = plr_uuid if ip == "127.0.0.1" else plr_uuid + "+" + ip
        if safe_uuid in user.uuid:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 200
            }
            await server_connection_manager.send_data(token, re, None)
        else:
            login_requests[user.open_id] = LoginRequest(datetime.datetime.now(),
                                                        plr_uuid if ip == "127.0.0.1" else plr_uuid + "+" + ip)
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 405
            }
            await server_connection_manager.send_data(token, re, None)

    elif data['type'] == "mappngV2":
        base64_string = data['result']
        decoded_bytes = base64.b64decode(decompress_base64_gzip(base64_string))
        await bot.send_to_group(group_id, MessageSegment.file_image(decoded_bytes), msg_id=msg_id)


    elif data['type'] == "lookbag":
        if data['exist'] == 0:
            await bot.send_to_group(group_id, MessageSegment.text(f"\n『查背包』\n" +
                                                                  f"查询失败!\n" +
                                                                  f"查询的玩家不存在！"), msg_id=msg_id)
        else:
            data['economic']['Coins'] = SensitiveWordsFilter.replace(TextHandle.all(data['economic']['Coins']))
            data['economic']['LevelName'] = SensitiveWordsFilter.replace(TextHandle.all(data['economic']['LevelName']))
            data['economic']['Skill'] = SensitiveWordsFilter.replace(
                TextHandle.add_line_break(TextHandle.all(data['economic']['Skill']), 9))
            img = get_bag_png(SensitiveWordsFilter.replace(data['name']), data['inventory'], data['buffs'],
                              data['enhances'], data['life'],
                              data['mana'], data['quests_completed'], data['economic'])
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            byte_value = byte_arr.getvalue()
            await bot.send_to_group(group_id, MessageSegment.file_image(byte_value), msg_id=msg_id)
    elif data['type'] == "lookbag":
        if data['exist'] == 0:
            await bot.send_to_group(group_id, MessageSegment.text(f"\n『查背包』\n" +
                                                                  f"查询失败!\n" +
                                                                  f"查询的玩家不存在！"), msg_id=msg_id)
    elif data['type'] == "lookbag_text":
        await  bot.send_to_group(group_id, f"『查背包』\n" + SensitiveWordsFilter.replace(data['inventory']))

    elif data['type'] == "worldfileV2":
        # noinspection PyBroadException
        try:
            result = await create_upload_link(decompress_base64_gzip(data['base64']), data['name'])
            if result['success']:
                if data['name'].endswith('.wld'):
                    await bot.send_to_group(group_id, f"\n『下载地图』\n" +
                                            f"下载成功~\n" +
                                            f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                            f"PC导入路径: %USERPROFILE%/Documents/My Games/Terraria/Worlds\n" +
                                            f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Worlds",
                                            msg_id=msg_id)
                else:
                    await bot.send_to_group(group_id, f"\n『下载地图』\n" +
                                            f"下载成功~\n" +
                                            f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                            f"tMODL导入路径: %USERPROFILE%/Documents/My Games/Terraria/tModLoader/Worlds\n" +
                                            f"TIPS: 需要先解压压缩包哦~",
                                            msg_id=msg_id)
            else:
                await bot.send_to_group(group_id, f"\n『下载地图』\n" +
                                        f"下载失败!\n" +
                                        f"{result['message']}",
                                        msg_id=msg_id)
        except:
            print(traceback.format_exc())

    elif data['type'] == "mapfileV2":
        result = await create_upload_link(decompress_base64_gzip(data['base64']), data['name'])
        if result['success']:
            if data['name'].endswith('.map'):
                await bot.send_to_group(group_id, f"\n『下载小地图』\n" +
                                        f"下载成功~\n" +
                                        f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                        f"PC导入路径: %USERPROFILE%/Documents/My Games/Terraria/Players/玩家名\n"
                                        f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Players/玩家名",
                                        msg_id=msg_id)
            else:
                await bot.send_to_group(group_id, f"\n『下载小地图』\n" +
                                        f"下载成功~\n" +
                                        f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                        f"tMODL导入路径: %USERPROFILE%/Documents/My Games/Terraria/tModLoader/Players/玩家名\n"
                                        f"TIPS: 需要先解压压缩包哦~",
                                        msg_id=msg_id)
        else:
            await bot.send_to_group(group_id, f"\n『下载小地图』\n" +
                                    f"下载失败!\n" +
                                    f"{result['message']}",
                                    msg_id=msg_id)
    elif data['type'] == "pluginlist":
        tshock_plugins = data['plugins']
        tshock_plugins.sort(key=lambda x: x['Name'])
        await bot.send_to_group(group_id, MessageSegment.text(f"\n『插件列表』\n" +
                                                              "\n".join(
                                                                  [
                                                                      f"{SensitiveWordsFilter.replace(i['Name'])} v{i['Version']}"
                                                                      for i in
                                                                      tshock_plugins])),
                                msg_id=msg_id)
    elif data['type'] == "modlist":
        mods = data['mods']
        mods.sort(key=lambda x: x['Name'])
        await bot.send_to_group(group_id, MessageSegment.text(f"\n『TMOD列表』\n" +
                                                              "\n".join(
                                                                  [
                                                                      f"{SensitiveWordsFilter.replace(i['Name'])} v{i['Version']}"
                                                                      for i in
                                                                      mods])),
                                msg_id=msg_id)




logger.success("[API启动]Websocket服务器初始化完成!")
