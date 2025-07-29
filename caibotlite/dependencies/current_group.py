from typing import Annotated

from nonebot.adapters.qq import GroupAtMessageCreateEvent
from nonebot.params import Depends

from caibotlite.dependencies import Session
from caibotlite.managers import GroupManager
from caibotlite.models import Group


async def get_current_group(event: GroupAtMessageCreateEvent, session: Session):
    group = await GroupManager.get_group_by_open_id(session, event.group_openid)
    if group is None:
        await GroupManager.create_group(session, event.group_openid, event.author.union_openid, )
        group = await GroupManager.get_group_by_open_id(session, event.group_openid)

    await session.refresh(group, ["parent_group"])
    if group.parent_group is not None:
        return group.parent_group

    return group


CurrentGroup = Annotated[Group, Depends(get_current_group)]
