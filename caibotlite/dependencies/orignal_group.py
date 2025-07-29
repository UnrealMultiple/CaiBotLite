from typing import Annotated

from nonebot.adapters.qq import GroupAtMessageCreateEvent
from nonebot.params import Depends

from caibotlite.dependencies import Session
from caibotlite.managers import GroupManager
from caibotlite.models import Group


async def get_original_group(event: GroupAtMessageCreateEvent, session: Session):
    group = await GroupManager.get_group_by_open_id(session, event.group_openid)
    if group is None:
        await GroupManager.create_group(session, event.group_openid, event.author.union_openid, )
        group = await GroupManager.get_group_by_open_id(session, event.group_openid)

    return group


OriginalGroup = Annotated[Group, Depends(get_original_group)]
