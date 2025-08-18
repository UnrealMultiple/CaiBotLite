from nonebot import on_command, on_message
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from caibotlite.utils import match_like_command

help_list = on_command("菜单", aliases={"帮助"}, force_whitespace=True, block=True)


@help_list.handle()
async def help_handle():
    await help_list.finish(f'\n『菜单』\n'
                           f'⚡群管理\n'
                           f'⚡服务器管理\n'
                           f'⚡快捷功能菜单\n'
                           f'⚡地图功能菜单\n'
                           f'⚡白名单菜单\n'
                           f'⚡图鉴搜索菜单\n'
                           f'😘文档: https://docs.terraria.ink/zh/caibot/CaiBotLite.html')


help_list0 = on_command("群管理", force_whitespace=True, block=True)


@help_list0.handle()
async def _():
    await help1.finish(f'\n『菜单•服务器管理』\n'
                       f'⚡管理列表 [列出BOT管理]\n'
                       f'⚡添加管理 <管理员白名单名字> [添加BOT管理]\n'
                       f'⚡删除管理 <管理员白名单名字> [删除BOT管理]\n'
                       f'⚡绑定父群 <父群ID> [绑定父群]\n'
                       f'⚡解绑父群 [解绑父群] \n'
                       f'⚡获取群信息 [获取一个群的ID等信息]\n'
                       f'⚡设置 [设置群的一些功能]\n'
                       f'TIPS： 重新拉BOT即可重置管理员')


help1 = on_command("服务器管理", force_whitespace=True, block=True)


@help1.handle()
async def _():
    await help1.finish(f'\n『菜单•服务器管理』\n'
                       f'⚡添加服务器 <IP地址> <端口> <绑定码>\n'
                       f'⚡修改服务器 <服务器序号> <IP地址> <端口>\n'
                       f'⚡删除服务器 <服务器序号> \n'
                       f'⚡服务器列表 [获取服务器地址端口等]\n'
                       f'⚡服务器信息 <服务器序号> [获取服务器详细信息]')


help2 = on_command("快捷功能菜单", force_whitespace=True, block=True)


@help2.handle()
async def _():
    await help2.finish(f'\n『菜单•快捷功能』\n'
                       f'⚡添加白名单 <名字> [绑定角色]\n'
                       f'⚡修改白名单 <名字> [重新绑定角色]\n'
                       f'⚡黑名单列表 [查看被封禁的玩家]\n'
                       f'⚡添加黑名单 <名字> [封禁玩家]\n'
                       f'⚡删除黑名单 <名字> [解封玩家]\n'
                       f'⚡远程指令 <服务器序号> <命令内容> [执行远程命令]\n'
                       f'⚡在线 [获取服务器在线]\n'
                       f'⚡服务器列表 [获取服务器地址端口等]\n'
                       f'⚡进度查询 <服务器序号>\n'
                       f'⚡查背包 <服务器序号> <玩家名> [查询玩家的背包内容]\n'
                       f'⚡清空设备 [清除绑定的设备]\n'
                       f'⚡自踢 [断开所有服务器连接]')


help3 = on_command("地图功能菜单", force_whitespace=True, block=True)


@help3.handle()
async def _():
    await help3.finish(f'\n『菜单•地图功能』\n'
                       f'⚡查看地图 <服务器序号> [获取地图图片]\n'
                       f'⚡下载地图 <服务器序号> [获取地图文件]\n'
                       f'⚡下载小地图 <服务器序号> [获取小地图文件]')


help4 = on_command("白名单菜单", force_whitespace=True, block=True)


@help4.handle()
async def _():
    await help4.finish(f'\n『菜单•白名单』\n'
                       f'⚡签到 [没啥用]\n'
                       f'⚡查询金币 [字面意思]\n'
                       f'⚡添加白名单 <名字> [绑定角色]\n'
                       f'⚡修改白名单 <名字> [重新绑定角色]')


help5 = on_command("图鉴搜索菜单", force_whitespace=True, block=True)


@help5.handle()
async def _():
    await help5.finish(f'\n『菜单•图鉴搜索』\n'
                       f'⚡si <名字|ID> [搜物品]\n'
                       f'⚡sn <名字|ID> [搜生物]\n'
                       f'⚡sp <名字|ID> [搜弹幕]\n'
                       f'⚡sb <名字|ID> [搜Buff]\n'
                       f'⚡sx <名字|ID> [搜修饰语]')


command_helper = on_message(priority=114514, block=True)


@command_helper.handle()
async def _(event: GroupAtMessageCreateEvent):
    if not event.get_plaintext().strip():
        await command_helper.finish("我不是AI捏, @我也没用喵~\n"
                                    "使用\"/帮助\"查询命令列表")

    command_name = event.get_plaintext().strip().split(maxsplit=1)[0].lstrip('/ ')
    like_commands = match_like_command(command_name)
    if len(like_commands) == 0:
        await command_helper.finish("没有找到匹配的命令呢~\n"
                                    "使用\"/帮助\"查询命令列表")

    await command_helper.finish(f"没有任何匹配的命令呢~\n"
                                f"猜你想要: {', '.join(like_commands)}")
