from nonebot.adapters.qq import GroupAddRobotEvent
from nonebot import on_notice

from caibotlite.commands.server_commands import help_doc_keyboard
from caibotlite.dependencies import Session
from caibotlite.managers import GroupManager
from caibotlite.markdown.keyboard import MessageSegment
from caibotlite.markdown.tag import cmd_input_tag, at_user_tag
from caibotlite.markdown.image import user_avatar

init = on_notice()


@init.handle()
async def _(event: GroupAddRobotEvent, session: Session):
    group = await GroupManager.get_group_by_open_id(session, event.group_openid)
    if group is None:
        await GroupManager.create_group(
            session, event.group_openid, event.op_member_openid
        )

    else:
        group.admins = [event.op_member_openid]
        group.parent_open_id = None
        await GroupManager.update_group(session, group)

    await init.finish(
        MessageSegment.markdown(
            "## 🍥 欢迎使用 CaiBotLite\n"
            f"> 默认管理已设为{user_avatar(event.op_member_openid)} {at_user_tag(event.op_member_openid)}\n"
            f'- 使用"{cmd_input_tag("/添加白名单")} `<名字>`"注册账户\n'
            f'- 使用"{cmd_input_tag("/添加管理员")} `<名字>`"添加新管理\n'
        )
        + help_doc_keyboard
    )
