from caibotlite.constants import API_URL


def at_user_tag(user_open_id: str) -> str:
    return f'<qqbot-at-user id="{user_open_id}" />'


def cmd_input_tag(text: str, show: str | None = None, reference: bool = False) -> str:
    if show is None:
        show = text
    return f'<qqbot-cmd-input text="{text}" show="{show}" reference="{str(reference).lower()}" />'


def cmd_enter_tag(text: str) -> str:
    return f'<qqbot-cmd-enter text="{text}" />'

def copy_link_tag(text: str) -> str:
    return f'[{text}]({API_URL}/copy?content={text})'
