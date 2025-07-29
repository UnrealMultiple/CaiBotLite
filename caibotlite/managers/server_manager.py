import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from caibotlite.models import Server


class ServerManager:

    @classmethod
    async def get_server_by_token(cls, session: AsyncSession, token: str) -> Optional[Server]:
        result = await session.execute(select(Server).where(Server.token == token))
        taget_server = result.scalar()

        return taget_server

    @classmethod
    async def get_server_by_id(cls, session: AsyncSession, server_id: int) -> Optional[Server]:
        result = await session.execute(select(Server).where(Server.id == server_id))
        taget_server = result.scalar()

        return taget_server

    @classmethod
    async def delete_server_by_token(cls, session: AsyncSession, token: str):
        if (server := await cls.get_server_by_token(session, token)) is not None:
            await session.delete(server)
            await session.commit()

    @classmethod
    async def create_server(cls, session: AsyncSession, group_open_id: str, token: str, ip: str, port: int) -> bool:
        server = Server(
            group_open_id=group_open_id,
            token=token,
            ip=ip,
            port=port
        )
        session.add(server)
        await session.commit()

        if await cls.get_server_by_token(session, token) is None:
            return False

        else:
            return True

    @classmethod
    async def update_server(cls, session: AsyncSession, server: Server) -> None:
        await session.merge(server)
        await session.commit()

    @classmethod
    async def count_all_servers(cls, session: AsyncSession) -> int:
        result = await session.execute(func.count(Server.id))
        return result.scalar()

    @staticmethod
    def is_valid_token(token: str) -> bool:
        try:
            uuid.UUID(token, version=4)
            return True
        except ValueError:
            return False
