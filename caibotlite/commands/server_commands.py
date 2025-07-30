import asyncio
import base64
import io
import socket

from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent, MessageSegment

from caibotlite.dependencies import Args, Session, CurrentGroup
from caibotlite.enums import PackageType
from caibotlite.managers import ConnectionManager, GroupManager, UserManager
from caibotlite.models import Server, GroupConfig, Package
from caibotlite.services import LookBag, QueryProcess, FileService, PackageWriter
from caibotlite.utils import decompress_base64_gzip, filter_all, replace_all_tag, build_rank


async def call_server_command(server: Server, server_index: int, package: Package):
    server_num = server_index + 1
    if not ConnectionManager.is_server_online(server.token):
        return f"❌服务器[{server_num}]处于离线状态!"
    try:
        result = await ConnectionManager.call_api(server.token, package)
    except TimeoutError:
        return f"⚠️服务器[{server_num}]响应超时!"
    if result['output']:
        return (f"#️⃣服务器[{server_num}]返回结果:\n"
                f"{filter_all(replace_all_tag('\n'.join(result['output'])))}")
    else:
        return f"#️⃣服务器[{server_num}]返回了个寂寞~"


remote_command = on_command("#", aliases={"远程命令", "远程指令", "c"}, force_whitespace=True, block=True)


@remote_command.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup):
    if GroupManager.has_permission(group, event.author.union_openid):
        if len(args) < 2:
            await remote_command.finish(f'\n『远程指令』\n' +
                                        f"格式错误!正确格式: 远程指令 <服务器序号> <命令内容>")
        server_num = args[0]

        command = " ".join(args[1:])

        if command[0] != "/":
            command = "/" + command

        package_writer = PackageWriter(PackageType.CALL_COMMAND)
        package_writer.write("command", command)
        package_writer.write("group_open_id", event.group_openid)
        package_writer.write("user_open_id", event.author.union_openid)
        package = package_writer.build()
        if server_num == "all" or server_num == "*":
            if len(group.servers) == 0:
                await remote_command.finish(f'\n『远程指令』\n' +
                                            f"你好像还没有绑定服务器捏？")

            tasks = [call_server_command(index, server, package) for server, index
                     in enumerate(group.servers)]
            results = await asyncio.gather(*tasks)
            await remote_command.finish(filter_all('\n『远程指令』\n' +
                                                   "\n".join(results)))

        if not server_num.isdigit() or int(server_num) > len(group.servers):
            await remote_command.finish(f'\n『远程指令』\n' +
                                        f"执行失败！\n" +
                                        f"服务器序号错误!")
        server_index = int(server_num) - 1
        result = await call_server_command(group.servers[server_index], server_index, package)
        await remote_command.finish(filter_all("\n『远程指令』\n" +
                                               f"{result}"))
    else:
        await remote_command.finish(f'\n『远程指令』\n' +
                                    "没有权限!")


async def call_server_online(server: Server, server_index: int, config: GroupConfig, package: Package):
    server_num = server_index + 1
    if not ConnectionManager.is_server_online(server.token):
        return f"๑{server_num}๑❌处于离线状态!"
    try:
        result = await ConnectionManager.call_api(server.token, package)
    except TimeoutError:
        return f"๑{server_num}๑⚠️服务器连接超时!"

    player_list = result['player_list']
    server_name = result['server_name']
    process = f"「{result['process']}」" if result['process'] else ""
    current_online = result['current_online']
    max_online = result['max_online']
    lines = [f"๑{server_num}๑⚡{server_name} {process}"]

    if current_online == 0:
        lines.append(f"没有玩家在线捏...")
        return "\n".join(lines)

    if config.disabled_show_playerlist:
        lines.append(f"当前有{current_online}名玩家在线~")
        return "\n".join(lines)

    lines.append(f"在线玩家({current_online}/{max_online})")
    lines.append(", ".join(player_list))
    return "\n".join(lines)


online = on_command("在线", aliases={"在线人数", "在线查询", "泰拉在线", "查询在线"}, force_whitespace=True, block=True)


@online.handle()
async def _(group: CurrentGroup):
    if len(group.servers) == 0:
        await online.finish(f'\n『泰拉在线』\n' +
                            f"你好像还没有绑定服务器捏？" + "\n*由于CaiBot更新, 请下载最新版适配插件，然后重新添加服务器: \n"
                                                           "https://docs.terraria.ink/zh/other/CaiBotLite.html")

    package_writer = PackageWriter(PackageType.PLAYER_LIST)
    package = package_writer.build()
    tasks = [call_server_online(index, server, group.config, package) for server, index
             in enumerate(group.servers)]
    results = await asyncio.gather(*tasks)
    await online.finish(filter_all('\n『泰拉在线』\n' +
                                   "\n".join(results)))


