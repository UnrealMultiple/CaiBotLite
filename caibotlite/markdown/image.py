from typing import Iterable

from caibotlite.constants import BOT_APPID, API_URL
from caibotlite.database import async_session
from caibotlite.managers import UserManager


async def get_user_avatar(group_openid: str, user_name: str, size: int = 20) -> str:
    async with async_session() as session:
        user = await UserManager.get_user_by_name(
            session=session, group_open_id=group_openid, name=user_name
        )
    return user_avatar(user.open_id, size) if user else ""


def user_avatar(user_openid: str, size: int = 20) -> str:
    return f"![text #{size}px #{size}px](https://thirdqq.qlogo.cn/qqapp/{BOT_APPID}/{user_openid}/1)"


async def get_users_avatar(
    group_openid: str, user_names: Iterable[str], size: int = 20
) -> dict[str, str]:
    async with async_session() as session:
        users = await UserManager.get_users_by_names(
            session=session, group_open_id=group_openid, names=user_names
        )

    return {
        user_name: f"![text #{size}px #{size}px](https://thirdqq.qlogo.cn/qqapp/{BOT_APPID}/{user.open_id}/1)"
        for user_name, user in users.items()
    }


def get_image(url: str, size: int = 20) -> str:
    return f"![text #{size}px #{size}px]({url})"


_TERRARIA_CATEGORY_MAP = {
    "item": ("items", "Item_{}.png"),
    "npc": ("npcs", "NPC_{}.png"),
    "projectile": ("projectiles", "Projectile_{}.png"),
    "buff": ("buffs", "Buff_{}.png"),
}

# cache: (category, item_id) -> (w, h)
_TERRARIA_SIZE_CACHE: dict[tuple[str, int], tuple[int, int]] = {}


def _get_terraria_image_size(
    category: str, item_id: int, fallback: int = 32
) -> tuple[int, int]:
    key = (category, item_id)
    if key in _TERRARIA_SIZE_CACHE:
        return _TERRARIA_SIZE_CACHE[key]

    from pathlib import Path
    from PIL import Image

    folder, template = _TERRARIA_CATEGORY_MAP.get(category, ("", ""))
    w, h = fallback, fallback
    if folder:
        local_path = Path("assets/images") / folder / template.format(item_id)
        try:
            with Image.open(local_path) as img:
                w, h = img.size
        except Exception:
            pass

    _TERRARIA_SIZE_CACHE[key] = (w, h)
    return w, h


def get_terraria_image(category: str, item_id: int, fallback_size: int = 32) -> str:
    """Return a markdown inline image tag for a terraria resource (item/npc/projectile/buff).
    Reads actual image dimensions (cached after first read).
    """
    url = f"{API_URL.rstrip('/')}/image/{category}/{item_id}"
    w, h = _get_terraria_image_size(category, item_id, fallback_size)
    return f"![text #{w}px #{h}px]({url})"
