from nonebot.adapters.qq import GroupAddRobotEvent
from nonebot import on_notice

from src.models.group import Group

init = on_notice()
@init.handle()
async def init_personal_handle(event: GroupAddRobotEvent):
    if isinstance(event,GroupAddRobotEvent):
        group = Group.get_group(event.group_openid)
        if group is None:
            Group.add_group(event.group_openid,event.op_member_openid)
        else:
            group.admins = [event.op_member_openid]
            group.update()