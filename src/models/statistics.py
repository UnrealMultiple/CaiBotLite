from typing import Optional
from threading import Lock
from src.database import Database


class Statistics:
    _write_buffer = {
        'check_whitelist': 0,
        'total_check': 0,
        'total_kick': 0
    }
    _buffer_lock = Lock()
    BUFFER_FLUSH_THRESHOLD = 100

    def __init__(self, total_group: int, total_kick: int, total_check: int, check_whitelist: int,
                 total_users: int, total_servers: int) -> None:
        self.total_group = total_group
        self.total_kick = total_kick
        self.total_check = total_check
        self.check_whitelist = check_whitelist
        self.total_users = total_users
        self.total_servers = total_servers

    @classmethod
    def _flush_buffer(cls, field: str):
        """如果缓冲区达到阈值，则刷新指定字段的增量到数据库"""
        with cls._buffer_lock:
            if cls._write_buffer[field] >= cls.BUFFER_FLUSH_THRESHOLD:
                increment = cls._write_buffer[field]
                Database.query(f'UPDATE "Statistics" SET "{field}" = "{field}" + ? WHERE rowid = 1;', increment)
                cls._write_buffer[field] = 0  # 重置计数器

    @staticmethod
    def get_group_user_count(group_id: str) -> int:
        count_result = Database.query(f"SELECT COUNT(*) as count FROM Users_{group_id}")
        return count_result[0]['count']

    @staticmethod
    def get_statistics() -> Optional['Statistics']:
        re = Database.query('SELECT * FROM "Statistics" WHERE rowid = 1;')
        # 从数据库读取实际值 + 缓冲区中的未提交增量
        with Statistics._buffer_lock:
            total_kick = re[0]['total_kick'] + Statistics._write_buffer['total_kick']
            total_check = re[0]['total_check'] + Statistics._write_buffer['total_check']
            check_whitelist = re[0]['check_whitelist'] + Statistics._write_buffer['check_whitelist']

        re = Database.query('SELECT COUNT(*) AS nums FROM "Groups";')
        total_group = re[0]['nums']
        tables_result = Database.query("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Users_%'")
        total_users = 0
        for table in tables_result:
            table_name = table['name']
            count_result = Database.query(f'SELECT COUNT(*) as count FROM "{table_name}"')
            row_count = count_result[0]['count']
            total_users += row_count
        re = Database.query('SELECT COUNT(*) AS nums FROM "Servers"')
        total_servers = re[0]['nums']
        return Statistics(total_group, total_kick, total_check, check_whitelist, total_users, total_servers)

    @staticmethod
    def add_kick() -> None:
        with Statistics._buffer_lock:
            Statistics._write_buffer['total_kick'] += 1
        Statistics._flush_buffer('total_kick')

    @staticmethod
    def add_check() -> None:
        with Statistics._buffer_lock:
            Statistics._write_buffer['total_check'] += 1
        Statistics._flush_buffer('total_check')

    @staticmethod
    def add_check_whitelist() -> None:
        with Statistics._buffer_lock:
            Statistics._write_buffer['check_whitelist'] += 1
        Statistics._flush_buffer('check_whitelist')