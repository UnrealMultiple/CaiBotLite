from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from common.group import Group
from common.group_helper import GroupHelper
from common.statistics import Statistics
from common.user import User


def msg_cut(msg: str) -> list:
    msg = msg.split(" ")
    msg = [word for word in msg if word]
    return msg


bind_parent_group = on_command("绑定父群", force_whitespace=True)


@bind_parent_group.handle()
async def bind_parent_group_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid, True):
        group = Group.get_group(event.group_openid)
        if len(msg) != 2:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           f"格式错误!正确格式: 绑定父群 <父群ID> [只在本群有效]\n"
                                           f"TIPS: 使用'/获取群信息'获取群父群ID")
        if group.parent:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           f"本群已绑定父群[{group.parent}]!\n"
                                           f"使用'/解绑父群'解除绑定")

        father_group = Group.get_group(msg[1], True)

        if father_group is None:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           f"没有找到ID为[{(msg[1])}]的群!")
        if event.author.union_openid not in father_group.admins:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           f"没有权限!\n"
                                           f"你必须是父群的管理员才能进行此操作")

        if father_group.open_id == group.open_id:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           "StackOverFlow!\n"
                                           "父群不能是自己")

        if father_group.parent:
            await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                           "我的附庸的附庸不是我附庸 :(\n"
                                           "父群不能是子群")
        group.parent = father_group.open_id
        group.update()
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       f"已将[{msg[1]}]设为本群父群!")
    else:
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       "没有权限!\n"
                                       "只允许BOT管理员使用")


unbind_parent_group = on_command("解绑父群", force_whitespace=True)


@unbind_parent_group.handle()
async def unbind_parent_group_handle(event: GroupAtMessageCreateEvent):
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid, True):
        group = Group.get_group(event.group_openid, True)
        if not group.parent:
            await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                             f"本群没有已绑定的父群!\n"
                                             f"使用'/绑定父群 <群ID>'添加父群")

        group.parent = ""
        group.update()
        await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                         f"已解绑父群!")
    else:
        await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                         "没有权限!\n"
                                         "只允许BOT管理员使用\n"
                                         "TIPS: BOT添加者为默认管理员")


get_group_info = on_command("获取群信息", aliases={"获取群信息"}, force_whitespace=True)


@get_group_info.handle()
async def get_group_info_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid, True)
    sub_group = group.get_subgroup()
    admin_names = []
    black_names = []
    for i in group.admins:
        user = User.get_user(group.open_id, i)
        if user is None:
            admin_names.append(f"未添加白名单({i})")
        else:
            admin_names.append(user.name)
    for i in group.black_list:
        user = User.get_user(group.open_id, i)
        if user is None:
            black_names.append(f"未添加白名单({i})")
        else:
            black_names.append(user.name)
    await get_group_info.finish(f'\n『群信息』\n'
                                f'群ID: {event.group_openid}\n'
                                f'父群: {group.parent if group.parent else "无"}\n'
                                f'子群: {",".join(sub_group) if len(sub_group)!=0 else "无"}\n'
                                f'用户数: {Statistics.get_group_user_count(event.group_openid)}\n'
                                f'管理列表: {",".join(admin_names) if len(admin_names)!=0 else "无"}\n'
                                f'黑名单: {",".join(black_names) if len(black_names)!=0 else "无"}'
                                )



# apply_admin = on_command("授权管理", force_whitespace=True)
#
#
# @apply_admin.handle()
# async def apply_admin_handle(bot: Bot, event: GroupAtMessageCreateEvent):
#     user = User.get_user(event.group_openid, event.author.union_openid)
#     if user is None:
#         await apply_admin.finish(f'\n『管理授权』\n' +
#                                  f"你没有绑定捏!")
#     else:
#         keyboard = MessageKeyboard()
#         keyboard.open_id = "102256264_1738137606"
#         await bot.send_to_group(event.group_openid,
#                                 MessageSegment.markdown("102256264_1738136945") + MessageSegment.keyboard(keyboard))


# access_admin = on_keyword({"102256264_1738137606"})
# @access_admin.handle()
# async def access_admin_handle(event: Gro):
#     user = User.get_user(event.author.union _openid)
#     if user is None:
#         await apply_admin.finish(f'\n『管理授权』\n' +
#                                f"你没有绑定捏!")
#     else:
#         keyboard = MessageKeyboard()
#         keyboard.open_id = "102256264_1738137606"
#         await apply_admin.finish(MessageSegment.markdown("102256264_1738136945")+MessageSegment.keyboard(keyboard))

list_admin = on_command("管理列表", force_whitespace=True)



@list_admin.handle()
async def list_admin_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    names = []
    for i in group.admins:
        user = User.get_user(group.open_id, i)
        if user is None:
            names.append(f"未添加白名单({i})")
        else:
            names.append(user.name)
    if len(names) == 0 or names[0] == "ERROR_NONE":
        await list_blacklist.finish(f'\n『BOT管理』\n' +
                                    f"本群居然没有管理?\n"
                                    f"请尝试移除并重新添加机器人")
    else:
        await list_admin.finish(f'\n『BOT管理』\n' +
                               f"\n".join(names))



