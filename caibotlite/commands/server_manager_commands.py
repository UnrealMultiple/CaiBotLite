import socket
import uuid

from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from caibotlite.dependencies import Args, Session, CurrentGroup
from caibotlite.enums import PackageType
from caibotlite.managers import ConnectionManager, GroupManager, ServerManager, TokenManager
from caibotlite.services import PackageWriter

add_server = on_command("添加服务器", force_whitespace=True, block=True)


@add_server.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await add_server.finish(f'\n『添加服务器』\n' +
                                "没有权限!\n"
                                "只允许BOT管理设置\n"
                                "TIPS: BOT添加者为默认管理员")
    if len(args) != 3:
        await add_server.finish(f'\n『添加服务器』\n' +
                                f"格式错误!正确格式: 添加服务器 <IP地址> <端口> <验证码>")

    token = str(uuid.uuid4())
    ip = args[0]
    try:
        port = int(args[1])
    except ValueError:
        await add_server.finish(f'\n『添加服务器』\n' +
                                f"无效端口!")
    try:
        verification_code = int(args[2])
    except ValueError:
        await add_server.finish(f'\n『添加服务器』\n' +
                                f"无效验证码!")

    await ServerManager.create_server(session, group.open_id, token, ip, port)

    TokenManager.set_token(group.open_id, verification_code, token)

    await add_server.finish(f'\n『添加服务器』\n' +
                            f"正在绑定服务器中...\n"
                            f"请确保你的服务器绑定码为: {verification_code} (2分钟有效)")


edit_server = on_command("修改服务器", force_whitespace=True, block=True)


@edit_server.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await edit_server.finish(f'\n『修改服务器』\n' +
                                 "没有权限!\n"
                                 "只允许BOT管理设置")

    if len(args) != 3:
        await edit_server.finish(f'\n『修改服务器』\n' +
                                 f"格式错误!\n"
                                 f"正确格式: 修改服务器 <服务器序号> <新IP地址> <新端口>")

    if not args[0].isdigit() or int(args[0]) > len(group.servers):
        await edit_server.finish(f'\n『修改服务器』\n'
                                 f"服务器序号错误!")
    if not args[2].isdigit():
        await edit_server.finish(f'\n『修改服务器』\n'
                                 f"无效端口号!")

    server_index = int(args[0]) - 1
    server = group.servers[server_index]

    server.ip = args[1]
    server.port = int(args[2])

    await GroupManager.update_group(session, group)
    # noinspection PyBroadException
    try:
        ip = socket.gethostbyname(group.servers[server_index].ip)
    except:
        ip = group.servers[server_index].ip
    await edit_server.finish(f'\n『修改服务器』\n'
                             f"修改成功!\n"
                             f"服务器IP信息已改为: {ip}:{server.port}")


del_server = on_command("删除服务器", force_whitespace=True, block=True)


@del_server.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await del_server.finish(f'\n『删除服务器』\n' +
                                "没有权限!\n"
                                "只允许BOT管理设置")
    if len(args) != 1:
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"格式错误!正确格式: 删除服务器 <服务器序号>")

    if not args[0].isdigit() or int(args[0]) > len(group.servers):
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"删除失败！\n"
                                f"服务器序号错误!")
    server_index = int(args[0]) - 1
    server = group.servers[server_index]
    if ConnectionManager.is_server_online(server.token):
        package = PackageWriter(PackageType.UNBIND_SERVER, False)
        package.write("reason", "群主动解绑服务器!")
        await ConnectionManager.send_data(server.token, package.build())

    await ServerManager.delete_server_by_token(session, server.token)
    await del_server.finish(f'\n『删除服务器』\n' +
                            f"服务器删除成功!\n"
                            f"若解绑失败，请删除服务器\"tshock/CaiBotLite.json\"然后重启")
