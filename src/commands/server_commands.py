import socket

from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from src.models.group import Group
from src.utils.group_helper import GroupHelper
from src.utils.sensitive_words_filter import SensitiveWordsFilter
from src.models.user import User
from src.cai_api import wait_for_online, server_connection_manager, wait_for_cmd


def msg_cut(msg: str) -> list:
    msg = msg.split(" ")
    msg = [word for word in msg if word]
    return msg


def paginate(data, page_size, page_number):
    # 计算开始和结束的索引
    start = (page_number - 1) * page_size
    end = start + page_size
    # 返回分页后的数据
    return data[start:end]


remote_command = on_command("#", aliases={"远程命令", "远程指令", "c"}, force_whitespace=True)


@remote_command.handle()
async def remote_command_handle(event: GroupAtMessageCreateEvent):
    msg = event.get_plaintext().split(" ", 2)
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        if len(msg) != 3 or msg[2] == "":
            await remote_command.finish(f'\n『远程指令』\n' +
                                        f"格式错误!正确格式: 远程指令 <服务器序号> <命令内容>")
        if msg[2][0] != "/":
            msg[2] = "/" + msg[2]
        cmd = {
            "type": "cmd",
            "cmd": msg[2],
            "at": str(event.author.union_openid),
            "group": event.group_openid,
            "msg_id": event.id
        }
        if msg[1] == "all" or msg[1] == "*":
            if len(group.servers) == 0:
                await remote_command.finish(f'\n『远程指令』\n' +
                                            f"你好像还没有绑定服务器捏？")
            result = await wait_for_cmd(event.group_openid, cmd, group.servers)

            await remote_command.finish(f'\n『远程指令』\n' +
                                        "\n".join(result))
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await remote_command.finish(f'\n『远程指令』\n' +
                                        f"执行失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await remote_command.finish(f'\n『远程指令』\n' +
                                        f"执行失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
    else:
        await remote_command.finish(f'\n『远程指令』\n' +
                                    "没有权限!")


online = on_command("在线", aliases={"在线人数", "在线查询", "泰拉在线", "查询在线"}, force_whitespace=True)


@online.handle()
async def remote_command_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    if len(group.servers) == 0:
        await online.finish(f'\n『泰拉在线』\n' +
                            f"你好像还没有绑定服务器捏？")
    result = await wait_for_online(event.group_openid, group.servers)

    await online.finish(f'\n『泰拉在线』\n' +
                        "\n".join(result))


world_progress = on_command("进度", aliases={"进度查询", "查询进度"}, force_whitespace=True)


@world_progress.handle()
async def world_progress_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) == 2:
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await world_progress.finish(f'\n『进度查询』\n' +
                                        f"获取失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await world_progress.finish(f'\n『进度查询』\n' +
                                        f"执行失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        cmd = {
            "type": "bosses",
            "group": event.group_openid,
            "msg_id": event.id
        }
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
    else:
        await world_progress.finish(f'\n『进度查询』\n'
                                    f'查询失败！\n'
                                    f'格式错误！正确格式: 进度查询 [服务器序号]')


self_kick = on_command("自踢", aliases={"自提", "自体"}, force_whitespace=True)


@self_kick.handle()
async def self_kick_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    user = User.get_user(group.open_id, event.author.union_openid)
    if user is None:
        await self_kick.finish(f'\n『自踢』\n' +
                               "你还没有添加白名单！\n"
                               f"发送'/添加白名单 <名字>'来添加白名单")
    cmd = {
        "type": "selfkick",
        "group": event.group_openid,
        "name": user.name
    }
    for i in group.servers:
        await server_connection_manager.send_data(i.token, cmd, event.group_openid)
    await self_kick.finish(f'\n『自踢』\n' +
                           f"自踢成功！")


get_map_png = on_command("查看地图", force_whitespace=True)


