from typing import Annotated, AsyncGenerator

from fastapi import Depends as APIDepends
from nonebot.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from caibotlite.database import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


Session = Annotated[AsyncSession, Depends(get_session)]

APISession = Annotated[AsyncSession, APIDepends(get_session)]