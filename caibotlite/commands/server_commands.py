import asyncio
import base64
import io
import socket

from nonebot import on_command
from nonebot.adapters.qq import (
    GroupAtMessageCreateEvent,
    MessageSegment,
    GroupMessageCreateEvent,
)

from caibotlite.dependencies import Args, Session, CurrentGroup
from caibotlite.enums import PackageType, ServerType
from caibotlite.managers import ConnectionManager, GroupManager, UserManager
from caibotlite.markdown.image import get_users_avatar
from caibotlite.markdown.keyboard import (
    help_doc_keyboard,
    reedit_keyboard,
    download_keyboard,
    rank_page_keyboard,
    add_whitelist_keyboard,
)
from caibotlite.markdown.tag import cmd_input_tag, copy_link_tag
from caibotlite.models import Server, GroupConfig, Package, Group, ServerInfo
from caibotlite.models.server_error_exception import ServerError
from caibotlite.services import LookBag, QueryProcess, FileService, PackageWriter
from caibotlite.utils import (
    decompress_base64_gzip,
    filter_all,
    replace_all_tag,
    build_rank,
)
from caibotlite.utils.process import get_process_icon


async def call_server_command(server: Server, server_index: int, package: Package):
    server_num = server_index + 1
    if not ConnectionManager.is_server_online(server.token):
        return f"**❌服务器[{server_num}]处于离线状态!**"
    try:
        result = await ConnectionManager.call_api(server.token, package)
    except ServerError as ex:
        return f"**⚠️ 服务器[{server_num}]内部错误:**\n{ex.error}"
    except TimeoutError:
        return f"**⚠️ 服务器[{server_num}]响应超时!**"
    if result["output"]:
        return (
            f"**#️⃣服务器[{server_num}]返回结果:**\n"
            f"{replace_all_tag('\n'.join([f'> **{filter_all(i.strip())}**' for i in result['output']]))}"
        )
    else:
        return f"**#️⃣服务器[{server_num}]返回了个寂寞~**"


remote_command = on_command(
    "#", aliases={"远程命令", "远程指令", "c"}, force_whitespace=True, block=True
)


@remote_command.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if GroupManager.has_permission(group, event.author.union_openid):
        if len(args) < 2:
            await remote_command.finish(
                MessageSegment.markdown(
                    "## 🍥 远程指令\n"
                    "格式错误！\n"
                    f"正确格式: {cmd_input_tag('/远程指令')} `<服务器序号>` `<命令内容>`"
                )
                + reedit_keyboard(event.get_plaintext())
            )
        server_num = args[0]

        raw_command = " ".join(args[1:])
        command = raw_command

        if command[0] != "/":
            command = "/" + command

        package_writer = PackageWriter(PackageType.CALL_COMMAND)
        package_writer.write("command", command)
        package_writer.write("group_open_id", event.group_openid)
        package_writer.write("user_open_id", event.author.union_openid)
        package = package_writer.build()
        if server_num == "all" or server_num == "*":
            if len(group.servers) == 0:
                await remote_command.finish(
                    MessageSegment.markdown(
                        "## 🍥 远程指令\n> 你好像还没有绑定服务器捏？"
                    )
                )

            tasks = [
                call_server_command(index, server, package)
                for server, index in enumerate(group.servers)
            ]
            results = await asyncio.gather(*tasks)

            await remote_command.finish(
                MessageSegment.markdown("## 🍥 远程指令\n" + "\n\n".join(results))
                + reedit_keyboard(event.get_plaintext())
            )

        if not server_num.isdigit() or int(server_num) > len(group.servers):
            await remote_command.finish(
                MessageSegment.markdown(f"## 🍥 远程指令\n" + f"服务器序号错误！")
                + reedit_keyboard(event.get_plaintext())
            )

        server_index = int(server_num) - 1
        result = await call_server_command(
            group.servers[server_index], server_index, package
        )
        await remote_command.finish(
            MessageSegment.markdown(f"## 🍥 远程指令\n" + f"{result}")
            + reedit_keyboard(event.get_plaintext())
        )
    else:
        await remote_command.finish(
            MessageSegment.markdown(f"## 🍥 远程指令\n" + f"没有权限！")
        )


