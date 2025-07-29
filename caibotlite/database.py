from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from caibotlite.models import Base

engine = create_async_engine('sqlite+aiosqlite:///data/bot.db', echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=True)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # WARNING: 此语句仅仅测试时使用
        await conn.run_sync(Base.metadata.create_all)