@get_map_png.handle()
async def get_map_png_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        if len(msg) != 2:
            await get_map_png.finish(f'\n『查看地图』\n' +
                                     f"格式错误!\n"
                                     f"正确格式: 查看地图 <服务器序号>")
        cmd = {
            "type": "mappng",
            "group": event.group_openid,
            "msg_id": event.id
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_map_png.finish(f'\n『查看地图』\n' +
                                     f"获取失败！\n"
                                     f"服务器序号错误!")

        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_map_png.finish(f'\n『查看地图』\n' +
                                     f"获取失败！\n"
                                     f"❌服务器[{int(msg[1])}]处于离线状态")
        # try:
        #     server = server_connection_manager.get_server_connection(group_id.servers[int(msg[1]) - 1].token)
        #     if server.terraria_version.startswith("tModLoader"):
        #         await get_map_png.finish(f'\n『查看地图』\n' +
        #                                  f"获取失败！\n"
        #                                  f"❌不支持tModLoader服务器")
        # except:
        #     pass

        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
    else:
        await get_map_png.finish(f'\n『查看地图』\n' +
                                 "没有权限!")


get_world_file = on_command("下载地图", force_whitespace=True)


@get_world_file.handle()
async def get_world_file_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        if len(msg) != 2:
            await get_world_file.finish(f'\n『下载地图』\n' +
                                        f"格式错误!\n"
                                        f"正确格式: 下载地图 <服务器序号>")
        cmd = {
            "type": "worldfile",
            "group": event.group_openid,
            "msg_id": event.id
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_world_file.finish(f'\n『下载地图』\n' +
                                        f"获取失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_world_file.finish(f'\n『下载地图』\n' +
                                        f"获取失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
    else:
        await get_world_file.finish(f'\n『下载地图』\n' +
                                    "没有权限!")


get_map_file = on_command("下载小地图", force_whitespace=True)


@get_map_file.handle()
async def get_world_file_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        if len(msg) != 2:
            await get_map_file.finish(f'\n『下载小地图』\n' +
                                      f"格式错误!正确格式: 下载小地图 <服务器序号>")
        cmd = {
            "type": "mapfile",
            "group": event.group_openid,
            "msg_id": event.id
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_map_file.finish(f'\n『下载小地图』\n' +
                                      f"获取失败！\n"
                                      f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_map_file.finish(f'\n『下载小地图』\n' +
                                      f"获取失败！\n"
                                      f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
    else:
        await get_map_file.finish(f'\n『下载小地图』\n' +
                                  "没有权限!")


get_plugin_list = on_command("插件列表", aliases={"模组列表"}, force_whitespace=True)


@get_plugin_list.handle()
async def get_plugin_list_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    if len(msg) != 2:
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"格式错误!\n"
                                     f"正确格式: 插件列表 <服务器序号>")
    cmd = {
        "type": "pluginlist",
        "group": event.group_openid,
        "msg_id": event.id
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"获取失败！\n"
                                     f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"获取失败！\n"
                                     f"❌服务器[{int(msg[1])}]处于离线状态")
    await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)


look_bag = on_command("查背包", aliases={"查看背包", "查询背包"}, force_whitespace=True)


@look_bag.handle()
async def look_bag_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 3:
        await look_bag.finish(f'\n『查背包』\n' +
                              f"格式错误!\n"
                              f"正确格式: 查背包 <服务器序号> <玩家名>")
    cmd = {
        "type": "lookbag",
        "name": msg[2],
        "group": event.group_openid,
        "msg_id": event.id
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await look_bag.finish(f'\n『查背包』\n' +
                              f"查询失败！\n"
                              f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await look_bag.finish(f'\n『查背包』\n' +
                              f"查询失败！\n"
                              f"❌服务器[{int(msg[1])}]处于离线状态")
    await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)


server_list = on_command("服务器列表", aliases={"ip", "IP"}, force_whitespace=True)


@server_list.handle()
async def server_list_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    result = []
    index = 1
    for i in group.servers:
        if server_connection_manager.server_available(i.token):
            # noinspection PyBroadException
            try:
                ip = socket.gethostbyname(i.ip)
            except:
                ip = i.ip
            server = server_connection_manager.get_server_connection(i.token)
            server_version = server.terraria_version
            world = server.world
            if server.whitelist:
                white_list = "[白名单]"
            else:
                white_list = ""
            result.append(f"๑{index}๑🌐{world}{white_list}({server_version})\n"
                          f"地址: {SensitiveWordsFilter.replace(ip)}\n"
                          f"端口: {i.port}")


        else:
            result.append(f"๑{index}๑❌服务器处于离线状态")
        index += 1
    await server_list.finish(f'\n『泰拉在线』\n' +
                             "\n".join(result))


server_info = on_command("服务器信息", force_whitespace=True)


@server_info.handle()
async def server_info_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"格式错误!\n"
                                 f"正确格式: 服务器信息 <服务器序号>")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"❌服务器[{int(msg[1])}]处于离线状态")
    i = group.servers[int(msg[1]) - 1]
    server = server_connection_manager.get_server_connection(i.token)
    server_version = server.terraria_version
    world = server.world
    tshock_version = server.tshock_version
    whitelist = server.whitelist
    plugin_version = server.plugin_version
    os = server.os
    # noinspection PyBroadException
    try:
        ip = socket.gethostbyname(i.ip)
    except Exception:
        ip = i.ip
    await server_info.finish(f'\n『服务器信息』\n' +
                           f"服务器[{int(msg[1])}]的详细信息: \n"
                           f"地址: {SensitiveWordsFilter.replace(ip)}:{i.port}\n"
                           f"世界名: {world}\n"
                           f"Terraria版本: {server_version}\n"
                           f"TShock版本: {tshock_version}\n"
                           f"CaiBot扩展版本: {plugin_version}\n"
                           f"Cai白名单: {whitelist}\n"
                           f"服务器系统: {os}\n"
                           f"所属群: {i.owner}\n"
                           f"共享群: {'无' if not i.shared else ','.join(map(str, i.shared))}")
