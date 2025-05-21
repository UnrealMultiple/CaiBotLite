from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent, MessageSegment

from src.utils.terraria_id_helper import get_item_by_name_or_id, get_npc_by_name_or_id, get_project_by_name_or_id, get_buff_by_name_or_id, \
    get_prefix_by_name_or_id


def msg_cut(msg: str) -> list:
    msg = msg.split(" ")
    msg = [word for word in msg if word]
    return msg


def paginate(data, page_size, page_number):
    # 计算开始和结束的索引
    start = (page_number - 1) * page_size
    end = start + page_size
    # 返回分页后的数据
    return data[start:end]


# wiki = on_startswith(("搜索", "wiki", "Wiki", "WIKI"))
#
#
# @wiki.handle()
# async def wiki_handle(event: GroupMessageEvent):
#     group_id = Group.get_group(event.group_id)
#     if group_id is None or not group_id.enable_server_bot:
#         return
#     msg = event.get_plaintext().replace("搜索 ", "").replace("wiki ", "").replace("Wiki ", "").replace("WIKI ",
#                                                                                                        "").replace(
#         "搜索", "").replace("wiki", "").replace("Wiki", "").replace("WIKI", "")
#     if msg == "":
#         await wiki.finish(MessageSegment.at(event.user_id) +
#                           f"\n『Terraria Wiki』\n"
#                           f"已为你找到以下TerrariaWiki网站：\n1"
#                           f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/Terraria_Wiki\n"
#                           f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Terraria_Wiki\n"
#                           f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh")
#     await wiki.finish(MessageSegment.at(event.user_id) +
#                       f"\n『Terraria Wiki』\n"
#                       f"已从Wiki上帮你找到[{msg}]，点击对应链接查看：\n1"
#                       f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/{parse.quote(msg)}\n"
#                       f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Special:%E6%90%9C%E7%B4%A2?search={parse.quote(msg)}\n"
#                       f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh/index.php?search={parse.quote(msg)}")


search_item = on_command("si", aliases={"搜物品"}, force_whitespace=True)


@search_item.handle()
async def search_item_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_item.finish(f'\n『搜物品』\n'
                                 + "格式错误!正确格式: 搜物品 <物品名字|ID>")

    await search_item.finish(MessageSegment.text(f'\n『搜物品』\n') +
                             get_item_by_name_or_id(msg[1]))



search_npc = on_command("sn", aliases={"搜生物"}, force_whitespace=True)


@search_npc.handle()
async def search_npc_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_npc.finish(f'\n『搜生物』\n'
                                + "格式错误!正确格式: 搜生物 <生物名字|ID>")

    await search_npc.finish(MessageSegment.text(f'\n『搜生物』\n') +
                            get_npc_by_name_or_id(msg[1]))


search_project = on_command("sp", aliases={"搜弹幕"}, force_whitespace=True)


@search_project.handle()
async def search_project_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_project.finish(f'\n『搜弹幕』\n'
                                    + "格式错误!正确格式: 搜弹幕 <弹幕名字|ID>")

    await search_project.finish(MessageSegment.text(f'\n『搜弹幕』\n') +
                                get_project_by_name_or_id(msg[1]))


search_buff = on_command("sb", aliases={"搜增益"}, force_whitespace=True)


@search_buff.handle()
async def search_buff_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_buff.finish(f'\n『搜增益』\n'
                                 + "格式错误!正确格式: 搜增益 <增益名字|ID>")

    await search_buff.finish(MessageSegment.text(f'\n『搜增益』\n') + get_buff_by_name_or_id(msg[1]))


search_prefix = on_command("sx", aliases={"搜修饰"}, force_whitespace=True)


@search_prefix.handle()
async def search_prefix_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_prefix.finish(f'\n『搜修饰语』\n'
                                   + "格式错误!正确格式: 搜修饰 <修饰语|ID>")

    await search_prefix.finish(MessageSegment.text(f'\n『搜修饰语』\n') +
                               get_prefix_by_name_or_id(msg[1]))
