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
    else:
        group.admins = [event.op_member_openid]
        await GroupManager.update_group(session, group)
