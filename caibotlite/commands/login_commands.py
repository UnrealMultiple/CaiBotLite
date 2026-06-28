from nonebot import on_command
from nonebot.adapters.qq import (
    GroupAtMessageCreateEvent,
    MessageSegment,
    GroupMessageCreateEvent,
)

from caibotlite.dependencies import CurrentGroup, Session
from caibotlite.managers import LoginManager, UserManager
from caibotlite.markdown.keyboard import add_whitelist_keyboard
from caibotlite.markdown.tag import cmd_input_tag, at_user_tag

login = on_command(
    "登录", aliases={"批准", "允许", "登陆"}, force_whitespace=True, block=True
)


@login.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    group: CurrentGroup,
    session: Session,
):
    user = await UserManager.get_user_by_open_id(
        session, group.open_id, event.author.union_openid
    )
    if user is None:
        await login.finish(
            MessageSegment.markdown(
                f"{at_user_tag(event.author.union_openid)}\n"
                + "## 🍥 登录\n"
                + "你还没有添加白名单！\n"
                + f'发送"{cmd_input_tag("/添加白名单")} `<名字>`"来添加白名单'
            )
            + add_whitelist_keyboard
        )

    if await LoginManager.accept_login_ok(session, user):
        await login.finish(
            MessageSegment.markdown(
                f"{at_user_tag(event.author.union_openid)}\n"
                + "## 🍥 登录\n"
                + "✅ 已接受此登录请求！\n"
                + f'发送"{cmd_input_tag("/清空设备")} `<名字>`"解除所有设备绑定'
            )
        )

    await login.finish(
        MessageSegment.markdown(
            f"{at_user_tag(event.author.union_openid)}\n"
            + "## 🍥 登录\n"
            + "❔登录请求**不存在**或**已过期**！\n"
            "> 尝试**重新进入服务器**获取新的登录请求"
        )
    )


reject_login = on_command(
    "拒绝", aliases={"不批准", "不允许"}, force_whitespace=True, block=True
)


@reject_login.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    group: CurrentGroup,
    session: Session,
):
    user = await UserManager.get_user_by_open_id(
        session, group.open_id, event.author.union_openid
    )
    if user is None:
        await reject_login.finish(
            MessageSegment.markdown(
                f"{at_user_tag(event.author.union_openid)}\n"
                + "## 🍥 登录\n"
                + "你还没有添加白名单！\n"
                + f'发送"{cmd_input_tag("/添加白名单")} `<名字>`"来添加白名单'
            )
            + add_whitelist_keyboard
        )

    if LoginManager.reject_login_ok(user):
        await reject_login.finish(
            MessageSegment.markdown(
                f"{at_user_tag(event.author.union_openid)}\n"
                + "## 🍥 登录\n"
                + "❌ 已拒绝此登录请求！"
            )
        )

    await reject_login.finish(
        MessageSegment.markdown(
            f"{at_user_tag(event.author.union_openid)}\n"
            + "## 🍥 登录\n"
            + "❔登录请求**不存在**或**已过期**！\n"
            "> 尝试**重新进入服务器**获取新的登录请求"
        )
    )


clean_device = on_command(
    "清空设备", aliases={"清除绑定"}, force_whitespace=True, block=True
)


@clean_device.handle()
async def _(
    event: GroupAtMessageCreateEvent | GroupMessageCreateEvent,
    group: CurrentGroup,
    session: Session,
):
    user = await UserManager.get_user_by_open_id(
        session, group.open_id, event.author.union_openid
    )
    if user is None:
        await clean_device.finish(
            MessageSegment.markdown(
                f"{at_user_tag(event.author.union_openid)}\n"
                + "## 🍥 登录\n"
                + "你还没有添加白名单！\n"
                + f'发送"{cmd_input_tag("/添加白名单")} `<名字>`"来添加白名单'
            )
            + add_whitelist_keyboard
        )

    await LoginManager.clean_login_info(session, user)
    await clean_device.finish(
        MessageSegment.markdown(
            f"{at_user_tag(event.author.union_openid)}\n"
            + "## 🍥 登录\n"
            + "🗑️ 已清除所有绑定设备！"
        )
    )
