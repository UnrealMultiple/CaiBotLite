import re
from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent, Bot, MessageSegment

from common.statistics import Statistics
from plugins import cai_api


changelog = on_command("公告")
@changelog.handle()
async def changelog_handle(bot: Bot, event: GroupAtMessageCreateEvent):
    await bot.send_to_group(event.group_openid, MessageSegment.markdown(""))



about = on_command("关于", force_whitespace=True)

@about.handle()
async def ban_about_handle(event: GroupAtMessageCreateEvent):
    statistics = Statistics.get_statistics()
    await about.finish(f'\n『关于』\n'
                       f'📖CaiBotLite\n'
                       f'🎉开发者: Cai\n'
                       f'✨感谢: \n'
                       f'迅猛龙 [提供服务器]\n'
                       f'羽学 [代码贡献]\n'
                       f'2409: [代码贡献]\n'
                       f'西江 [代码贡献]\n'
                       f'熙恩 [代码贡献]\n'
                       f'Star gazer [背景图]\n'
                       f'命乌 [TR汉化包]\n'
                       f'葉玖 [可爱捏(?)]\n'
                       f'泉港一中 [周六补课]\n'
                       f'🙏反馈群: 991556763\n'
                       f'⚡当前已加入{statistics.total_group}个群\n'
                       f'绑定{statistics.total_users}名玩家,检查白名单{statistics.check_whitelist}次\n'
                       f'绑定{statistics.total_servers}台服务器,当前已连接{len(cai_api.server_connection_manager.connections)}台\n'
                       f'Powered by Nonebot2')


def version_key(version):
    return [int(part) if part.isdigit() else part for part in re.split('(\d+)', version)]


server_statistics = on_command("CaiBot统计", force_whitespace=True)


@server_statistics.handle()
async def plugin_version_handle(event: GroupAtMessageCreateEvent):
    version_count = {}
    tshock_count = {}
    os_count = {}
    whitelist_count = 0
    for server in cai_api.server_connection_manager.connections.values():
        version = server.plugin_version
        if version in version_count:
            version_count[version] += 1
        else:
            version_count[version] = 1

        tshock_version = server.tshock_version
        if tshock_version in tshock_count:
            tshock_count[tshock_version] += 1
        else:
            tshock_count[tshock_version] = 1

        if server.whitelist:
            whitelist_count += 1

        os = server.os
        if os in os_count:
            os_count[os] += 1
        else:
            os_count[os] = 1

    sorted_versions = sorted(version_count.items(), key=lambda item: version_key(item[0]), reverse=True)
    tshock_sorted_versions = sorted(tshock_count.items())
    tshock_info = "\n".join([f"v{version} > {count}" for version, count in tshock_sorted_versions])
    version_info = "\n".join([f"v{version} > {count}" for version, count in sorted_versions])
    os_info = "\n".join([f"{os} > {count}" for os, count in os_count.items()])
    await server_statistics.finish(f'\n『CaiBot统计』\n'
                                   f'🔭适配插件版本:\n'
                                   f'{version_info}\n'
                                   f'#️⃣TShock版本:\n'
                                   f'{tshock_info}\n'
                                   f'✨系统版本:\n'
                                   f'{os_info}\n'
                                   f'📖白名单服务器:\n'
                                   f'{whitelist_count}台')

# ping = on_command("ping", force_whitespace=True)


# @ping.handle()
# async def ping_handle(event: GroupMessageEvent):
#     msg = msg_cut(event.get_plaintext())
#     if len(msg) != 3:
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"格式错误!正确格式: ping <服务器地址> <端口>")
#     try:
#         adr = socket.gethostbyname(msg[1])
#     except:
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"没有找到服务器欸？")
#
#     try:
#         time, packId = await ping_server(adr, int(msg[2]))
#     except TimeoutError:
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"服务器连接超时！")
#     except Exception as ex:
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"连接失败！\n错误：{str(ex)}")
#     packId = str(packId)
#     if packId == "2":
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"PING到服务器啦!\n"
#                           f"延迟: {time:.2f}ms, 响应数据包：{packId}\n"
#                           f"然后小小Cai被服务器一脚踢了出去，呜呜呜...")
#     if packId != "LegacyMultiplayer4" and packId != "3":
#         await ping.finish(MessageSegment.at(event.user_id) +
#                           f'\n『PING』\n' +
#                           f"PING到服务器啦!\n"
#                           f"延迟: {time:.2f}ms, 响应数据包：{packId}\n"
#                           f"但是小小Cai发现这好像不是Terraria服务器？")
#     await ping.finish(MessageSegment.at(event.user_id) +
#                       f'\n『PING』\n' +
#                       f"PING到服务器啦!\n"
#                       f"延迟: {time:.2f}ms, 响应数据包：{packId}")
