from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from caibotlite import constants
from caibotlite.models import Group, GroupConfig


class GroupManager:

    @classmethod
    async def get_group_by_open_id(cls, session: AsyncSession, group_open_id: str) -> Optional[Group]:
        result = await session.execute(select(Group).where(Group.open_id == group_open_id))
        taget_group = result.scalar()

        return taget_group

    @classmethod
    async def get_group_by_id(cls, session: AsyncSession, group_id: int) -> Optional[Group]:

        result = await session.execute(select(Group).where(Group.id == group_id))
        taget_group = result.scalar()

        return taget_group

    @classmethod
    async def create_group(cls, session: AsyncSession, group_open_id: str, first_admin_open_id: str) -> bool:
        group = Group(
            open_id=group_open_id,
            config=GroupConfig(),
            admins=[first_admin_open_id],
        )
        session.add(group)
        await session.commit()

        if await cls.get_group_by_open_id(session, group_open_id) is None:
            return False

        else:
            return True

    @classmethod
    async def count_all_groups(cls, session: AsyncSession, ) -> int:
        result = await session.execute(func.count(Group.id))
        return result.scalar()

    @classmethod
    async def update_group(cls, session: AsyncSession, group: Group) -> None:
        await session.merge(group)
        await session.commit()

    @staticmethod
    def check_server_num_ok(group: Group, num: str) -> bool:
        return num.isdigit() and 0 < int(num) <= len(group.servers)

    @classmethod
    def has_permission(cls, group: Group, user_open_id: str) -> bool:
        if user_open_id in constants.SUPERADMINS_OPEN_ID:
            return True

        if user_open_id in group.admins:
            return True
        else:
            return False
