from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group import Group
    from .shop_item import ShopItem


class ShopList(Base):
    __tablename__ = "shop_list"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20))
    items: Mapped["ShopItem"] = relationship(back_populates="list")
    group_open_id: Mapped[str] = mapped_column(ForeignKey("group.open_id"))
    group: Mapped["Group"] = relationship(back_populates="shop_lists", lazy='joined')
