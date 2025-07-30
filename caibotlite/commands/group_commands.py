from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from caibotlite.dependencies import Args, CurrentGroup, OriginalGroup, Session
from caibotlite.managers import GroupManager, UserManager

bind_parent_group = on_command("绑定父群", force_whitespace=True, block=True)


@bind_parent_group.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: OriginalGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       "没有权限!\n"
                                       "只允许BOT管理员使用")

    if len(args) == 0:
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       f"格式错误!\n"
                                       f"正确格式: 绑定父群 <父群ID> [只在本群有效]\n"
                                       f"TIPS: 使用\"/获取群信息\"获取群父群ID")
    if group.parent_open_id is not None:
        await session.refresh(group, ["parent_group"])
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       f"本群已绑定父群[{group.parent_group.id}]!\n"
                                       f"使用\"/解绑父群\"解除绑定")
    parent_group_id = int(args[0])
    if parent_group_id == group.id:
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       "StackOverFlow!\n"
                                       "父群不能是自己")

    parent_group = await GroupManager.get_group_by_id(session, parent_group_id)

    if parent_group is None:
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       f"没有找到ID为[{parent_group_id}]的群!")

    if not GroupManager.has_permission(parent_group, event.author.union_openid):
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       f"没有权限!\n"
                                       f"你必须是父群的管理员才能进行此操作")

    if parent_group.parent_open_id is not None:
        await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                       "我的附庸的附庸不是我附庸 :(\n"
                                       "父群不能是子群")

    group.parent_open_id = parent_group.open_id
    await GroupManager.update_group(session, group)
    await bind_parent_group.finish(f'\n『绑定父群』\n' +
                                   f"已将[{parent_group_id}]设为本群父群!\n"
                                   f"TIPS: 使用\"/解绑父群\"解除绑定")


unbind_parent_group = on_command("解绑父群", force_whitespace=True, block=True)


@unbind_parent_group.handle()
async def _(event: GroupAtMessageCreateEvent, group: OriginalGroup, session: Session):
    if GroupManager.has_permission(group, event.author.union_openid):
        if group.parent_open_id is None:
            await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                             f"本群没有已绑定的父群!\n"
                                             f"使用\"/绑定父群 <群ID>\"添加父群")

        group.parent_open_id = None
        await GroupManager.update_group(session, group)
        await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                         f"已解绑父群!")
    else:
        await unbind_parent_group.finish(f'\n『解绑父群』\n' +
                                         "没有权限!\n"
                                         "只允许BOT管理员使用\n"
                                         "TIPS: BOT添加者为默认管理员")


get_group_info = on_command("获取群信息", aliases={"获取群信息"}, force_whitespace=True, block=True)


@get_group_info.handle()
async def _(group: OriginalGroup, session: Session):
    await session.refresh(group, ["child_groups"])
    await session.refresh(group, ["parent_group"])
    child_group = group.child_groups
    admin_names = []
    black_names = []
    for i in group.admins:
        user = await UserManager.get_user_by_open_id(session, group.open_id, i)
        if user is None:
            admin_names.append(f"无白名单({i})")
        else:
            admin_names.append(user.name)
    for i in group.black_list:
        user = await UserManager.get_user_by_open_id(session, group.open_id, i)
        if user is None:
            black_names.append(f"无白名单({i})")
        else:
            black_names.append(user.name)
    await get_group_info.finish(f'\n『群信息』\n'
                                f'群ID: {group.id}\n'
                                f'群OpenID: {group.open_id}\n'
                                f'父群: {group.parent_group.id if group.parent_open_id else "无"}\n'
                                f'子群: {",".join([str(i.id) for i in child_group]) if len(child_group) != 0 else "无"}\n'
                                f'用户数: {await UserManager.count_group_users(session, group.open_id)}\n'
                                f'管理列表: {",".join(admin_names)}\n'
                                f'黑名单: {",".join(black_names) if len(black_names) != 0 else "无"}\n'
                                f'TIPS: 绑定父群时使用\"群ID\"'
                                )


list_admin = on_command("管理列表", force_whitespace=True, block=True)


