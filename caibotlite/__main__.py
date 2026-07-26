import asyncio
from datetime import datetime

import nonebot
from nonebot.adapters.qq import Adapter
from nonebot.log import logger, default_format


def main():
    logger.add(
        f"logs/{datetime.today().strftime('%Y-%m-%d')}.log",
        level="WARNING",
        format=default_format,
        rotation="3 week",
    )

    nonebot.init()

    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    from caibotlite.database import engine, init_db
    from caibotlite.services import LookBag
    from caibotlite.services import TerrariaSearch
    from caibotlite.services.geo_ip import GeoIP
    from caibotlite.services.statistics import Statistics

    async def init_services():
        await init_db()
        await Statistics.init()
        # asyncpg 连接绑定创建它的事件循环, 必须在临时循环结束前清空连接池,
        # 否则 nonebot 的事件循环复用旧连接会报 "attached to a different loop"
        await engine.dispose()

    asyncio.run(init_services())

    TerrariaSearch.init_search()
    LookBag.init_look_bag()
    GeoIP.init()
    nonebot.load_plugins("caibotlite/commands")
    nonebot.load_plugins("caibotlite/api")
    nonebot.load_plugins("caibotlite/event")
    nonebot.run()


if __name__ == "__main__":
    main()
