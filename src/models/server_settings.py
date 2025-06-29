class ServerSettings:
    def __init__(self,token) -> None:
        # noinspection PyBroadException
        try:
            import src.api.server
            server = src.api.server.server_connection_manager.get_server_connection(token)
            self.server_version = server.terraria_version
            self.world = server.world
            self.tshock_version = server.tshock_version
            self.whitelist = server.whitelist
            self.plugin_version = server.plugin_version
            self.os = server.os
            self.sync_group_chat = server.sync_group_chat
            self.sync_server_chat= server.sync_server_chat
        except:
            self.server_version = None
            self.world = None
            self.tshock_version = None
            self.whitelist = None
            self.plugin_version = None
            self.os = None
            self.sync_group_chat = None
            self.sync_server_chat = None