@list_admin.handle()
async def _(group: CurrentGroup, session: Session):
    names = []
    for i in group.admins:
        user = await UserManager.get_user_by_open_id(
            session, group.open_id, i)
        if user is None:
            names.append(f"无白名单({i})")
        else:
            names.append(user.name)
    if len(names) == 0:
        await list_blacklist.finish(f'\n『BOT管理』\n' +
                                    f"本群居然没有管理?\n"
                                    f"请尝试移除并重新添加机器人")
    else:
        await list_admin.finish(f'\n『BOT管理』\n' +
                                f"\n".join(names))


add_admin = on_command("添加管理", aliases={"添加管理员"}, force_whitespace=True, block=True)


@add_admin.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await add_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "只允许BOT管理员使用\n"
                               "TIPS: BOT添加者为默认管理员")

    if event.author.union_openid != group.admins[0] and not group.config.allow_admin_addadmin:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "本群已设置仅允许第一管理员删除管理")

    if len(args) == 0:
        await add_admin.finish(f'\n『BOT管理』\n' +
                               f"格式错误!\n"
                               f"正确格式: 添加管理 <玩家名> [只在本群有效]\n"
                               f"TIPS: BOT添加者为默认管理员")

    taget_name = args[0]

    user = await UserManager.get_user_by_name(session, group.open_id, taget_name)
    if user is None:
        await add_admin.finish(f'\n『BOT管理』\n' +
                               f"没有找到名为[{taget_name}]的用户!\n"
                               f"*请确保对方已添加白名单")

    if user.open_id in group.admins:
        await add_admin.finish(f'\n『BOT管理』\n' +
                               "该用户已是本群BOT管理!")
    else:
        group.admins.append(user.open_id)
        await GroupManager.update_group(session, group)
        await add_admin.finish(f'\n『BOT管理』\n' +
                               f"已将[{taget_name}]设为本群BOT管理!")


del_admin = on_command("删除管理", aliases={"删除管理员"}, force_whitespace=True, block=True)


@del_admin.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await del_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "只允许BOT管理员使用")
    if event.author.union_openid != group.admins[0] and not group.config.allow_admin_addadmin:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "本群已设置仅允许第一管理员删除管理")

    if len(args) == 0:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               f"格式错误!\n"
                               f"正确格式: 删除管理 <玩家名> [只在本群有效]")

    taget_name = args[0]
    user = await UserManager.get_user_by_name(session, group.open_id, taget_name)
    if user is None:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               f"没有找到名为[{taget_name}]的用户!")

    if user.open_id in group.admins:
        if len(group.admins) == 1:
            await del_admin.finish(f'\n『BOT管理』\n' +
                                   "群内至少需要1名管理!")
        group.admins.remove(user.open_id)
        await GroupManager.update_group(session, group)
        await del_admin.finish(f'\n『BOT管理』\n' +
                               f"[{taget_name}]不再是本群BOT管理!")

    else:
        await del_admin.finish(f'\n『BOT管理』\n' +
                               "该用户不是本群BOT管理!")


list_blacklist = on_command("黑名单列表", force_whitespace=True, block=True)


@list_blacklist.handle()
async def _(group: CurrentGroup, session: Session):
    names = []
    for i in group.black_list:
        user = await UserManager.get_user_by_open_id(session, group.open_id, i)
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


add_blacklist = on_command("添加黑名单", force_whitespace=True, block=True)


@add_blacklist.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await add_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   "没有权限!\n"
                                   "只允许BOT管理员使用")
    if len(args) == 0:
        await add_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"格式错误!\n"
                                   f"正确格式: 添加黑名单 <玩家名> [只在本群有效]")

    taget_name = args[0]
    user = await UserManager.get_user_by_name(session, group.open_id, taget_name)
    if user is None:
        await add_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"没有找到名为[{taget_name}]的玩家!")

    if user.open_id in group.black_list:
        await add_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   "该玩家已在本群黑名单中!")
    else:
        group.black_list.append(user.open_id)
        await GroupManager.update_group(session, group)
        await add_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"已将[{taget_name}]加入本群黑名单!")


