from nonebot.adapters.qq import MessageSegment
from nonebot.adapters.qq.models import MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, \
    Permission

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