async def call_server_online(
    server: Server,
    group: Group,
    server_index: int,
    config: GroupConfig,
    package: Package,
):
    server_num = server_index + 1
    if not ConnectionManager.is_server_online(server.token):
        return f"**๑{server_num}๑ ❌处于离线状态!**"
    try:
        result = await ConnectionManager.call_api(server.token, package)
    except ServerError as ex:
        return f"**๑{server_num}๑ ⚠️ 服务器内部错误:**\n{ex.error}"

    except TimeoutError:
        return f"**๑{server_num}๑ ⚠️ 服务器响应超时!**"

    player_list = result["player_list"]
    server_name = filter_all(result["server_name"])
    process_icon = get_process_icon(result["process"])
    if process_icon:
        process = (
            f" 「{process_icon} {filter_all(result['process'])}」"
            if result["process"]
            else ""
        )
    else:
        process = f" 「{filter_all(result['process'])}」" if result["process"] else ""
    current_online = int(result["current_online"])
    max_online = int(result["max_online"])
    ConnectionManager.connected_servers[
        server.token
    ].server_info.server_name = server_name
    lines = [f"**๑{server_num}๑ ⚡{server_name}{process}**"]

    def version_warning():
        _server_info: ServerInfo = ConnectionManager.connected_servers[
            server.token
        ].server_info

        if _server_info is None:
            return

        version = tuple(map(int, _server_info.plugin_version.split('.')))

        if version == (2026, 1, 29, 0) and _server_info.type == ServerType.TSHOCK:
            lines.append("⚠️ 此适配插件版本具有严重Bug，建议升级")

        if version < (2026, 7, 7, 0) and _server_info.type == ServerType.TSHOCK:
            lines.append("⚠️ 此适配插件版本具有严重白名单漏洞，建议升级 (APM/CaiBotLite群文件)")

    if current_online == 0:
        lines.append(f"没有玩家在线捏...")
        version_warning()
        return "\n".join(lines)

    if config.disabled_show_playerlist:
        lines.append(f"当前有**{current_online}**名玩家在线~")
        version_warning()
        return "\n".join(lines)

    lines.append(f"在线玩家(**{current_online}**/{max_online})")

    server = ConnectionManager.connected_servers[server.token]
    if server.server_info.enable_whitelist:
        user_avatars = await get_users_avatar(group.open_id, player_list)
        players = ""
        for player_name in player_list:
            avatar = user_avatars.get(player_name, "")
            players += (
                f"{avatar} {filter_all(player_name)}\t\t"
                if avatar
                else f"{filter_all(player_name)}\t\t"
            )
        lines.append(players)
    else:
        lines.append(", ".join(player_list))

    version_warning()
    return "\n\n".join(lines)


online = on_command("在线", force_whitespace=True, block=True)


@online.handle()
async def _(group: CurrentGroup):
    if len(group.servers) == 0:
        await online.finish(
            MessageSegment.markdown("# 🍥 泰拉在线\n> 你好像还没有绑定服务器捏？")
            + help_doc_keyboard
        )

    package_writer = PackageWriter(PackageType.PLAYER_LIST)
    package = package_writer.build()
    tasks = [
        call_server_online(index, group, server, group.config, package)
        for server, index in enumerate(group.servers)
    ]
    results = await asyncio.gather(*tasks)
    await online.finish(MessageSegment.markdown("# 🍥 泰拉在线\n" + "\n".join(results)))


world_progress = on_command(
    "进度", aliases={"进度查询", "查询进度"}, force_whitespace=True, block=True
)