add_admin = on_command("添加管理", aliases={"添加管理员"}, force_whitespace=True)
@add_admin.handle()
async def add_admin_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):
        group = Group.get_group(event.group_openid)
        if group is None:
            return
        else:
            if len(msg) != 2:
                await add_admin.finish(f'\n『BOT管理』\n' +
                                       f"格式错误!正确格式: 添加管理 <玩家名> [只在本群有效]\n"
                                       f"TIPS: BOT添加者为默认管理员")

            user = User.get_user_by_name(event.group_openid, msg[1])
            if user is None:
                await add_admin.finish(f'\n『BOT管理』\n' +
                                       f"没有找到名为[{(msg[1])}]的用户!")

            if user.open_id in group.admins:
                await add_admin.finish(f'\n『BOT管理』\n' +
                                       "该用户已是本群BOT管理!")
            else:

                group.admins.append(user.open_id)
                group.update()
                await add_admin.finish(f'\n『BOT管理』\n' +
                                       f"已将[{msg[1]}]设为本群BOT管理!")
    else:
        await add_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "只允许BOT管理员使用\n"
                               "TIPS: BOT添加者为默认管理员")


del_admin = on_command("删除管理", aliases={"删除管理员"}, force_whitespace=True)


@del_admin.handle()
async def add_admin_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):

        group = Group.get_group(event.group_openid)
        if group is None:
            return
        else:
            if len(msg) != 2:
                await del_admin.finish(f'\n『BOT管理』\n' +
                                       f"格式错误!正确格式: 删除管理 <玩家名> [只在本群有效]")

            user = User.get_user_by_name(event.group_openid, msg[1])
            if user is None:
                await del_admin.finish(f'\n『BOT管理』\n' +
                                       f"没有找到名为[{(msg[1])}]的用户!")

            if user.open_id in group.admins:
                if len(group.admins) == 1:
                    await del_admin.finish(f'\n『BOT管理』\n' +
                                           "群内至少需要1名管理!")
                group.admins.remove(user.open_id)
                group.update()
                await del_admin.finish(f'\n『BOT管理』\n' +
                                       f"[{msg[1]}]不再是本群BOT管理!")

            else:
                await del_admin.finish(f'\n『BOT管理』\n' +
                                       "该用户不是本群BOT管理!")
    else:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "只允许BOT管理员使用")


list_blacklist= on_command("黑名单列表", force_whitespace=True)



@list_blacklist.handle()
async def list_blacklist_handle(event: GroupAtMessageCreateEvent):
    group = Group.get_group(event.group_openid)
    names = []
    for i in group.black_list:
        user = User.get_user(group.open_id, i)
        if user is None:
            names.append(f"未添加白名单({i})")
        else:
            names.append(user.name)

    if len(names) == 0:
        await list_blacklist.finish(f'\n『BOT黑名单』\n' +
                                    f"小黑屋啥也没有捏~")
    else:
        await list_blacklist.finish(f'\n『BOT黑名单』\n' +
                               f"\n".join(names))

add_blacklist = on_command("添加黑名单", force_whitespace=True)


@add_blacklist.handle()
async def add_admin_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):

        group = Group.get_group(event.group_openid)
        if group is None:
            return
        else:
            if len(msg) != 2:
                await add_blacklist.finish(f'\n『Ban』\n' +
                                           f"格式错误!正确格式: 添加黑名单 <玩家名> [只在本群有效]")

            user = User.get_user_by_name(event.group_openid, msg[1])
            if user is None:
                await add_blacklist.finish(f'\n『Ban』\n' +
                                           f"没有找到名为[{(msg[1])}]的玩家!")

            if user.open_id in group.black_list:
                await add_blacklist.finish(f'\n『Ban』\n' +
                                           "该玩家已被本群封禁!")
            else:
                group.black_list.append(user.open_id)
                group.update()
                await add_blacklist.finish(f'\n『Ban』\n' +
                                           f"已封禁[{msg[1]}]!")
    else:
        await add_blacklist.finish(f'\n『Ban』\n' +
                                   "没有权限!\n"
                                   "只允许BOT管理员使用")


del_blacklist = on_command("删除黑名单", force_whitespace=True)


@del_blacklist.handle()
async def add_admin_handle(event: GroupAtMessageCreateEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.has_permission(event.group_openid, event.author.union_openid):

        group = Group.get_group(event.group_openid)
        if group is None:
            return
        else:
            if len(msg) != 2:
                await del_blacklist.finish(f'\n『Ban』\n' +
                                           f"格式错误!正确格式: 解封 <玩家名> [只在本群有效]")

            user = User.get_user_by_name(event.group_openid, msg[1])
            if user is None:
                await del_blacklist.finish(f'\n『Ban』\n' +
                                           f"没有找到名为[{(msg[1])}]的玩家!")

            if user.open_id in group.admins:
                group.black_list.remove(user.open_id)
                group.update()
                await del_blacklist.finish(f'\n『Ban』\n' +
                                           f"[{msg[1]}]已被本群解封!")

            else:
                await del_blacklist.finish(f'\n『Ban』\n' +
                                           "该玩家没有被本群封禁!")
    else:
        await del_blacklist.finish(f'\n『Ban』\n' +
                                   "没有权限!\n"
                                   "只允许BOT管理员使用")
