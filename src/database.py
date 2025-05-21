import sqlite3
from typing import List

from nonebot import get_driver
from nonebot.log import logger

class Database:
    db = None
    def __init__(self) -> None:
        conn = sqlite3.connect("bot.db", check_same_thread=False)
        conn.row_factory = self.dict_factory
        self.conn = conn
        Database.db = self

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def query(cmd: str, *args) -> List['dict']:
        cursor = Database.db.conn.cursor()
        cursor.execute(cmd, args)
        Database.db.conn.commit()
        return cursor.fetchall()


start_db = get_driver()


@start_db.on_startup
def start_api_function():
    Database()
    logger.warning("[Sqlite启动]数据库初始化完成!")
