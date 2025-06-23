import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from src.models.server import Server
from src.database import Database


@dataclass
class Group:
    open_id: str
    parent: str
    admins: List[str]
    black_list: List[str]
    servers: List['Server']
    config: Dict
    connected_servers: List['Server'] = field(init=False)

    def __post_init__(self):
        # noinspection PyBroadException
        try:
            object.__setattr__(self, 'connected_servers', [i for i in self.servers if i.is_connected()])
        except:
            object.__setattr__(self, 'connected_servers', [])

    @staticmethod
    def add_group(open_id: str, admin: str) -> None:
        Database.query(f'''
        CREATE TABLE IF NOT EXISTS "Users_{open_id}" (
          "id" text NOT NULL,
          "name" text,
          "uuid" text,
          "money" integer,
          "last_sign" text,
          "sign_count" integer,
          "last_rename" text,
          PRIMARY KEY ("id")
        );''')
        Database.query(
            'INSERT INTO "Groups" ("id","parent", "admins","black_list","config") '
            'VALUES (?,?,?,?,?);', open_id, "", json.dumps([admin]), json.dumps([]), json.dumps({}))

    @staticmethod
    def get_group_through_server(server: Server) -> Optional['Group']:
        return Group.get_group(server.owner)


    @staticmethod
    def get_group(open_id: str, origin: bool = False) -> Optional['Group']:
        result = Database.query('SELECT * FROM "Groups" WHERE "id" = ?', open_id)
        if len(result) == 0:
            Group.add_group(open_id, "ERROR_NONE")
            return Group(open_id, "", [], [], [], {})
        else:
            result = result[0]
            servers = Server.get_group_servers(open_id)
            if origin or not result['parent']:
                return Group(result['id'], result['parent'], json.loads(result['admins']), json.loads(result['black_list']), servers,
                             json.loads(result['config']))
            else:
                return Group.get_group(result['parent'], True)

    def update(self) -> None:
        Database.query('UPDATE "Groups" SET "parent" = ?,"admins" = ?,"black_list" =?,"config"=? WHERE "id" = ?;',
                       self.parent, json.dumps(self.admins), json.dumps(self.black_list), json.dumps(self.config),
                       self.open_id)

    def get_subgroup(self) -> List['str']:
        result = Database.query('SELECT * FROM "Groups" WHERE parent = ? AND parent != \'\' ;', self.open_id)
        return [ i['id'] for i in result ]