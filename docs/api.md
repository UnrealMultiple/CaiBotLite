# CaiBotLite API 协议

本文档描述 `CaiBotLite` 当前代码中已经实现的 HTTP / WebSocket 接口，以及服务端适配插件与 Bot 之间使用的数据包协议。

> 文档依据当前仓库代码整理，时间：`2026-06-18`

---

## 目录

- [1. 总体流程](#1-总体流程)
- [2. HTTP 接口](#2-http-接口)
- [3. WebSocket 连接](#3-websocket-连接)
- [4. 数据包结构](#4-数据包结构)
- [5. 枚举定义](#5-枚举定义)
- [6. 数据包类型](#6-数据包类型)
- [7. 错误处理](#7-错误处理)
- [8. 编码约定](#8-编码约定)

---

## 1. 总体流程

### 1.1 绑定服务器

1. 群管理员在 Bot 中执行“添加服务器”命令，Bot 生成一个绑定验证码与服务器令牌。
2. 服务端插件通过 HTTP 调用获取令牌：`GET /server/token/{init_code}`。
3. 服务端插件使用获取到的 `token` 建立 WebSocket 连接：`/server/ws/{group_open_id}/{server_type}/`。
4. 建立连接后，服务端应主动发送 `hello` 数据包，告知 Bot 当前服务器信息。

### 1.2 运行期交互

- **Bot 主动调用服务器**：如在线查询、进度查询、远程命令、下载地图等。
- **服务器主动通知 Bot**：如 `hello`、`whitelist`。
- **错误返回**：当服务器无法完成某个 Bot 发起的调用时，应返回 `error` 数据包。

---

## 2. HTTP 接口

## 2.1 `GET /ping`

健康检查接口。

### 响应示例

```json
{
  "result": "pong"
}
```

---

## 2.2 `GET /server/token/{init_code}`

用于服务端插件通过绑定验证码换取 WebSocket 连接令牌。

### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `init_code` | `int` | 群内“添加服务器”命令生成的验证码，默认 2 分钟有效 |

### 成功响应

```json
{
  "token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "group_open_id": "GROUP_OPEN_ID"
}
```

### 失败响应

- `404 Not Found`: 没有可用令牌或验证码已过期。

---

## 2.3 `GET /download/{file_id}`

下载 Bot 临时托管的文件。主要用于地图、小地图等文件的二次下载。

### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `file_id` | `str` | 临时文件 ID |

### 说明

- 文件来自 Bot 内部临时目录 `temp/`
- 文件记录默认保存 **10 分钟**
- 超时后访问会返回 404

### 失败响应

- `404 Not Found`: 文件不存在或已过期。

---

## 2.4 `GET /plugin/{name}`

下载 `plugins/` 目录下的插件文件。

### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 插件文件名，不允许包含 `/` |

### 失败响应

- `403 Forbidden`: 文件名非法。
- `404 Not Found`: 插件文件不存在。
- `500 Internal Server Error`: 读取文件时出现未预期异常。

---

## 2.5 `GET /102256264.json`

用于 QQ 侧域名校验的接口，路径中的 `102256264` 来自当前项目常量 `BOT_APPID`。

> 当前代码中该接口仅用于返回 Bot AppID 信息；若接入方依赖该接口，请以实际部署结果为准。

---

## 3. WebSocket 连接

## 3.1 连接地址

```text
/server/ws/{group_open_id}/{server_type}/
```

### 路径参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `group_open_id` | `str` | 当前服务器所属群的 OpenID |
| `server_type` | `str` | 服务器类型，见 [ServerType](#52-servertype) |

### 请求头

必须携带：

```http
Authorization: Bearer <server_token>
```

### 连接校验规则

Bot 会按以下顺序校验：

1. 是否提供 `Authorization` / `authorization`
2. 是否以 `Bearer ` 开头
3. 令牌是否有效
4. `server_type` 是否受支持
5. 令牌是否能匹配数据库中的服务器记录
6. 该服务器所属群是否与路径中的 `group_open_id` 一致

### 常见关闭原因

| Code | 原因 |
|---|---|
| `1008` | 缺失认证令牌 / 认证格式错误 / 不支持的服务器类型 |
| `4003` | 无效令牌 / 群 OpenID 不匹配 / 无匹配服务器 |
| `1011` | Bot 内部异常 |

---

## 4. 数据包结构

所有 WebSocket 消息都使用统一 JSON 结构。

```jsonc
{
  "version": "2025.7.18",      // 数据包版本
  "direction": "to_server",    // to_server / to_bot
  "type": "player_list",       // 数据包类型
  "is_request": true,            // 是否属于“请求-响应”链路
  "request_id": "abc123...",   // 请求ID；非请求型可为 null
  "payload": {
    "...": "..."
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `version` | `str` | 是 | 当前包类型的协议版本 |
| `direction` | `PackageDirection` | 是 | 包的语义方向：发往服务器或发往 Bot |
| `type` | `PackageType` | 是 | 包类型 |
| `is_request` | `bool` | 是 | 是否参与请求-响应模式 |
| `request_id` | `str \| null` | 是 | 请求标识；仅 `is_request=true` 时需要有效值 |
| `payload` | `dict[str, any]` | 是 | 业务数据 |

### 重要说明：`is_request` 的实际语义

在当前实现里：

- `is_request = false`：通常表示**单向通知包**，例如 `hello`、`whitelist`、`self_kick`、`unbind_server`
- `is_request = true`：表示**Bot 主动发起的 RPC 调用**以及服务器对该调用的响应

也就是说，**服务器返回给 Bot 的响应包同样需要 `is_request = true`，并携带原始 `request_id`**。

---

## 5. 枚举定义

## 5.1 PackageDirection

| 值 | 说明 |
|---|---|
| `to_server` | Bot -> Server |
| `to_bot` | Server -> Bot |

---

## 5.2 ServerType

| 值 | 说明 |
|---|---|
| `tshock` | TShock 服务器 |
| `tModLoader` | tModLoader 服务器 |
| `bukkit` | Bukkit 服务器 |

> 连接路径中请使用上表原值。

---

## 5.3 WhitelistResult

| 值 | 说明 |
|---|---|
| `accept` | 允许进入服务器 |
| `need_login` | 需要先在 Bot 中完成登录流程 |
| `not_in_whitelist` | 不在白名单中 |
| `in_group_blacklist` | 位于群黑名单中 |
| `in_bot_blacklist` | 位于 Bot 黑名单中（当前代码暂未主动返回） |

---

## 5.4 PackageType

当前代码中定义的包类型如下：

| 类型 | 当前版本 |
|---|---|
| `hello` | `2025.7.18` |
| `whitelist` | `2025.12.18` |
| `player_list` | `2025.7.18` |
| `progress` | `2025.7.18` |
| `look_bag` | `2025.7.18` |
| `world_file` | `2025.7.18` |
| `map_file` | `2025.7.18` |
| `map_image` | `2025.7.18` |
| `self_kick` | `2025.7.18` |
| `call_command` | `2025.7.18` |
| `unbind_server` | `2025.7.18` |
| `heartbeat` | `2025.7.25` |
| `plugin_list` | `2025.7.25` |
| `rank_data` | `2025.7.25` |
| `shop_buy` | `2025.7.25` |
| `shop_condition` | `2025.7.25` |
| `error` | `2026.2.14` |

---

## 6. 数据包类型

## 6.1 `hello`（Server -> Bot）

服务器连接成功后主动上报自身环境及插件信息。

- 版本：`2025.7.18`
- `is_request`: `false`
- `request_id`: `null`

### payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `game_version` | `str` | Terraria 游戏版本 |
| `server_core_version` | `str` | 服务端核心版本，如 TShock 版本 |
| `plugin_version` | `str` | CaiBotLite 适配插件版本 |
| `enable_whitelist` | `bool` | 是否启用 Cai 白名单检查 |
| `system` | `str` | 服务器系统信息 |
| `server_name` | `str` | 服务器名称 / 世界名 |
| `settings` | `dict[str, any]` | 适配插件配置对象 |

### 示例

```json
{
  "version": "2025.7.18",
  "direction": "to_bot",
  "type": "hello",
  "is_request": false,
  "request_id": null,
  "payload": {
    "game_version": "1.4.4.9",
    "server_core_version": "TShock 5.x",
    "plugin_version": "2026.1.29.0",
    "enable_whitelist": true,
    "system": "Windows Server 2022",
    "server_name": "Cai World",
    "settings": {}
  }
}
```

---

## 6.2 `whitelist`（Server <-> Bot）

服务器向 Bot 查询某玩家是否允许进入；Bot 返回检查结果。

- 版本：`2025.12.18`
- 双向包均为 `is_request = false`
- 该包不依赖 `request_id`

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `player_name` | `str` | 玩家名称 |
| `player_ip` | `str` | 玩家 IP |
| `player_uuid` | `str` | 玩家 UUID |

### Bot -> Server payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `player_name` | `str` | 玩家名称 |
| `is_admin` | `bool` | 是否为群管理员 |
| `whitelist_result` | `WhitelistResult` | 白名单 / 登录检查结果 |

---

## 6.3 `player_list`（Bot -> Server -> Bot）

查询在线玩家列表。

- 版本：`2025.7.18`
- 请求包：`is_request = true`
- 响应包：`is_request = true`，并复用原 `request_id`

### Bot -> Server payload

空对象即可：

```json
{}
```

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `server_name` | `str` | 服务器名称 |
| `process` | `str` | 当前进度文字，可为空字符串 |
| `current_online` | `int` | 当前在线人数 |
| `max_online` | `int` | 最大在线人数 |
| `player_list` | `list[str]` | 在线玩家名列表 |

---

## 6.4 `progress`（Bot -> Server -> Bot）

查询世界进度。

- 版本：`2025.7.18`

### Bot -> Server payload

空对象即可。

### Server -> Bot payload

#### 文本模式

| 字段 | 类型 | 说明 |
|---|---|---|
| `is_text` | `bool` | 固定为 `true` |
| `text` | `str` | 直接显示给用户的文本 |

#### 结构化模式

| 字段 | 类型 | 说明 |
|---|---|---|
| `is_text` | `bool` | 固定为 `false` |
| `world_name` | `str` | 世界名 |
| `world_icon` | `str` | 世界图标资源名 |
| `drunk_world` | `bool` | 是否醉酒世界 |
| `zenith_world` | `bool` | 是否天顶世界 |
| `process` | `dict[str, bool]` | Boss / 事件击败状态 |
| `kill_counts` | `dict[str, int]` | Boss 击败次数 |
| `boss_lock` | `dict[str, str]` | 可选，Boss 锁定信息，如刷新时间 |

### `process` 常见键

`King Slime`、`Eye of Cthulhu`、`Eater of Worlds`、`Brain of Cthulhu`、`Queen Bee`、`Deerclops`、`Skeletron`、`Wall of Flesh`、`Queen Slime`、`The Destroyer`、`The Twins`、`Skeletron Prime`、`Plantera`、`Golem`、`Duke Fishron`、`Empress of Light`、`Lunatic Cultist`、`Moon Lord`、`Pillars`、`Tower Stardust`、`Tower Vortex`、`Tower Nebula`、`Tower Solar`、`Goblins`、`Pirates`、`Frost`、`Pumpkin Moon`、`Frost Moon`、`DD2InvasionT1`、`DD2InvasionT2`、`DD2InvasionT3`。

---

## 6.5 `self_kick`（Bot -> Server）

Bot 通知服务器将指定玩家踢出。

- 版本：`2025.7.18`
- `is_request = false`

### payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 要踢出的玩家名 |

---

## 6.6 `call_command`（Bot -> Server -> Bot）

远程执行服务器命令。

- 版本：`2025.7.18`

### Bot -> Server payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `command` | `str` | 命令文本，通常以 `/` 开头 |
| `group_open_id` | `str` | 发起命令的群 OpenID |
| `user_open_id` | `str` | 发起命令的用户 OpenID |

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `output` | `list[str]` | 命令输出行列表；可为空 |

---

## 6.7 `map_image`（Bot -> Server -> Bot）

获取地图 PNG 预览图。

- 版本：`2025.7.18`

### Bot -> Server payload

空对象即可。

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `base64` | `str` | 按本文[编码约定](#8-编码约定)压缩编码后的 PNG 数据 |

---

## 6.8 `world_file`（Bot -> Server -> Bot）

获取世界文件。

- 版本：`2025.7.18`

### Bot -> Server payload

空对象即可。

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 文件名，如 `world.wld` / `world.twld` / `world.zip` |
| `base64` | `str` | 按本文[编码约定](#8-编码约定)压缩编码后的文件数据 |

---

## 6.9 `map_file`（Bot -> Server -> Bot）

获取小地图文件。

- 版本：`2025.7.18`

### Bot -> Server payload

空对象即可。

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | `str` | 文件名，如 `xxx.map` / `xxx.tmap` / `xxx.zip` |
| `base64` | `str` | 按本文[编码约定](#8-编码约定)压缩编码后的文件数据 |

---

## 6.10 `plugin_list`（Bot -> Server -> Bot）

查询插件或模组列表。

- 版本：`2025.7.25`

### Bot -> Server payload

空对象即可。

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `is_mod` | `bool` | `true` 表示模组列表，`false` 表示插件列表 |
| `plugins` | `list[dict]` | 插件 / 模组列表 |

### `plugins` 列表中当前至少应包含

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | `str` | 名称 |
| `Version` | `str` | 版本 |

---

## 6.11 `look_bag`（Bot -> Server -> Bot）

查询玩家背包数据。

- 版本：`2025.7.18`

### Bot -> Server payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `player_name` | `str` | 玩家名 |

### Server -> Bot payload

#### 玩家不存在

| 字段 | 类型 | 说明 |
|---|---|---|
| `exist` | `int` | `0` 表示玩家不存在 |

#### 文本模式

| 字段 | 类型 | 说明 |
|---|---|---|
| `exist` | `int` | 通常为 `1` |
| `is_text` | `bool` | 固定为 `true` |
| `text` | `str` | 文本结果 |

#### 结构化模式

| 字段 | 类型 | 说明 |
|---|---|---|
| `exist` | `int` | 通常为 `1` |
| `is_text` | `bool` | 固定为 `false` |
| `name` | `str` | 玩家名 |
| `inventory` | `list[list[int, int]]` | 背包/猪猪/保险箱/虚空袋等格子数据，元素格式为 `[物品ID, 数量]` |
| `buffs` | `list[int]` | Buff ID 列表 |
| `enhances` | `list[int]` | 永久增益对应物品 ID 列表 |
| `life` | `str` | 生命值文本，如 `500/500` |
| `mana` | `str` | 魔力值文本，如 `200/200` |
| `quests_completed` | `int` | 渔夫任务完成次数 |
| `economic` | `dict` | 经济插件扩展信息 |

### `economic` 常见键

| 字段 | 类型 | 说明 |
|---|---|---|
| `Coins` | `str` | 货币信息 |
| `LevelName` | `str` | 职业 / 等级名称 |
| `Skill` | `str` | 技能信息 |

---

## 6.12 `rank_data`（Bot -> Server -> Bot）

查询排行榜信息。

- 版本：`2025.7.25`

### Bot -> Server payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `rank_type` | `str` | 排行榜类型；空字符串表示仅查询支持列表 |
| `arg` | `str` | 可选参数；无参数时传空字符串 |

### Server -> Bot payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `support_rank_types` | `list[str]` | 当前服务器支持的排行类型 |
| `rank_type_support` | `bool` | 所请求的排行类型是否受支持 |
| `need_arg` | `bool` | 该排行是否需要额外参数 |
| `arg_support` | `bool` | 当需要参数时，当前参数是否合法 |
| `message` | `str` | 参数错误时的提示文本 |
| `support_args` | `list[str]` | 支持的参数列表 |
| `rank` | `dict` | 排行正文 |

### `rank` 结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `title` | `str` | 排行标题 |
| `rank_lines` | `dict[str, str]` | 键为名称，值为对应数据 |

---

## 6.13 `unbind_server`（Bot -> Server）

Bot 通知服务器主动解绑。

- 版本：`2025.7.18`
- `is_request = false`

### payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `reason` | `str` | 解绑原因 |

---

## 6.14 `error`（Server -> Bot）

服务器用于响应 Bot 发起的 RPC 失败。

- 版本：`2026.2.14`
- `is_request = true`
- 必须携带原始 `request_id`

### payload

| 字段 | 类型 | 说明 |
|---|---|---|
| `error` | `str` | 错误详情文本 |

### 使用场景

例如服务器处理 `call_command`、`progress`、`look_bag` 等请求时发生异常，可以返回：

```json
{
  "version": "2026.2.14",
  "direction": "to_bot",
  "type": "error",
  "is_request": true,
  "request_id": "same-as-request",
  "payload": {
    "error": "stack trace or friendly message"
  }
}
```

---

## 6.15 预留 / 尚未在当前 Bot 侧消费的包

以下包类型已在枚举中定义版本，但当前仓库代码中尚未看到明确消费逻辑，建议仅作为预留能力使用：

- `heartbeat`
- `shop_buy`
- `shop_condition`

如果后续扩展这些类型，建议继续遵循本文统一包结构与错误返回规范。

---

## 7. 错误处理

## 7.1 HTTP 层

- 参数错误、文件不存在、令牌过期等问题通过 HTTP 状态码表达。
- 常见状态码：`403`、`404`、`500`。

## 7.2 WebSocket / 业务层

- 鉴权失败或握手非法时，Bot 直接关闭连接。
- 业务请求失败时，服务器应优先返回 `error` 包，而不是静默超时。
- 如果服务器长时间未响应，Bot 侧默认会按调用超时处理：
  - 普通请求默认约 `10s`
  - 地图/文件请求约 `60s`

---

## 8. 编码约定

## 8.1 文件 / 图片二进制传输

对于 `map_image`、`world_file`、`map_file` 这类二进制内容，当前 Bot 侧约定的 `payload.base64` 编码流程为：

1. 原始文件字节 `bytes`
2. 转为普通 Base64 字符串
3. 对该 Base64 字符串的 UTF-8 字节进行 `gzip` 压缩
4. 再将压缩结果整体 Base64 编码

服务端发送时应保证 Bot 能按以下逆过程恢复：

```text
payload.base64
-> Base64 decode
-> gzip decompress
-> 得到“原始文件的 Base64 字符串”
-> 再 Base64 decode
-> 得到最终 bytes
```

## 8.2 版本兼容

Bot 会检查收到的数据包 `version` 是否与 `type` 当前版本一致；版本落后时会记录警告日志，但不会仅因版本较低立即拒绝处理。

## 8.3 扩展字段

`payload` 允许在兼容前提下扩展额外字段；但已定义字段名与类型不应随意改变，否则可能导致 Bot 解析失败。
