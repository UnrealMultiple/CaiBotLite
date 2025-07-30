from nonebot import on_command
from nonebot.adapters.qq import GroupAtMessageCreateEvent

from caibotlite.dependencies import CurrentGroup, Session
from caibotlite.managers import LoginManager, UserManager

login = on_command('登录', aliases={"批准", "允许", "登陆"}, force_whitespace=True, block=True)


@login.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None:
        await login.finish(f'\n『登录系统』\n' +
                           "你还没有添加白名单！\n"
                           f"发送\"/添加白名单 <名字>\"来添加白名单")

    if await LoginManager.accept_login_ok(session, user):
        await login.finish(f"\n『登录系统』\n"
                           f"✅已接受此登录请求！\n"
                           f"使用\"/清空设备\"解除所有绑定")

    await login.finish(f"\n『登录系统』\n"
                       f"❔登录请求不存在或已过期！")


reject_login = on_command('拒绝', aliases={"不批准", "不允许"}, force_whitespace=True, block=True)


@reject_login.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None:
        await reject_login.finish(f'\n『登录系统』\n' +
                                  "你还没有添加白名单！\n"
                                  f"发送\"/添加白名单 <名字>\"来添加白名单")

    if LoginManager.reject_login_ok(user):
        await reject_login.finish(f"\n『登录系统』\n"
                                  f"❌已拒绝此登录请求！")

    await login.finish(f"\n『登录系统』\n"
                       f"❔登录请求不存在或已过期！")


clean_device = on_command('清空设备', aliases={"清除绑定"}, force_whitespace=True, block=True)


@clean_device.handle()
async def _(event: GroupAtMessageCreateEvent, group: CurrentGroup, session: Session):
    user = await UserManager.get_user_by_open_id(session, group.open_id, event.author.union_openid)
    if user is None:
        await reject_login.finish(f'\n『登录系统』\n' +
                                  "你还没有添加白名单！\n"
                                  f"发送\"/添加白名单 <名字>\"来添加白名单")

    await LoginManager.clean_login_info(session, user)
    await clean_device.finish(f"\n『登录系统』\n"
                              f"🗑️你已清除所有绑定信息！")
