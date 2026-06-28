from nonebot.adapters.qq import MessageSegment
from nonebot.adapters.qq.models import (
    MessageKeyboard,
    InlineKeyboard,
    InlineKeyboardRow,
    Button,
    RenderData,
    Action,
    Permission,
)

from caibotlite.constants import BOT_QQ, BOT_UID
from caibotlite.utils import text

help_doc_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="😘 帮助文档",
                                visited_label="😘 帮助文档",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data="https://docs.terraria.ink/zh/other/CaiBotLite.html",
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)

bot_admin_group_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="🙏 加入反馈群",
                                visited_label="🙏 加入反馈群",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data="https://qm.qq.com/q/K4icZbgwWy",
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)

help_list_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="#️⃣ 群管理", visited_label="#️⃣ 群管理", style=1
                            ),
                            action=Action(
                                type=2,
                                data="/群管理",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="📄 白名单", visited_label="📄 白名单", style=1
                            ),
                            action=Action(
                                type=2,
                                data="/白名单菜单",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="⚡ 快捷功能",
                                visited_label="⚡ 快捷功能",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/快捷功能菜单",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="🗺️ 地图功能",
                                visited_label="🗺️ 地图功能",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/地图功能菜单",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="🔍 图鉴搜索",
                                visited_label="🔍 图鉴搜索",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/图鉴搜索菜单",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="💾 服务器管理",
                                visited_label="💾 服务器管理",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/服务器管理",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="🔒 主动权限",
                                visited_label="🔒 主动权限",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/主动权限",
                                permission=Permission(type=1),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="😘 帮助文档",
                                visited_label="😘 帮助文档",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data="https://docs.terraria.ink/zh/other/CaiBotLite.html",
                                permission=Permission(
                                    type=2, specify_role_ids=["1", "2", "3"]
                                ),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="🙏 加入反馈群",
                                visited_label="🙏 加入反馈群",
                                style=1,
                            ),
                            action=Action(
                                type=0,
                                data="https://qm.qq.com/q/K4icZbgwWy",
                                permission=Permission(type=2),
                            ),
                        ),
                    ]
                ),
            ]
        )
    )
)


def reedit_keyboard(cmd: str) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="📝 重新编辑",
                                    visited_label="📝 重新编辑",
                                    style=1,
                                ),
                                action=Action(
                                    type=2, data=cmd, permission=Permission(type=2)
                                ),
                            )
                        ]
                    )
                ]
            )
        )
    )


def download_keyboard(url: str) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="💾 下载", visited_label="💾 下载", style=1
                                ),
                                action=Action(
                                    type=0, data=url, permission=Permission(type=2)
                                ),
                            )
                        ]
                    )
                ]
            )
        )
    )


def rank_page_keyboard(
    server_index: str, rank_type: str, arg: str | None, page: int
) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="⬅️ 上一页",
                                    visited_label="⬅️ 上一页",
                                    style=1,
                                ),
                                action=Action(
                                    type=2,
                                    data=f"/排行 {server_index} {rank_type} {arg if arg else ''} {page - 1}",
                                    permission=Permission(type=2),
                                ),
                            ),
                            Button(
                                render_data=RenderData(
                                    label="下一页 ➡️",
                                    visited_label="下一页 ➡️",
                                    style=1,
                                ),
                                action=Action(
                                    type=2,
                                    data=f"/排行 {server_index} {rank_type} {arg if arg else ''} {page + 1}",
                                    permission=Permission(type=2),
                                ),
                            ),
                        ]
                    )
                ]
            )
        )
    )


whitelist_success_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="💾 服务器列表",
                                visited_label="💾 服务器列表",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/服务器列表",
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)

whitelist_bound_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="✏️ 修改白名单",
                                visited_label="✏️ 修改白名单",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/修改白名单",
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)

add_whitelist_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="📄 添加白名单",
                                visited_label="📄 添加白名单",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/添加白名单",
                                permission=Permission(type=2),
                            ),
                        )
                    ]
                )
            ]
        )
    )
)

member_add_keyboard = MessageSegment.keyboard(
    MessageKeyboard(
        content=InlineKeyboard(
            rows=[
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="📄 菜单",
                                visited_label="📄 菜单",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/帮助",
                                permission=Permission(type=2),
                            ),
                        ),
                        Button(
                            render_data=RenderData(
                                label="ℹ️ 关于",
                                visited_label="ℹ️ 关于",
                                style=1,
                            ),
                            action=Action(
                                type=2,
                                data="/关于",
                                permission=Permission(type=2),
                            ),
                        ),
                    ]
                )
            ]
        )
    )
)


def permission_request_keyboard(group_id: str) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="🔒 权限请求",
                                    visited_label="🔒 权限请求",
                                    style=1,
                                ),
                                action=Action(
                                    type=0,
                                    data="https://club.vip.qq.com/transfer?open_kuikly_info="
                                    "{"
                                    f'"page_name": "ai_group_service_agreement_pop_page",'
                                    f'"groupCode":{group_id},"botUin":{BOT_QQ},'
                                    f'"botUid":"{BOT_UID}","screen":1'
                                    "}",
                                    permission=Permission(type=1),
                                ),
                            )
                        ]
                    )
                ]
            )
        )
    )


def login_request_keyboard(
    user_openid: str,
) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="✅ 批准",
                                    visited_label="✅ 批准",
                                    style=1,
                                ),
                                action=Action(
                                    type=2,
                                    data="/登录",
                                    permission=Permission(
                                        type=0,
                                        specify_user_ids=[user_openid],
                                    ),
                                ),
                            ),
                            Button(
                                render_data=RenderData(
                                    label="❌ 拒绝",
                                    visited_label="❌ 拒绝",
                                    style=1,
                                ),
                                action=Action(
                                    type=2,
                                    data="/拒绝",
                                    permission=Permission(
                                        type=0,
                                        specify_user_ids=[user_openid],
                                    ),
                                ),
                            ),
                        ]
                    )
                ]
            )
        )
    )