del_blacklist = on_command("删除黑名单", aliases={"解封"}, force_whitespace=True, block=True)


@del_blacklist.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await del_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   "没有权限!\n"
                                   "只允许BOT管理员使用")
    if len(args) != 1:
        await del_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"格式错误!\n"
                                   f"正确格式: 删除黑名单 <玩家名> [只在本群有效]")

    taget_name = args[0]
    user = await UserManager.get_user_by_name(session, group.open_id, taget_name)
    if user is None:
        await del_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"没有找到名为[{taget_name}]的玩家!")

    if user.open_id in group.black_list:
        group.black_list.remove(user.open_id)
        await GroupManager.update_group(session, group)
        await del_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   f"已将[{taget_name}]从本群黑名单中移除!")

    else:
        await del_blacklist.finish(f'\n『BOT黑名单』\n' +
                                   "该玩家没有不在本群黑名单中!")


settings = on_command("设置", force_whitespace=True, block=True)


@settings.handle()
async def _(event: GroupAtMessageCreateEvent, args: Args, group: CurrentGroup, session: Session):
    if not GroupManager.has_permission(group, event.author.union_openid):
        await settings.finish(f'\n『BOT设置』\n' +
                              "没有权限!\n"
                              "只允许BOT管理员使用")
    if len(args) != 2:
        await settings.finish(f'\n『BOT设置』\n' +
                              f"格式错误!\n" +
                              f"正确格式: 设置 <配置项> <值>\n" +
                              f"当前支持的设置项: \n" +
                              "\n".join(
                                  ["最大签到金币", "最小签到金币", "不显示在线玩家", "允许群员下载地图",
                                   "允许群员查看地图", "允许群员下载小地图", "允许非第一管理员添加管理员"]
                              ))

    key = args[0]
    value = args[1]

    match key:
        case "最大签到金币":
            if not value.isdigit():
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是数字")
            value = int(value)
            if value > 1000000000:
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"不可以大于1000000000")

            if value < group.config.min_sign_coins:
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"不可以小于最小值")

            group.config.max_sign_coins = value
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"最大签到金币已设置为: {group.config.max_sign_coins}")

        case "最小签到金币":
            if not value.isdigit():
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是数字")
            value = int(value)
            if value > 1000000000:
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"不可以大于1000000000")

            if value > group.config.max_sign_coins:
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"不可以大于最大值")

            group.config.min_sign_coins = value
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"最小签到金币已设置为: {group.config.min_sign_coins}")

        case "不显示在线玩家":
            if value.lower() not in ("true", "false"):
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是true/false")
            group.config.disabled_show_playerlist = value.lower() == "true"
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"不显示在线玩家已设置为: {group.config.disabled_show_playerlist}")

        case "允许群员下载地图":

            if value.lower() not in ("true", "false"):
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是true/false")
            group.config.allow_default_getworldfile = value.lower() == "true"
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"允许群员下载地图已设置为: {group.config.allow_default_getworldfile}")

        case "允许群员查看地图":
            if value.lower() not in ("true", "false"):
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是true/false")
            group.config.allow_default_getmapimage = value.lower() == "true"
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"允许群员查看地图已设置为: {group.config.allow_default_getmapimage}")

        case "允许群员下载小地图":
            if value.lower() not in ("true", "false"):
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是true/false")
            group.config.allow_default_getmapfile = value.lower() == "true"
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"允许群员下载小地图已设置为: {group.config.allow_default_getmapfile}")

        case "允许非第一管理员添加管理员":
            if event.author.union_openid != group.admins[0]:
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"没有权限!\n"
                                      f"只有第一管理员才能设置此配置")

            if value.lower() not in ("true", "false"):
                await settings.finish(f'\n『BOT设置』\n' +
                                      f"无效参数!\n"
                                      f"必须是true/false")
            group.config.allow_admin_addadmin = value.lower() == "true"
            await GroupManager.update_group(session, group)
            await settings.finish(f'\n『BOT设置』\n' +
                                  f"设置成功!\n"
                                  f"允许非第一管理员添加管理员已设置为: {group.config.allow_admin_addadmin}")
