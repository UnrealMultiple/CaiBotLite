import re
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio.session import AsyncSession

from caibotlite.models import User, LoginAttempt
from caibotlite.services import Statistics


class UserManager:
    login_attempts: Dict[str, LoginAttempt] = {}

    @classmethod
    async def get_user_by_open_id(cls, session: AsyncSession, group_open_id: str, user_open_id: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.open_id == user_open_id, User.group_open_id == group_open_id))
        taget_user = result.scalar()

        return taget_user

    @classmethod
    async def get_user_by_name(cls, session: AsyncSession, group_open_id: str, name: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.name == name, User.group_open_id == group_open_id))
        taget_user = result.scalar()

        return taget_user

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.id == user_id))
        taget_user = result.scalar()

        return taget_user

    @classmethod
    async def create_user(cls, session: AsyncSession, group_open_id: str, user_open_id: str, name: str) -> bool:
        user = User(name=name, group_open_id=group_open_id, open_id=user_open_id)
        session.add(user)
        await session.commit()
        if await cls.get_user_by_name(session, group_open_id, name) is None:
            return False

        else:
            return True

    @classmethod
    async def update_user(cls, session: AsyncSession, user: User) -> None:
        await session.merge(user)
        await session.commit()

    @classmethod
    async def count_group_users(cls, session: AsyncSession, group_open_id: str) -> int:
        result = await session.execute(
            select(func.count()).select_from(User).where(User.group_open_id == group_open_id))
        return result.scalar()

    @classmethod
    async def count_all_users(cls, session: AsyncSession, ) -> int:
        result = await session.execute(func.count(User.id))
        return result.scalar()

    @classmethod
    async def sign(cls, session: AsyncSession, user: User) -> Optional[int]:
        if user.last_sign.date() == datetime.today().date():
            return None

        if user.last_sign.date() == datetime.today().date() - timedelta(days=1):
            user.sign_consistency += 1
        else:
            user.sign_consistency = 1

        user.sign_days += 1

        user.last_sign = datetime.now()
        await cls.update_user(session, user)
        Statistics.player_signs += 1
        today = datetime.today().date()
        # noinspection PyTypeChecker
        result = await session.execute(
            select(func.count()).select_from(User).where(func.date(User.last_sign) == today))
        return result.scalar()

    @staticmethod
    def check_name_ok(name: str) -> bool:
        pattern = re.compile(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$')
        if pattern.match(name):
            return True
        else:
            return False