world_progress = on_command("进度", aliases={"进度查询", "查询进度"}, force_whitespace=True, block=True)


@world_progress.handle()
async def _(args: Args, group: CurrentGroup):
    if len(args) != 1:
        await world_progress.finish(f'\n『进度查询』\n'
                                    f'查询失败！\n' +
                                    f'格式错误！正确格式: 进度查询 [服务器序号]')

    if not GroupManager.check_server_num_ok(group, args[0]):
        await world_progress.finish(f'\n『进度查询』\n' +
                                    f"获取失败！\n" +
                                    f"服务器序号错误!")
    server_number = int(args[0])
    server_index = server_number - 1

    if not ConnectionManager.is_server_online(group.servers[server_index].token):
        await world_progress.finish(f'\n『进度查询』\n' +
                                    f"执行失败！\n" +
                                    f"❌服务器[{server_number}]处于离线状态")

    package_writer = PackageWriter(PackageType.PROGRESS, True)

    payload = await ConnectionManager.call_api(group.servers[server_index].token, package_writer.build())

    if payload['is_text']:
        await world_progress.finish(f'\n『进度查询』\n' +
                                    filter_all(payload['text']))

    progress_img = QueryProcess.get_process_png(payload)
    byte_arr = io.BytesIO()
    progress_img.save(byte_arr, format='PNG')
    await world_progress.finish(MessageSegment.file_image(byte_arr.getvalue()))


async def call_server_self_kick(server: Server, package: Package):
    if not ConnectionManager.is_server_online(server.token):
        return
    await ConnectionManager.send_data(server.token, package)


self_kick = on_command("自踢", aliases={"自提", "自体"}, force_whitespace=True, block=True)


@self_kick.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None:
        await self_kick.finish(f'\n『自踢』\n' +
                               "你还没有添加白名单！\n"
                               f"发送\"/添加白名单 <名字>\"来添加白名单")

    package_writer = PackageWriter(PackageType.SELF_KICK, False)
    package_writer.write("name", user.name)
    package = package_writer.build()
    tasks = [call_server_self_kick(server, package) for server in group.servers]
    await asyncio.gather(*tasks)
    await self_kick.finish(f'\n『自踢』\n' +
                           f"自踢成功！")


get_map_png = on_command("查看地图", force_whitespace=True, block=True)


