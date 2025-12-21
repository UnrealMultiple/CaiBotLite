from datetime import datetime
from typing import Optional

from expiringdict import ExpiringDict
from sqlalchemy import delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from caibotlite.models import User, LoginIP, LoginUUID, LoginAttempt
from caibotlite.services import GeoIP


class LoginManager:
    # noinspection PyTypeHints
    login_attempts: ExpiringDict[str, LoginAttempt] = ExpiringDict(max_len=1000, max_age_seconds=600)

    @classmethod
    def get_attempt(cls, user_open_id: str) -> Optional[LoginAttempt]:
        if user_open_id not in cls.login_attempts:
            return None
        login_attempt = cls.login_attempts[user_open_id]
        del cls.login_attempts[user_open_id]
        return login_attempt

    @classmethod
    def add_attempt(cls, user_open_id: str, uuid: str, ip: str, city: str):
        cls.login_attempts[user_open_id] = LoginAttempt(user_open_id, uuid, ip, city)

    @classmethod
    def remove_attempt(cls, user_open_id: str):
        if user_open_id in cls.login_attempts:
            del cls.login_attempts[user_open_id]

    @classmethod
    async def insert_new_ip(cls, session: AsyncSession, user: User, ip: str, city: str):
        login_ip = LoginIP()
        login_ip.ip = ip
        login_ip.city = city
        login_ip.record_time = datetime.now()
        user.ips.append(login_ip)
        await session.merge(user)
        await session.commit()

    @classmethod
    async def clean_up(cls, session: AsyncSession, user: User):
        need_merge = False
        if len(user.uuids) > 10:
            user.uuids = user.uuids[len(user.uuids) - 10:]
            need_merge = True

        if len(user.ips) > 10:
            user.ips = user.ips[len(user.ips) - 10:]
            need_merge = True

        if need_merge:
            await session.merge(user)
            await session.commit()

    @classmethod
    async def try_login_ok(cls, session, user: User, uuid: str, ip: str) -> bool:
        city = GeoIP.get_city(ip)
        if uuid not in user.uuid_list:
            cls.add_attempt(user.open_id, uuid, ip, city)
            return False

        if ip not in user.ip_list:
            if city is None or city not in user.city_list:
                cls.add_attempt(user.open_id, uuid, ip, city)
                return False
            else:
                await cls.insert_new_ip(session, user, ip, city)

        return True

    @classmethod
    async def accept_login_ok(cls, session: AsyncSession, user: User) -> bool:
        login_attempt = cls.get_attempt(user.open_id)

        if login_attempt is None:
            return False

        if login_attempt.login_uuid not in user.uuid_list:
            user.uuids.append(
                LoginUUID(uuid=login_attempt.login_uuid, record_time=datetime.now()))

        if login_attempt.login_ip not in user.ip_list:
            user.ips.append(
                LoginIP(ip=login_attempt.login_ip, city=login_attempt.login_city, record_time=datetime.now()))

        user.last_login_time = datetime.now()
        await session.merge(user)
        await session.commit()
        await cls.clean_up(session, user)
        return True

    @classmethod
    def reject_login_ok(cls, user: User) -> bool:
        login_attempt = cls.get_attempt(user.group_open_id)

        if login_attempt is None:
            return False

        cls.remove_attempt(user.open_id)
        return True

    @classmethod
    async def clean_login_info(cls, session: AsyncSession, user: User):
        await session.execute(
            delete(LoginUUID).where(LoginUUID.user_open_id == user.open_id)
        )
        await session.execute(
            delete(LoginIP).where(LoginIP.user_open_id == user.open_id)
        )
        await session.commit()

        user.uuids = []
        user.ips = []

        await session.merge(user)
