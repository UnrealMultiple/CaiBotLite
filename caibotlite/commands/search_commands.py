from nonebot import on_command
from nonebot.adapters.qq import MessageSegment, GroupAtMessageCreateEvent

from caibotlite.dependencies import Args
from caibotlite.markdown.keyboard import reedit_keyboard
from caibotlite.markdown.tag import cmd_input_tag
from caibotlite.services import TerrariaSearch

search_item = on_command("si", aliases={"搜物品"}, force_whitespace=True, block=True)


@search_item.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args):
    if len(args) == 0:
        await search_item.finish(
            MessageSegment.markdown(
                "## 🍥 搜物品\n"
                "格式错误！"
                f"正确格式: {cmd_input_tag('/搜物品')} `<物品名字|ID>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    result = TerrariaSearch.search_item(" ".join(args))
    await search_item.finish(MessageSegment.markdown(f"## 🍥 搜物品\n{result}"))


search_npc = on_command("sn", aliases={"搜生物"}, force_whitespace=True, block=True)


@search_npc.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args):
    if len(args) == 0:
        await search_npc.finish(
            MessageSegment.markdown(
                "## 🍥 搜生物\n"
                "格式错误！"
                f"正确格式: {cmd_input_tag('/搜生物')} `<生物名字|ID>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    result = TerrariaSearch.search_npc(" ".join(args))
    await search_npc.finish(MessageSegment.markdown(f"## 🍥 搜生物\n{result}"))


search_project = on_command("sp", aliases={"搜弹幕"}, force_whitespace=True, block=True)


@search_project.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args):
    if len(args) == 0:
        await search_project.finish(
            MessageSegment.markdown(
                "## 🍥 搜弹幕\n"
                "格式错误！"
                f"正确格式: {cmd_input_tag('/搜弹幕')} `<弹幕名字|ID>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    result = TerrariaSearch.search_projectile(" ".join(args))
    await search_project.finish(MessageSegment.markdown(f"## 🍥 搜弹幕\n{result}"))


search_buff = on_command("sb", aliases={"搜增益"}, force_whitespace=True, block=True)


@search_buff.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args):
    if len(args) == 0:
        await search_buff.finish(
            MessageSegment.markdown(
                "## 🍥 搜增益\n"
                "格式错误！\n"
                f"正确格式: {cmd_input_tag('/搜增益')} `<增益名字|ID>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    result = TerrariaSearch.search_buff(" ".join(args))
    await search_buff.finish(MessageSegment.markdown(f"## 🍥 搜增益\n{result}"))


search_prefix = on_command("sx", aliases={"搜修饰"}, force_whitespace=True, block=True)


@search_prefix.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args):
    if len(args) == 0:
        await search_prefix.finish(
            MessageSegment.markdown(
                "## 🍥 搜修饰语\n"
                "格式错误！\n"
                f"正确格式: {cmd_input_tag('/搜修饰')} `<修饰语|ID>`"
            )
            + reedit_keyboard(event.get_plaintext())
        )

    result = TerrariaSearch.search_prefix(" ".join(args))
    await search_prefix.finish(MessageSegment.markdown(f"## 🍥 搜修饰语\n{result}"))
