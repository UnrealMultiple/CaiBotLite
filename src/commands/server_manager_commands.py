import socket
import uuid

from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from src.models.group import Group
from src.utils.group_helper import GroupHelper
from src.models.server import Server
from src import cai_api
from src.cai_api import server_connection_manager


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


add_server = on_command("添加服务器", force_whitespace=True)


@add_server.handle()
async def add_server_handle(event: GroupAtMessageCreateEvent):
    if not await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        await add_server.finish(f'\n『添加服务器』\n' +
                                "没有权限!\n"
                                "只允许BOT管理设置\n"
                                "TIPS: BOT添加者为默认管理员")
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 4:
        await add_server.finish(f'\n『添加服务器』\n' +
                                f"格式错误!正确格式: 添加服务器 <IP地址> <端口> <验证码> [需要服务器适配插件]")

    cai_api.add_token(int(msg[3]), Server(str(uuid.uuid4()), event.group_openid, [], msg[1], int(msg[2])), 300)
    await add_server.finish(f'\n『添加服务器』\n' +
                            f"正在绑定服务器中...\n"
                            f"请确保你的服务器绑定码为: {int(msg[3])}")

edit_server = on_command("修改服务器", force_whitespace=True)


@edit_server.handle()
async def edit_server_handle(event: GroupAtMessageCreateEvent):
    if not await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        await edit_server.finish(f'\n『修改服务器』\n' +
                                "没有权限!\n"
                                "只允许BOT管理设置")
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 4:
        await edit_server.finish(f'\n『修改服务器』\n' +
                                f"格式错误!正确格式: 修改服务器 <服务器序号> <新IP地址> <新端口>")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await edit_server.finish(f'\n『修改服务器』\n'
                                f"服务器序号错误!")
    if not msg[3].isdigit():
        await edit_server.finish(f'\n『修改服务器』\n'
                                  f"无效端口号!")
    index = int(msg[1]) - 1
    group.servers[index].ip = msg[2]
    group.servers[index].port = int(msg[3])
    group.servers[index].update()
    # noinspection PyBroadException
    try:
        ip = socket.gethostbyname(group.servers[index].ip)
    except:
        ip = group.servers[index].ip
    await edit_server.finish(f'\n『修改服务器』\n'
                              f"修改成功!\n"
                              f"服务器IP信息已改为: {ip}:{group.servers[index].port}~")


del_server = on_command("删除服务器", force_whitespace=True)


@del_server.handle()
async def del_server_handle(event: GroupAtMessageCreateEvent):
    if not await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        await del_server.finish(f'\n『删除服务器』\n' +
                                "没有权限!\n"
                                "只允许BOT管理设置")
    group = Group.get_group(event.group_openid)
    if group is None:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"格式错误!正确格式: 删除服务器 <服务器序号>")
    cmd = {
        "type": "delserver",
        "msg_id": event.id
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"删除失败！\n"
                                f"服务器序号错误!")
    if group.servers[int(msg[1]) - 1].is_owner_server(event.group_openid):
        if server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_openid)
        Server.del_server(group.servers[int(msg[1]) - 1].token)
        await server_connection_manager.disconnect_server(group.servers[int(msg[1]) - 1].token)
        del group.servers[int(msg[1]) - 1]
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"服务器删除成功!\n"
                                f"若解绑失败，请删除服务器tshock/CaiBot.json然后重启")
    else:
        group.servers[int(msg[1]) - 1].shared.remove(group.open_id)
        group.servers[int(msg[1]) - 1].update()
        await server_connection_manager.disconnect_server(group.servers[int(msg[1]) - 1].token)
        await del_server.finish(f'\n『删除服务器』\n' +
                                f"服务器已被取消共享!")