@get_map_png.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup):
    if not GroupManager.has_permission(group, event.author.union_openid) and not group.config.allow_default_getmapimage:
        await get_map_png.finish(f'\n『查看地图』\n' +
                                 "没有权限!")
    if len(args) != 1:
        await get_map_png.finish(f'\n『查看地图』\n' +
                                 f"格式错误!\n"
                                 f"正确格式: 查看地图 <服务器序号>")
    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_map_png.finish(f'\n『查看地图』\n' +
                                 f"获取失败！\n" +
                                 f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1

    package_writer = PackageWriter(PackageType.MAP_IMAGE)

    if not ConnectionManager.is_server_online(group.servers[server_index].token):
        await get_map_png.finish(f'\n『查看地图』\n' +
                                 f"获取失败！\n" +
                                 f"❌服务器[{server_number}]处于离线状态")

    payload = await ConnectionManager.call_api(group.servers[server_index].token, package_writer.build(), timeout=30.0)
    decoded_bytes = base64.b64decode(decompress_base64_gzip(payload['base64']))
    await world_progress.finish(MessageSegment.file_image(decoded_bytes))


get_world_file = on_command("下载地图", force_whitespace=True, block=True)


@get_world_file.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup):
    if not GroupManager.has_permission(group,
                                       event.author.union_openid) and not group.config.allow_default_getworldfile:
        await get_world_file.finish(f'\n『下载地图』\n' +
                                    "没有权限!")

    if len(args) != 1:
        await get_world_file.finish(f'\n『下载地图』\n' +
                                    f"格式错误!\n" +
                                    f"正确格式: 下载地图 <服务器序号>")

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_world_file.finish(f'\n『下载地图』\n' +
                                    f"获取失败！\n" +
                                    f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.WORLD_FILE)

    if not ConnectionManager.is_server_online(server_token):
        await get_world_file.finish(f'\n『下载地图』\n' +
                                    f"获取失败！\n" +
                                    f"❌服务器[{server_number}]处于离线状态")

    payload = await ConnectionManager.call_api(server_token, package_writer.build(), timeout=30.0)
    result = await FileService.create_upload_link(decompress_base64_gzip(payload['base64']), payload['name'])
    if result['success']:
        if payload['name'].endswith('.wld'):
            await get_world_file.finish(f"\n『下载地图』\n" +
                                        f"下载成功~\n" +
                                        f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                        f"PC导入路径: %USERPROFILE%/Documents/My Games/Terraria/Worlds\n" +
                                        f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Worlds")
        else:
            await get_world_file.finish(f"\n『下载地图』\n" +
                                        f"下载成功~\n" +
                                        f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                        f"tMODL导入路径: %USERPROFILE%/Documents/My Games/Terraria/tModLoader/Worlds\n")
    else:
        await get_world_file.finish(f"\n『下载地图』\n" +
                                    f"下载失败!\n" +
                                    f"{result['message']}")


get_map_file = on_command("下载小地图", force_whitespace=True, block=True)


@get_map_file.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup):
    if not GroupManager.has_permission(group, event.author.union_openid) and not group.config.allow_default_getmapfile:
        await get_map_file.finish(f'\n『下载小地图』\n' +
                                  "没有权限!")

    if len(args) != 1:
        await get_map_file.finish(f'\n『下载小地图』\n' +
                                  f"格式错误!正确格式: 下载小地图 <服务器序号>")

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_map_file.finish(f'\n『下载小地图』\n' +
                                  f"获取失败！\n" +
                                  f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.MAP_FILE)

    if not ConnectionManager.is_server_online(server_token):
        await get_map_file.finish(f'\n『下载小地图』\n' +
                                  f"获取失败！\n"
                                  f"❌服务器[{server_number}]处于离线状态")
    payload = await ConnectionManager.call_api(server_token, package_writer.build(), 30.0)

    result = await FileService.create_upload_link(decompress_base64_gzip(payload['base64']), payload['name'])
    if result['success']:
        if payload['name'].endswith('.map'):
            await get_map_file.finish(f"\n『下载小地图』\n" +
                                      f"下载成功~\n" +
                                      f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                      f"PC导入路径: %USERPROFILE%/Documents/My Games/Terraria/Players/玩家名\n"
                                      f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Players/玩家名")
        else:
            await get_map_file.finish(f"\n『下载小地图』\n" +
                                      f"下载成功~\n" +
                                      f"链接: https://raw.terraria.ink{result['download_url']}\n" +
                                      f"tMODL导入路径: %USERPROFILE%/Documents/My Games/Terraria/tModLoader/Players/玩家名\n"
                                      f"TIPS: 需要先解压压缩包哦~")
    else:
        await get_map_file.finish(f"\n『下载小地图』\n" +
                                  f"下载失败!\n" +
                                  f"{result['message']}")


get_plugin_list = on_command("插件列表", aliases={"模组列表"}, force_whitespace=True, block=True)


@get_plugin_list.handle()
async def _(args: Args, group: CurrentGroup):
    if len(args) != 1:
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"格式错误!\n"
                                     f"正确格式: 插件列表 <服务器序号>")

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"获取失败！\n" +
                                     f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.PLUGIN_LIST)

    if not ConnectionManager.is_server_online(server_token):
        await get_plugin_list.finish(f'\n『插件列表』\n' +
                                     f"获取失败！\n" +
                                     f"❌服务器[{server_number}]处于离线状态")
    payload = await ConnectionManager.call_api(server_token, package_writer.build())
    is_mod = payload['is_mod']
    plugins = payload['plugins']
    plugins.sort(key=lambda x: x['Name'])
    await get_plugin_list.finish(filter_all(f"\n『{'MOD' if is_mod else '插件'}列表』\n" +
                                            f"\n".join(
                                                [f"{(replace_all_tag(i['Name']))} v{i['Version']}" for i in plugins])))


look_bag = on_command("查背包", aliases={"查看背包", "查询背包"}, force_whitespace=True, block=True)


