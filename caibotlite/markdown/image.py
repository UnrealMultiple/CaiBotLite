from caibotlite.constants import BOT_APPID
from caibotlite.database import async_session
from caibotlite.managers import UserManager


async def get_user_avatar(group_openid: str, user_name: str, size: int = 20) -> str:
    user = await UserManager.get_user_by_name(session=async_session(), group_open_id=group_openid, name=user_name)
    return f"![text #{size}px #{size}px](https://thirdqq.qlogo.cn/qqapp/{BOT_APPID}/{user.open_id}/1)"

def get_image(url: str, size: int = 20) -> str:
    return f"![text #{size}px #{size}px]({url})"
