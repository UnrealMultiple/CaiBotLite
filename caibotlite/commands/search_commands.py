from nonebot import on_command
from nonebot.adapters.qq import MessageSegment

from caibotlite.dependencies import Args
from caibotlite.services import TerrariaSearch

search_item = on_command("si", aliases={"搜物品"}, force_whitespace=True, block=True)


@search_item.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_item.finish(
            f"\n『搜物品』\n" + "格式错误!正确格式: 搜物品 <物品名字|ID>"
        )

    await search_item.finish(
        MessageSegment.text(f"\n『搜物品』\n") + TerrariaSearch.search_item(" ".join(args))
    )


search_npc = on_command("sn", aliases={"搜生物"}, force_whitespace=True, block=True)


@search_npc.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_npc.finish(
            f"\n『搜生物』\n" + "格式错误!正确格式: 搜生物 <生物名字|ID>"
        )

    await search_npc.finish(
        MessageSegment.text(f"\n『搜生物』\n") + TerrariaSearch.search_npc(" ".join(args))
    )


search_project = on_command("sp", aliases={"搜弹幕"}, force_whitespace=True, block=True)


@search_project.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_project.finish(
            f"\n『搜弹幕』\n" + "格式错误!正确格式: 搜弹幕 <弹幕名字|ID>"
        )

    await search_project.finish(
        MessageSegment.text(f"\n『搜弹幕』\n") + TerrariaSearch.search_projectile(" ".join(args))
    )


search_buff = on_command("sb", aliases={"搜增益"}, force_whitespace=True, block=True)


@search_buff.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_buff.finish(
            f"\n『搜增益』\n" + "格式错误!正确格式: 搜增益 <增益名字|ID>"
        )

    await search_buff.finish(
        MessageSegment.text(f"\n『搜增益』\n") + TerrariaSearch.search_buff(" ".join(args))
    )


search_prefix = on_command("sx", aliases={"搜修饰"}, force_whitespace=True, block=True)


@search_prefix.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_prefix.finish(
            f"\n『搜修饰语』\n" + "格式错误!正确格式: 搜修饰 <修饰语|ID>"
        )

    await search_prefix.finish(
        MessageSegment.text(f"\n『搜修饰语』\n") + TerrariaSearch.search_prefix(" ".join(args))
    )


search_config = on_command("sc", aliases={"搜配置"}, force_whitespace=True, block=True)


@search_config.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_config.finish(
            f"\n『搜配置』\n" + "格式错误!正确格式: 搜配置 <键|描述>"
        )

    await search_config.finish(
        MessageSegment.text(f"\n『搜配置』\n") + TerrariaSearch.search_config(" ".join(args))
    )


search_perm = on_command("sperm", aliases={"搜权限"}, force_whitespace=True, block=True)


@search_perm.handle()
async def _(args: Args):
    if len(args) == 0:
        await search_perm.finish(
            f"\n『搜权限』\n" + "格式错误!正确格式: 搜权限 <权限名|描述>"
        )

    await search_perm.finish(
        MessageSegment.text(f"\n『搜权限』\n") + TerrariaSearch.search_config(" ".join(args))
    )
