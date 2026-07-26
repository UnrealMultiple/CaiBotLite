import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from caibotlite.models import Base

DEFAULT_DATABASE_URL = "postgresql+asyncpg://caibot:caibot@localhost:5432/caibotlite"


def _get_database_url() -> str:
    try:
        from nonebot import get_driver

        url = getattr(get_driver().config, "database_url", None)
        if url:
            return url
    except Exception:
        pass
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


engine = create_async_engine(_get_database_url(), echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=True)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # WARNING: 此语句仅仅测试时使用
        await conn.run_sync(Base.metadata.create_all)
