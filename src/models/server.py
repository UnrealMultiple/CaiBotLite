import json
from dataclasses import dataclass
from typing import List, Optional

from src.models.server_settings import ServerSettings
from src.database import Database


@dataclass
class Server:
    token: str
    owner: str
    shared: List[str]
    ip: str
    port: int

    @staticmethod
    def add_server(token: str, owner: str, ip: str, port: int) -> None:
        Database.query(
            'INSERT INTO "Servers" ("token", "owner", "shared", "ip", "port") '
            'VALUES (?,?,?,?,?);', token, owner, json.dumps([]), ip, port)

    def add_self_server(self) -> None:
        Database.query(
            'INSERT INTO "Servers" ("token", "owner", "shared", "ip", "port") '
            'VALUES (?,?,?,?,?);', self.token, self.owner, json.dumps([]), self.ip, self.port)

    @staticmethod
    def del_server(token: str) -> None:
        Database.query(
            'DELETE FROM "Servers" WHERE "token" = ?', token)

    @staticmethod
    def get_server(token: str) -> Optional['Server']:
        result = Database.query('SELECT * FROM "Servers" WHERE "token" = ?', token)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return Server(result['token'], result['owner'], json.loads(result['shared']), result['ip'], result['port'])

    @staticmethod
    def get_group_servers(group_id: str) -> List['Server']:
        results = Database.query('SELECT * FROM "Servers" WHERE "owner" = ?', group_id)
        results.extend(Database.query("SELECT * FROM Servers WHERE shared LIKE ?", '%' + str(group_id) + '%'))
        if len(results) == 0:
            return []
        else:
            return [Server(result['token'], result['owner'], json.loads(result['shared']), result['ip'], result['port'])
                    for result in results if result['owner'] == group_id or group_id in json.loads(result['shared'])]

    def get_server_index(self, group_id: str) -> int:
        servers = Server.get_group_servers(group_id)
        index = 1
        for i in servers:
            if i.token == self.token:
                return index
            index += 1
        raise Exception("服务器不存在")

    def is_connected(self):
        import src.api.server
        return src.api.server.server_connection_manager.server_available(self.token)

    def get_connection(self):
        import src.api.server
        return src.api.server.server_connection_manager.get_server_connection(self.token)

    def get_settings(self):
        return ServerSettings(self.token)

    async def send_data(self,data,group:int):
       import src.api.server
       await src.api.server.server_connection_manager.send_data(self.token, data, group)

    def is_owner_server(self, group_id: str) -> bool:
        return self.owner == group_id

    def update(self) -> None:
        Database.query('UPDATE "Servers" SET "owner" = ?, "shared" = ?, "ip" = ?,"port" = ? WHERE "token" = ?;',
                       self.owner, json.dumps(self.shared), self.ip, self.port, self.token)
