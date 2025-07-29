# CaiBotLite API协议

## 数据包结构

```jsonc
{
    "version": "0.1.0",       // 数据包版本
    "direction": "to_server", // 数据包方向
    "type": "self_kick",      // 数据包类型
    "is_request": true,       // 是否为请求
    "request_id": "...",      // 请求ID
    "payload": {              // 数据 Dict[str, Any]
        ...
    }
}
```

## 数据包类型

### hello (Server -> Bot)

服务器向Bot发送自身环境及配置信息

- 版本: v2025.7.18
- 请求: 否
- 交付:

| 字段                  | 类型             | 说明     |
|---------------------|----------------|--------|
| game_version        | str            | 游戏版本   |
| server_core_version | str            | 服务端版本  |
| plugin_version      | str            | 适配插件版本 |
| enable_whitelist    | bool           | 启用白名单  |
| system              | str            | 系统版本   |
| server_name         | str            | 服务器名称  |
| settings            | Dict[str, Any] | 适配插件配置 |

### whitelist (Server <-> Bot)

服务器向Bot查询白名单及请求登录, Bot返回的白名单及登录结果

- 版本: v2025.7.18
- 请求: 否
- -> Bot 交付:

| 字段          | 类型  | 说明     |
|-------------|-----|--------|
| player_name | str | 玩家名    |
| player_ip   | str | 玩家IP   |
| player_uuid | str | 玩家UUID |

- -> Server 交付:

| 字段               | 类型                   | 说明         |
|------------------|----------------------|------------|
| whitelist_result | WhitelistResult(str) | 白名单 & 登录结果 |
| player_name      | str                  | 玩家名字       |