@look_bag.handle()
async def _(args: Args, group: CurrentGroup):
    if len(args) != 2:
        await look_bag.finish(f'\n『查背包』\n' +
                              f"格式错误!\n" +
                              f"正确格式: 查背包 <服务器序号> <玩家名>")

    if not GroupManager.check_server_num_ok(group, args[0]):
        await look_bag.finish(f'\n『查背包』\n' +
                              f"查询失败！\n" +
                              f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token
    player_name = args[1]

    package_writer = PackageWriter(PackageType.LOOK_BAG)
    package_writer.write("player_name", player_name)

    if not ConnectionManager.is_server_online(server_token):
        await look_bag.finish(f'\n『查背包』\n' +
                              f"查询失败！\n" +
                              f"❌服务器[{server_number}]处于离线状态")
    payload = await ConnectionManager.call_api(server_token, package_writer.build())
    if payload['exist'] == 0:
        await look_bag.finish(f"\n『查背包』\n" +
                              f"查询失败!\n" +
                              f"查询的玩家不存在！")
    if payload['is_text']:
        await  look_bag.finish(f"\n『查背包』\n" +
                               filter_all(payload['text']))

    img = LookBag.get_bag_png(payload)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    await look_bag.finish(MessageSegment.file_image(byte_arr.getvalue()))


rank = on_command("排行", force_whitespace=True, block=True)


@rank.handle()
async def _(args: Args, group: CurrentGroup):
    if 1 > len(args) or len(args) > 4:
        await rank.finish(f'\n『排行』\n' +
                          f"格式错误!\n" +
                          f"正确格式: 排行 <服务器序号> <项目> [参数] [页码]")

    if not GroupManager.check_server_num_ok(group, args[0]):
        await  rank.finish(f'\n『排行』\n' +
                           f"获取失败！\n" +
                           f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.RANK_DATA)

    if len(args) == 1:
        package_writer.write("rank_type", "")
        package_writer.write("arg", "")
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
        await  rank.finish(filter_all(f'\n『排行』\n' +
                                      f"无效排行！\n" +
                                      f"当前服务器支持的排行榜类型: " +
                                      f", ".join(payload["support_rank_types"])))

    rank_type = args[1]
    if len(args) == 3:
        arg = args[2]
    else:
        arg = ""
    page = 1

    package_writer.write("rank_type", rank_type)
    package_writer.write("arg", arg)

    if not ConnectionManager.is_server_online(server_token):
        await  rank.finish(f'\n『排行』\n' +
                           f"获取失败！\n"
                           f"❌服务器[{server_number}]处于离线状态")

    payload = await ConnectionManager.call_api(server_token, package_writer.build())

    if not payload["rank_type_support"]:
        await  rank.finish(filter_all(f'\n『排行』\n' +
                                      f"无效排行！\n" +
                                      f"当前服务器支持的排行榜类型: " +
                                      f", ".join(payload["support_rank_types"])))
    if payload["need_arg"]:
        if len(args) == 4 and arg[3].isdigit():
            page = int(arg[3])
        if not payload["arg_support"]:
            await rank.finish(filter_all(f'\n『排行』\n' +
                                         payload["message"]) +
                              f", ".join(payload["support_args"]))
    else:
        if len(args) == 3 and arg[2].isdigit():
            page = int(arg[2])

    rank_data = payload["rank"]
    rank_lines = dict(rank_data["rank_lines"])
    await  rank.finish(filter_all(f'\n『{rank_data["title"]}』\n' +
                                  build_rank(rank_lines, page)))


server_list = on_command("服务器列表", aliases={"ip", "IP"}, force_whitespace=True, block=True)


@server_list.handle()
async def _(group: CurrentGroup):
    results = []
    for index, server in enumerate(group.servers):
        server_number = index + 1
        if ConnectionManager.is_server_online(server.token):
            # noinspection PyBroadException
            try:
                ip = socket.gethostbyname(server.ip)
            except:
                ip = server.ip
            info = ConnectionManager.connected_servers[server.token].server_info
            white_list = "[白名单]" if info.enable_whitelist else ""
            results.append(f"๑{server_number}๑🌐{info.server_name}{white_list}({info.game_version})\n"
                           f"地址: {filter_all(ip)}\n"
                           f"端口: {server.port}")
        else:
            results.append(f"๑{server_number}๑❌服务器处于离线状态")
    await server_list.finish(f'\n『泰拉在线』\n' +
                             "\n".join(results))


server_info = on_command("服务器信息", force_whitespace=True, block=True)


@server_info.handle()
async def _(args: Args, group: CurrentGroup):
    if len(args) != 1:
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"格式错误!\n"
                                 f"正确格式: 服务器信息 <服务器序号>")
    if not GroupManager.check_server_num_ok(group, args[0]):
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"服务器序号错误!")

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    if not ConnectionManager.is_server_online(server_token):
        await server_info.finish(f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"❌服务器[{server_number}]处于离线状态")

    server = ConnectionManager.connected_servers[server_token]
    server_version = server.server_info.game_version
    world = server.server_info.server_name
    tshock_version = server.server_info.server_core_version
    whitelist = server.server_info.enable_whitelist
    plugin_version = server.server_info.plugin_version
    os = server.server_info.system
    # noinspection PyBroadException
    try:
        ip = socket.gethostbyname(server.ip)
    except Exception:
        ip = server.ip
    await server_info.finish(filter_all(f'\n『服务器信息』\n' +
                                        f"服务器[{server_number}]的详细信息: \n"
                                        f"地址: {filter_all(ip)}:{server.port}\n"
                                        f"世界名: {world}\n"
                                        f"游戏版本: {server_version}\n"
                                        f"{server.type}版本: {tshock_version}\n"
                                        f"CaiBot扩展版本: {plugin_version}\n"
                                        f"Cai白名单: {whitelist}\n"
                                        f"服务器系统: {os}\n"
                                        f"所属群: {server.group_open_id}\n"))
