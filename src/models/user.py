import datetime
import json
from dataclasses import dataclass
from typing import Optional, List

from src.database import Database

DEFAULT_SIGN_DATE = datetime.datetime.min
DEFAULT_RENAME_DATE = datetime.datetime.min
MAX_NAME_LENGTH = 20
MIN_MONEY = 0


@dataclass
class User:
    group_id: str
    open_id: str
    name: str
    money: int
    last_sign: datetime.datetime
    sign_count: int
    uuid: List[str]
    last_rename: datetime.datetime


    @staticmethod
    def get_sign_rank(group_id:str) -> int:
        return Database.query(f"SELECT COUNT(*) as num FROM Users_{group_id} WHERE DATE(last_sign) = DATE('now','localtime');")[0]['num']

    @staticmethod
    def add_user(group_id:str, open_id: str, name: str) -> Optional['User'] | None:
        Database.query(
            f'INSERT INTO "Users_{group_id}" ("id", "name", "money", "last_sign","sign_count","uuid",'
            '"last_rename") '
            'VALUES (?,?,?,?,?,?,?);', open_id, name, 0, datetime.datetime.min.isoformat(), 0, "[]", datetime.datetime.min.isoformat())
        return User(group_id, open_id, name, 0, datetime.datetime.min, 0, [], datetime.datetime.min)

    @staticmethod
    def get_user(group_id:str, open_id: str) -> Optional['User'] | None:
        result = Database.query(f'SELECT * FROM "Users_{group_id}" WHERE "id" = ?', open_id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(group_id, result['id'], result['name'], result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']),
                        datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_user_by_name(group_id: str, name: str) -> Optional['User'] | None:
        result = Database.query(f'SELECT * FROM "Users_{group_id}" WHERE "name" = ?', name)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(group_id, result['id'], result['name'], result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']),
                        datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_users_by_uuid(group_id:str, uuid: str) -> list['User']:
        query = f'SELECT * FROM "Users_{group_id}" WHERE "uuid" LIKE ?'
        results = Database.query(query, '%' + uuid + '%')
        re = []
        for result in results:
            re.append(User(group_id, result['id'], result['name'], result['money'],
                           datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                           json.loads(result['uuid']),
                           datetime.datetime.fromisoformat(result['last_rename'])))
        return re


    def update(self) ->None :
        Database.query(f'UPDATE "Users_{self.group_id}" SET "name" = ?, "money" = ?, '
                  '"last_sign" = ? ,"sign_count" = ?,"uuid" = ? , "last_rename" = ?  WHERE "id" '
                  '= ?;', self.name, self.money, self.last_sign.isoformat(), self.sign_count,
                       json.dumps(self.uuid), self.last_rename.isoformat(), self.open_id)
