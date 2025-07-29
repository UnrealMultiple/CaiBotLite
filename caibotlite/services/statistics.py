from nonebot import require
from sqlalchemy import select

from caibotlite.database import async_session
from caibotlite.models.statistic_data import StatisticData

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

class Statistics:
    whitelist_check = 0
    player_signs = 0
    message_received = 0

    _inited = False

    @classmethod
    async def init(cls):
        if not cls._inited:
            async with async_session() as session:
                fields = {k: v for k, v in vars(cls).items() if
                          not isinstance(v, classmethod) and not k.startswith("_")}

                for k, v in fields.items():
                    result = await session.execute(select(StatisticData).where(StatisticData.key == k))
                    field = result.scalar_one_or_none()
                    if field is None:
                        field = StatisticData()
                        field.key = k
                        field.value = v
                        session.add(field)

                    else:
                        setattr(cls, k, field.value)
            await session.commit()

            @scheduler.scheduled_job("cron", second="*/30", id="auto_save_statistics")
            async def auto_save_statists():
                await Statistics.update()

            cls._inited = True

    @classmethod
    async def update(cls) -> None:
        if not cls._inited:
            raise Exception("Statistics not initialized!")

        async with async_session() as session:
            fields = {k: v for k, v in vars(cls).items() if not isinstance(v, classmethod) and not k.startswith("_")}

            for k, v in fields.items():
                result = await session.execute(select(StatisticData).where(StatisticData.key == k))
                field = result.scalar_one_or_none()
                if field is None:
                    field = StatisticData()
                    field.key = k
                    field.value = v
                    session.add(field)
                else:
                    field.value = v
                    await session.merge(field)

            await session.commit()
