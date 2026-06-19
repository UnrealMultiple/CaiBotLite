from nonebot.adapters.qq import MessageSegment
from nonebot.adapters.qq.models import MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, \
    Permission

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
                                style=1
                            ),
                            action=Action(
                                type=0,
                                data="https://docs.terraria.ink/zh/other/CaiBotLite.html",
                                permission=Permission(type=2)
                            )
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
                                style=1
                            ),
                            action=Action(
                                type=0,
                                data="https://qm.qq.com/q/K4icZbgwWy",
                                permission=Permission(type=2)
                            )
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
                                label="#️⃣ 群管理",
                                visited_label="#️⃣ 群管理",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/群管理",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        ),
                        Button(
                            render_data=RenderData(
                                label="📄 白名单",
                                visited_label="📄 白名单",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/白名单菜单",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        )
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="⚡ 快捷功能",
                                visited_label="⚡ 快捷功能",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/快捷功能菜单",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        ),
                        Button(
                            render_data=RenderData(
                                label="🗺️ 地图功能",
                                visited_label="🗺️ 地图功能",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/地图功能菜单",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        ),
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="🔍 图鉴搜索",
                                visited_label="🔍 图鉴搜索",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/图鉴搜索菜单",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        ),
                        Button(
                            render_data=RenderData(
                                label="💾 服务器管理",
                                visited_label="💾 服务器管理",
                                style=1
                            ),
                            action=Action(
                                type=2,
                                data="/服务器管理",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        )
                    ]
                ),
                InlineKeyboardRow(
                    buttons=[
                        Button(
                            render_data=RenderData(
                                label="😘 帮助文档",
                                visited_label="😘 帮助文档",
                                style=1
                            ),
                            action=Action(
                                type=0,
                                data="https://docs.terraria.ink/zh/other/CaiBotLite.html",
                                permission=Permission(type=2, specify_role_ids=["1", "2", "3"])
                            )
                        ),
                        Button(
                            render_data=RenderData(
                                label="🙏 加入反馈群",
                                visited_label="🙏 加入反馈群",
                                style=1
                            ),
                            action=Action(
                                type=0,
                                data="https://qm.qq.com/q/K4icZbgwWy",
                                permission=Permission(type=2)
                            )
                        )
                    ]
                )
            ]
        )
    )
)


def cmd_keyboard(server_index: str, cmd: str) -> MessageSegment:
    return MessageSegment.keyboard(
        MessageKeyboard(
            content=InlineKeyboard(
                rows=[
                    InlineKeyboardRow(
                        buttons=[
                            Button(
                                render_data=RenderData(
                                    label="📄 重新编辑",
                                    visited_label="📄 重新编辑",
                                    style=1
                                ),
                                action=Action(
                                    type=2,
                                    data=f"/远程命令 {server_index} {cmd}",
                                    permission=Permission(type=2)
                                )
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
                                    label="💾 下载",
                                    visited_label="💾 下载",
                                    style=1
                                ),
                                action=Action(
                                    type=0,
                                    data=url,
                                    permission=Permission(type=2)
                                )
                            )
                        ]
                    )
                ]
            )
        )
    )
