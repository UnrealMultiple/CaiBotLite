from nonebot.adapters.qq import GroupMemberAddEvent, MessageSegment
from nonebot import on_notice

from caibotlite.dependencies import Session
from caibotlite.managers import GroupManager
from caibotlite.markdown.tag import at_user_tag, cmd_input_tag
from caibotlite.markdown.keyboard import member_add_keyboard
from caibotlite.models import Server

welcome = on_notice()


@welcome.handle()
async def _(event: GroupMemberAddEvent, session: Session):
    group = await GroupManager.get_group_by_open_id(session, event.group_openid)
    if group is None:
        return

    await session.refresh(group, ["parent_group"])

    servers: list[Server] = []
    if group.parent_group is not None:
        servers = group.parent_group.servers
    else:
        servers = group.servers

    if len(servers) == 0:
        return

    await welcome.finish(
        MessageSegment.markdown(
            at_user_tag(event.member_openid) + f"\n## 🎉 Ciallo～(∠・ω< )⌒★\n"
            f"> 游玩服务器攻略\n"
            f"1. {cmd_input_tag('/添加白名单')} `<名字>`\n"
            f"2. {cmd_input_tag('/服务器列表')} (点击复制信息)\n"
            f"3. 连接服务器 (名字要和白名单一样)\n"
            f"4. {cmd_input_tag('/登录')}"
        )
        + member_add_keyboard
    )