@world_progress.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if len(args) != 1:
        await world_progress.finish(
            MessageSegment.markdown(
                "## 🍥 进度查询\n"
                + f"格式错误！\n"
                + f"正确格式: {cmd_input_tag('/进度查询')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await world_progress.finish(
            MessageSegment.markdown("## 🍥 进度查询\n" + "服务器序号错误！")
        )
    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    if not ConnectionManager.is_server_online(server_token):
        await world_progress.finish(
            MessageSegment.markdown(
                "## 🍥 进度查询\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    package_writer = PackageWriter(PackageType.PROGRESS, True)

    try:
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
    except ServerError as ex:
        await world_progress.finish(
            MessageSegment.markdown(
                "## 🍥 进度查询\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return

    except TimeoutError:
        await world_progress.finish(
            MessageSegment.markdown("## 🍥 进度查询\n" + "⚠️ 服务器响应超时")
        )
        return

    if payload["is_text"]:
        await world_progress.finish(
            MessageSegment.markdown(
                "## 🍥 进度查询\n" + replace_all_tag(filter_all(payload["text"]))
            )
        )

    progress_img = QueryProcess.get_process_png(payload)
    byte_arr = io.BytesIO()
    progress_img.save(byte_arr, format="PNG")
    await world_progress.finish(MessageSegment.file_image(byte_arr.getvalue()))


async def call_server_self_kick(server: Server, package: Package):
    if not ConnectionManager.is_server_online(server.token):
        return
    await ConnectionManager.send_data(server.token, package)


self_kick = on_command(
    "自踢", aliases={"自提", "自体"}, force_whitespace=True, block=True
)


@self_kick.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    group: CurrentGroup,
    session: Session,
):
    user = await UserManager.get_user_by_open_id(
        session, group.open_id, event.author.union_openid
    )
    if user is None:
        await self_kick.finish(
            MessageSegment.markdown(
                "## 🍥 自踢\n"
                + "你还没有添加白名单！\n"
                + f'发送"{cmd_input_tag("/添加白名单")} `<名字>`"来添加白名单'
            )
            + add_whitelist_keyboard
        )

    package_writer = PackageWriter(PackageType.SELF_KICK, False)
    package_writer.write("name", user.name)
    package = package_writer.build()
    tasks = [call_server_self_kick(server, package) for server in group.servers]
    await asyncio.gather(*tasks)
    await self_kick.finish(MessageSegment.markdown("## 🍥 自踢\n" + "自踢成功！"))


get_map_png = on_command("查看地图", force_whitespace=True, block=True)


@get_map_png.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if (
        not GroupManager.has_permission(group, event.author.union_openid)
        and not group.config.allow_default_getmapimage
    ):
        await get_map_png.finish(
            MessageSegment.markdown("## 🍥 查看地图\n" + "没有权限！")
        )
    if len(args) != 1:
        await get_map_png.finish(
            MessageSegment.markdown(
                "## 🍥 查看地图\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/查看地图')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )
    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_map_png.finish(
            MessageSegment.markdown("## 🍥 查看地图\n" + "服务器序号错误！")
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.MAP_IMAGE)

    if not ConnectionManager.is_server_online(server_token):
        await get_map_png.finish(
            MessageSegment.markdown(
                "## 🍥 查看地图\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(
            server_token, package_writer.build(), timeout=60.0
        )
    except ServerError as ex:
        await get_map_png.finish(
            MessageSegment.markdown(
                "## 🍥 查看地图\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await get_map_png.finish(
            MessageSegment.markdown("## 🍥 查看地图\n" + "⚠️ 服务器响应超时！")
        )
        return

    decoded_bytes = base64.b64decode(decompress_base64_gzip(payload["base64"]))
    await world_progress.finish(MessageSegment.file_image(decoded_bytes))


get_world_file = on_command("下载地图", force_whitespace=True, block=True)


@get_world_file.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if (
        not GroupManager.has_permission(group, event.author.union_openid)
        and not group.config.allow_default_getworldfile
    ):
        await get_world_file.finish(
            MessageSegment.markdown("## 🍥 下载地图\n" + "没有权限！")
        )

    if len(args) != 1:
        await get_world_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载地图\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/下载地图')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_world_file.finish(
            MessageSegment.markdown("## 🍥 下载地图\n" + "服务器序号错误！")
            + reedit_keyboard(event.get_plaintext())
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.WORLD_FILE)

    if not ConnectionManager.is_server_online(server_token):
        await get_world_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载地图\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(
            server_token, package_writer.build(), timeout=60.0
        )
    except ServerError as ex:
        await get_world_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载地图\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await get_world_file.finish(
            MessageSegment.markdown("## 🍥 下载地图\n" + "⚠️ 服务器响应超时")
        )
        return

    result = await FileService.create_upload_link(
        decompress_base64_gzip(payload["base64"]), payload["name"]
    )
    if result["success"]:
        if payload["name"].endswith(".wld"):
            await get_world_file.finish(
                MessageSegment.markdown(
                    "## 🍥 下载地图\n"
                    + "- **PC**导入路径: `%USERPROFILE%/Documents/My Games/Terraria/Worlds`\n"
                    + "- **PE**导入路径: `Android/data/com.and.games505.TerrariaPaid/Worlds`"
                )
                + download_keyboard(f"https://raw.terraria.ink{result['download_url']}")
            )
        else:
            await get_world_file.finish(
                MessageSegment.markdown(
                    "## 🍥 下载地图\n"
                    + "- **tMODL**导入路径: `%USERPROFILE%/Documents/My Games/Terraria/tModLoader/Worlds`\n"
                    "- **RAL**导入路径: `RALauncher/Terraria/tModLoader/Players/玩家名`\n"
                    + "> 需要先解压压缩包哦~"
                )
                + download_keyboard(f"https://raw.terraria.ink{result['download_url']}")
            )
    else:
        await get_world_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载地图\n下载失败！\n" + filter_all(result["message"])
            )
        )


get_map_file = on_command("下载小地图", force_whitespace=True, block=True)


@get_map_file.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if (
        not GroupManager.has_permission(group, event.author.union_openid)
        and not group.config.allow_default_getmapfile
    ):
        await get_map_file.finish(
            MessageSegment.markdown("## 🍥 下载小地图\n" + "没有权限！")
        )

    if len(args) != 1:
        await get_map_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载小地图\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/下载小地图')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_map_file.finish(
            MessageSegment.markdown("## 🍥 下载小地图\n" + "服务器序号错误！")
            + reedit_keyboard(event.get_plaintext())
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.MAP_FILE)

    if not ConnectionManager.is_server_online(server_token):
        await get_map_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载小地图\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(
            server_token, package_writer.build(), 60.0
        )
    except ServerError as ex:
        await get_map_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载小地图\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await get_map_file.finish(
            MessageSegment.markdown("## 🍥 下载小地图\n" + "⚠️ 服务器响应超时")
        )
        return

    result = await FileService.create_upload_link(
        decompress_base64_gzip(payload["base64"]), payload["name"]
    )
    if result["success"]:
        if payload["name"].endswith(".map"):
            await get_map_file.finish(
                MessageSegment.markdown(
                    "## 🍥 下载小地图\n"
                    + "- **PC**导入路径: `%USERPROFILE%/Documents/My Games/Terraria/Players/玩家名`\n"
                    + "- **PE**导入路径: `Android/data/com.and.games505.TerrariaPaid/Players/玩家名`"
                )
                + download_keyboard(f"https://raw.terraria.ink{result['download_url']}")
            )
        else:
            await get_map_file.finish(
                MessageSegment.markdown(
                    "## 🍥 下载小地图\n"
                    + "- **tMODL**导入路径: `%USERPROFILE%/Documents/My Games/Terraria/tModLoader/Players/玩家名`\n"
                    + "- **RAL**导入路径: `RALauncher/Terraria/tModLoader/Players/玩家名`\n"
                    + "> 需要先解压压缩包哦~"
                )
                + download_keyboard(f"https://raw.terraria.ink{result['download_url']}")
            )
    else:
        await get_map_file.finish(
            MessageSegment.markdown(
                "## 🍥 下载小地图\n下载失败！\n" + filter_all(result["message"])
            )
        )


get_plugin_list = on_command(
    "插件列表", aliases={"模组列表"}, force_whitespace=True, block=True
)


@get_plugin_list.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if len(args) != 1:
        await get_plugin_list.finish(
            MessageSegment.markdown(
                "## 🍥 插件列表\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/插件列表')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await get_plugin_list.finish(
            MessageSegment.markdown("## 🍥 插件列表\n" + "服务器序号错误！")
            + reedit_keyboard(event.get_plaintext())
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.PLUGIN_LIST)

    if not ConnectionManager.is_server_online(server_token):
        await get_plugin_list.finish(
            MessageSegment.markdown(
                "## 🍥 插件列表\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
    except ServerError as ex:
        await get_plugin_list.finish(
            MessageSegment.markdown(
                "## 🍥 插件列表\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await get_plugin_list.finish(
            MessageSegment.markdown("## 🍥 插件列表\n" + "⚠️ 服务器响应超时")
        )
        return

    is_mod = payload["is_mod"]
    plugins = payload["plugins"]
    plugins.sort(key=lambda x: x["Name"])
    await get_plugin_list.finish(
        MessageSegment.markdown(
            f"## 🍥 {'MOD' if is_mod else '插件'}列表\n"
            + "\n".join(
                [
                    filter_all(f"- {replace_all_tag(i['Name'])} v{i['Version']}")
                    for i in plugins
                ]
            )
        )
    )


look_bag = on_command(
    "查背包", aliases={"查看背包", "查询背包"}, force_whitespace=True, block=True
)


@look_bag.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if len(args) != 2:
        await look_bag.finish(
            MessageSegment.markdown(
                "## 🍥 查背包\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/查背包')} `<服务器序号>` `<玩家名>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await look_bag.finish(
            MessageSegment.markdown("## 🍥 查背包\n" + "服务器序号错误！\n")
            + reedit_keyboard(event.get_plaintext())
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token
    player_name = args[1]

    package_writer = PackageWriter(PackageType.LOOK_BAG)
    package_writer.write("player_name", player_name)

    if not ConnectionManager.is_server_online(server_token):
        await look_bag.finish(
            MessageSegment.markdown(
                "## 🍥 查背包\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
    except ServerError as ex:
        await look_bag.finish(
            MessageSegment.markdown(
                "## 🍥 查背包\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await look_bag.finish(
            MessageSegment.markdown("## 🍥 查背包\n" + "⚠️ 服务器响应超时")
        )
        return

    if payload["exist"] == 0:
        await look_bag.finish(
            MessageSegment.markdown("## 🍥 查背包\n" + "查询的玩家不存在！")
        )
    if payload["is_text"]:
        await look_bag.finish(
            MessageSegment.markdown(
                "## 🍥 查背包\n" + replace_all_tag(filter_all(payload["text"]))
            )
        )

    img = LookBag.get_bag_png(payload)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format="PNG")
    await look_bag.finish(MessageSegment.file_image(byte_arr.getvalue()))


rank = on_command("排行", force_whitespace=True, block=True)


@rank.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if 1 > len(args) or len(args) > 4:
        await rank.finish(
            MessageSegment.markdown(
                "## 🍥 排行\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/排行')} `<服务器序号>` `<项目>` `[参数]` `[页码]`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    if not GroupManager.check_server_num_ok(group, args[0]):
        await rank.finish(
            MessageSegment.markdown("## 🍥 排行\n" + "服务器序号错误！")
            + reedit_keyboard(event.get_plaintext())
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    package_writer = PackageWriter(PackageType.RANK_DATA)

    if len(args) == 1:
        package_writer.write("rank_type", "")
        package_writer.write("arg", "")
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
        await rank.finish(
            MessageSegment.markdown(
                "## 🍥 排行\n"
                + "无效排行！\n"
                + f"当前服务器支持的排行榜类型: **{filter_all(', '.join(payload['support_rank_types']))}**"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    rank_type = args[1]
    if len(args) >= 3:
        arg = args[2]
    else:
        arg = ""
    page = 1

    package_writer.write("rank_type", rank_type)
    package_writer.write("arg", arg)

    if not ConnectionManager.is_server_online(server_token):
        await rank.finish(
            MessageSegment.markdown(
                "## 🍥 排行\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

    try:
        payload = await ConnectionManager.call_api(server_token, package_writer.build())
    except ServerError as ex:
        await rank.finish(
            MessageSegment.markdown(
                "## 🍥 排行\n" + f"⚠️ 服务器内部错误:\n{filter_all(ex.error)}"
            )
        )
        return
    except TimeoutError:
        await rank.finish(MessageSegment.markdown("## 🍥 排行\n" + "⚠️ 服务器响应超时"))
        return

    if not payload["rank_type_support"]:
        await rank.finish(
            MessageSegment.markdown(
                "## 🍥 排行\n"
                + "无效排行！\n"
                + f"当前服务器支持的排行榜类型: **{filter_all(', '.join(payload['support_rank_types']))}**"
            )
            + reedit_keyboard(event.get_plaintext())
        )
    if payload["need_arg"]:
        if len(args) == 4 and args[3].isdigit():
            page = int(args[3])

        if not payload["arg_support"]:
            await rank.finish(
                MessageSegment.markdown(
                    "## 🍥 排行\n"
                    + filter_all(payload["message"])
                    + "\n"
                    + f"支持参数: **{filter_all(', '.join(payload['support_args']))}**"
                )
                + reedit_keyboard(event.get_plaintext())
            )
    else:
        if len(args) == 3 and args[2].isdigit():
            page = int(args[2])
        arg = None

    rank_data = payload["rank"]
    rank_lines = dict(rank_data["rank_lines"])
    await rank.finish(
        MessageSegment.markdown(
            f"## 🍥 {filter_all(rank_data['title'])}\n"
            + filter_all(build_rank(rank_lines, page))
        )
        + rank_page_keyboard(server_number, rank_type, arg, page)
    )


server_list = on_command(
    "服务器列表", aliases={"ip", "IP"}, force_whitespace=True, block=True
)


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
            results.append(
                f"**๑{server_number}๑ 🌐 {info.server_name} ({info.game_version})**\n"
                f"- 地址: {copy_link_tag(filter_all(ip))}\n"
                f"- 端口: {copy_link_tag(str(server.port))}"
            )
            if info.enable_whitelist:
                results.append(f"> 本服务器已启用**白名单**")
        else:
            results.append(f"๑{server_number}๑ ❌ 服务器处于离线状态")
    await server_list.finish(
        MessageSegment.markdown("## 🍥 服务器列表\n" + "\n\n".join(results))
    )


server_info = on_command("服务器信息", force_whitespace=True, block=True)


@server_info.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    args: Args,
    group: CurrentGroup,
):
    if len(args) != 1:
        await server_info.finish(
            MessageSegment.markdown(
                "## 🍥 服务器信息\n"
                + "格式错误！\n"
                + f"正确格式: {cmd_input_tag('/服务器信息')} `<服务器序号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )
    if not GroupManager.check_server_num_ok(group, args[0]):
        await server_info.finish(
            MessageSegment.markdown("## 🍥 服务器信息\n" + "服务器序号错误！")
        )

    server_number = int(args[0])
    server_index = server_number - 1
    server_token = group.servers[server_index].token

    if not ConnectionManager.is_server_online(server_token):
        await server_info.finish(
            MessageSegment.markdown(
                "## 🍥 服务器信息\n" + f"❌ 服务器[{server_number}]处于离线状态"
            )
        )

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
    await server_info.finish(
        MessageSegment.markdown(
            "## 🍥 服务器信息\n"
            + f"- 地址: {filter_all(ip)}:{server.port}\n"
            + f"- 世界名: {filter_all(world)}\n"
            + f"- 游戏版本: {filter_all(server_version)}\n"
            + f"- {filter_all(server.type)}版本: {filter_all(tshock_version)}\n"
            + f"- CaiBot扩展版本: {filter_all(plugin_version)}\n"
            + f"- Cai白名单: {whitelist}\n"
            + f"- 服务器系统: {filter_all(os)}\n"
            + f"- 所属群: {server.group_open_id}"
        )
    )
