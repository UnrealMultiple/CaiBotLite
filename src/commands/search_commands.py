from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent
from nonebot.adapters.qq.models.common import *
from nonebot.params import CommandArg

from src.utils.terraria_id_helper import *


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


rows = [
    InlineKeyboardRow(
        buttons=[
            Button(
                id="1",
                render_data=RenderData(label="⬅️上一页", visited_label="⬅️上一页"),
                action=Action(
                    type=1,
                    permission=Permission(type=1, specify_role_ids=["1", "2", "3"]),
                    click_limit=10,
                    unsupport_tips="兼容文本",
                    data="data",
                    at_bot_show_channel_list=True,
                ),
            ),
            Button(
                id="2",
                render_data=RenderData(label="➡️下一页", visited_label="➡️下一页"),
                action=Action(
                    type=1,
                    permission=Permission(type=1, specify_role_ids=["1", "2", "3"]),
                    click_limit=10,
                    unsupport_tips="兼容文本",
                    data="data",
                    at_bot_show_channel_list=True,
                ),
            ),
        ]
    ),
    InlineKeyboardRow(
        buttons=[
            Button(
                id="3",
                render_data=RenderData(
                    label="📅 打卡（5）", visited_label="📅 打卡（5）"
                ),
                action=Action(
                    type=1,
                    permission=Permission(type=1, specify_role_ids=["1", "2", "3"]),
                    click_limit=10,
                    unsupport_tips="兼容文本",
                    data="data",
                    at_bot_show_channel_list=True,
                ),
            )
        ]
    ),
]

wiki = on_command("wiki", aliases={"百科"}, force_whitespace=True)


@wiki.handle()
async def wiki_handle(event: GroupAtMessageCreateEvent):
    await wiki.finish(
        MessageSegment.keyboard(MessageKeyboard(content=InlineKeyboard(rows=rows)))
    )

    # if msg == "":
    #     await wiki.finish(MessageSegment.at(event.user_id) +
    #                       f"\n『Terraria Wiki』\n"
    #                       f"已为你找到以下TerrariaWiki网站：\n1"
    #                       f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/Terraria_Wiki\n"
    #                       f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Terraria_Wiki\n"
    #                       f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh")
    # await wiki.finish(MessageSegment.at(event.user_id) +
    #                   f"\n『Terraria Wiki』\n"
    #                   f"已从Wiki上帮你找到[{msg}]，点击对应链接查看：\n1"
    #                   f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/{parse.quote(msg)}\n"
    #                   f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Special:%E6%90%9C%E7%B4%A2?search={parse.quote(msg)}\n"
    #                   f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh/index.php?search={parse.quote(msg)}")


search_item = on_command("si", aliases={"搜物品"}, force_whitespace=True)


@search_item.handle()
async def search_item_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_item.finish(
            f"\n『搜物品』\n" + "格式错误!正确格式: 搜物品 <物品名字|ID>"
        )

    await search_item.finish(
        MessageSegment.text(f"\n『搜物品』\n") + get_item_by_name_or_id(msg[1])
    )


search_npc = on_command("sn", aliases={"搜生物"}, force_whitespace=True)


@search_npc.handle()
async def search_npc_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_npc.finish(
            f"\n『搜生物』\n" + "格式错误!正确格式: 搜生物 <生物名字|ID>"
        )

    await search_npc.finish(
        MessageSegment.text(f"\n『搜生物』\n") + get_npc_by_name_or_id(msg[1])
    )


search_project = on_command("sp", aliases={"搜弹幕"}, force_whitespace=True)


@search_project.handle()
async def search_project_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_project.finish(
            f"\n『搜弹幕』\n" + "格式错误!正确格式: 搜弹幕 <弹幕名字|ID>"
        )

    await search_project.finish(
        MessageSegment.text(f"\n『搜弹幕』\n") + get_project_by_name_or_id(msg[1])
    )


search_buff = on_command("sb", aliases={"搜增益"}, force_whitespace=True)


@search_buff.handle()
async def search_buff_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_buff.finish(
            f"\n『搜增益』\n" + "格式错误!正确格式: 搜增益 <增益名字|ID>"
        )

    await search_buff.finish(
        MessageSegment.text(f"\n『搜增益』\n") + get_buff_by_name_or_id(msg[1])
    )


search_prefix = on_command("sx", aliases={"搜修饰"}, force_whitespace=True)


@search_prefix.handle()
async def search_prefix_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_prefix.finish(
            f"\n『搜修饰语』\n" + "格式错误!正确格式: 搜修饰 <修饰语|ID>"
        )

    await search_prefix.finish(
        MessageSegment.text(f"\n『搜修饰语』\n") + get_prefix_by_name_or_id(msg[1])
    )


search_config = on_command("sc", aliases={"搜配置"}, force_whitespace=True)


@search_config.handle()
async def search_config_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_config.finish(
            f"\n『搜配置』\n" + "格式错误!正确格式: 搜配置 <键|描述>"
        )

    await search_config.finish(
        MessageSegment.text(f"\n『搜配置』\n") + get_config_by_name_or_id(msg[1])
    )


search_perm = on_command("sperm", aliases={"搜权限"}, force_whitespace=True)


@search_perm.handle()
async def search_perm_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await search_perm.finish(
            f"\n『搜权限』\n" + "格式错误!正确格式: 搜权限 <权限名|描述>"
        )

    await search_perm.finish(
        MessageSegment.text(f"\n『搜权限』\n") + get_permission_by_name_or_id(msg[1])
    )
