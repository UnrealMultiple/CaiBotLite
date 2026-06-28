from nonebot import on_command, on_message
from nonebot.adapters.qq import (
    GroupAtMessageCreateEvent,
    MessageSegment,
    GroupMessageCreateEvent,
)

from caibotlite.constants import BOT_VERSION
from caibotlite.dependencies import Session, Args
from caibotlite.managers import (
    ConnectionManager,
    GroupManager,
    ServerManager,
    UserManager,
)
from caibotlite.markdown.keyboard import (
    bot_admin_group_keyboard,
    reedit_keyboard,
    permission_request_keyboard,
)
from caibotlite.markdown.tag import cmd_input_tag
from caibotlite.services import Statistics

about = on_command("关于", force_whitespace=True, block=True)


@about.handle()
async def _(session: Session):
    await about.finish(
        MessageSegment.markdown(
            f"## 📖 关于\n"
            f"**CaiBotLite v{BOT_VERSION}**\n"
            f"🎉 **开发者**：Cai\n\n"
            f"✨ **感谢**：\n"
            f"- 迅猛龙 [提供服务器]\n"
            f"- 羽学 [代码贡献]\n"
            f"- 2409 [代码贡献]\n"
            f"- 西江 [代码贡献]\n"
            f"- 熙恩 [代码贡献]\n"
            f"- Star gazer [背景图]\n"
            f"- 命乌 [TR汉化包]\n"
            f"- 葉玖 [可爱捏(?)]\n"
            f"- 泉港一中 [周六补课]\n"
            f"- 福州大学 [暑假51天]\n\n"
            f"⚡ 当前已加入**{await GroupManager.count_all_groups(session)}**个群\n"
            f"绑定**{await UserManager.count_all_users(session)}**名玩家，检查白名单**{Statistics.whitelist_check}**次\n"
            f"绑定**{await ServerManager.count_all_servers(session)}**台服务器，当前已连接**{len(ConnectionManager.connected_servers)}**台\n\n"
            f"*Powered by Nonebot2*"
        )
        + bot_admin_group_keyboard
    )


server_statistics = on_command("统计", force_whitespace=True, block=True)


@server_statistics.handle()
async def _():
    version_count = {}
    tshock_count = {}
    os_count = {}
    whitelist_count = 0
    for server in ConnectionManager.connected_servers.values():
        version = server.server_info.plugin_version
        if version in version_count:
            version_count[version] += 1
        else:
            version_count[version] = 1

        tshock_version = server.server_info.server_core_version
        if tshock_version in tshock_count:
            tshock_count[tshock_version] += 1
        else:
            tshock_count[tshock_version] = 1

        if server.server_info.enable_whitelist:
            whitelist_count += 1

        os = server.server_info.system
        if os in os_count:
            os_count[os] += 1
        else:
            os_count[os] = 1

    sorted_versions = sorted(version_count.items())
    tshock_sorted_versions = sorted(tshock_count.items())
    tshock_info = "\n".join(
        [f"- v{version} > {count}" for version, count in tshock_sorted_versions]
    )
    version_info = "\n".join(
        [f"- v{version} > {count}" for version, count in sorted_versions]
    )
    os_info = "\n".join([f"- {os} > {count}" for os, count in os_count.items()])
    await server_statistics.finish(
        MessageSegment.markdown(
            f"## 📊 CaiBot统计\n\n"
            f"### 🔭 适配插件版本\n"
            f"{version_info}\n\n"
            f"### #️⃣ TShock版本\n"
            f"{tshock_info}\n\n"
            f"### ✨ 系统版本\n"
            f"{os_info}\n\n"
            f"### 📖 白名单服务器\n"
            f"{whitelist_count}台"
        )
    )


permission_request = on_command("权限请求", force_whitespace=True, block=True)


@permission_request.handle()
async def _(event: GroupAtMessageCreateEvent | GroupMessageCreateEvent, args: Args):
    if len(args) == 0:
        await permission_request.finish(
            MessageSegment.markdown(
                "## 🍥 权限请求\n"
                "格式错误！\n"
                f"正确格式: {cmd_input_tag('/权限请求')} `<本群群号>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    await permission_request.finish(
        MessageSegment.markdown(
            f"## 🍥 权限请求\n"
            f"> 需要群主授权\n"
            f"1. 机器人获取**全部**消息范围 -> 无需@即可使用\n"
            f"2. 启用主动消息 -> 群内推送登录请求"
        )
        + permission_request_keyboard(args[0])
    )


pre_receive_msg = on_message(priority=-114514, block=False)


@pre_receive_msg.handle()
async def _(event: GroupAtMessageCreateEvent | GroupMessageCreateEvent):
    Statistics.message_received += 1
