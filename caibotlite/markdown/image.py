from typing import Iterable

from caibotlite.constants import BOT_APPID, API_URL
from caibotlite.database import async_session
from caibotlite.managers import UserManager


async def get_user_avatar(group_openid: str, user_name: str, size: int = 20) -> str:
    async with async_session() as session:
        user = await UserManager.get_user_by_name(session=session, group_open_id=group_openid, name=user_name)
    return  user_avatar(user.open_id, size) if user else ""

def user_avatar(user_openid: str, size: int = 20) -> str:
   return f"![text #{size}px #{size}px](https://thirdqq.qlogo.cn/qqapp/{BOT_APPID}/{user_openid}/1)"


async def get_users_avatar(group_openid: str, user_names: Iterable[str], size: int = 20) -> dict[str, str]:
    async with async_session() as session:
        users = await UserManager.get_users_by_names(session=session, group_open_id=group_openid, names=user_names)

    return {
        user_name: f"![text #{size}px #{size}px](https://thirdqq.qlogo.cn/qqapp/{BOT_APPID}/{user.open_id}/1)"
        for user_name, user in users.items()
    }

def get_image(url: str, size: int = 20) -> str:
    return f"![text #{size}px #{size}px]({url})"


def get_terraria_image(category: str, item_id: int) -> str:
    """Return a markdown inline image tag for a terraria resource (item/npc/projectile/buff)."""
    url = f"{API_URL.rstrip('/')}/image/{category}/{item_id}"
    return f"![text]({url})"

