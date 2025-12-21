from nonebot.adapters.qq import GroupAddRobotEvent
from nonebot import on_notice

from caibotlite.dependencies import Session
from caibotlite.managers import GroupManager

init = on_notice()


@init.handle()
async def _(event: GroupAddRobotEvent, session: Session):
    group = await GroupManager.get_group_by_open_id(session, event.group_openid)
    if group is None:
        await GroupManager.create_group(session, event.group_openid, event.op_member_openid)
        await init.finish("『BOT初始化』\n"
                          "😘欢迎使用CaiBotLite! \n"
                          "默认群管理已设为BOT添加者\n"
                          "使用\"/添加管理员 <名字> (管理员要先加白名单)\"添加新管理\n"
                          "使用教程: https://docs.terraria.ink/zh/caibot/CaiBotLite.html")
    else:
        group.admins = [event.op_member_openid]
        group.parent_open_id = None
        await GroupManager.update_group(session, group)
        await init.finish("『BOT重置』\n"
                          "😘欢迎使用CaiBotLite! \n"
                          "群管理已重置为BOT添加者\n"
                          "使用\"/添加管理员 <名字> (管理员要先加白名单)\"添加新管理\n"
                          "使用教程: https://docs.terraria.ink/zh/caibot/CaiBotLite.html")
