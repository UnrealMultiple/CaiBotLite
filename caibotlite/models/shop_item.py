from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from caibotlite.enums.shop_item_type import ShopItemType
from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group import Group
    from .shop_list import ShopList


class ShopItem(Base):
    __tablename__ = "shop_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(20))
    type: Mapped["ShopItemType"] = mapped_column(String(10))
    item_id: Mapped[int] = mapped_column()
    item_stack: Mapped[int] = mapped_column()
    item_prefix: Mapped[int] = mapped_column()
    command: Mapped[str] = mapped_column(String(50))
    list_id: Mapped[int] = mapped_column(ForeignKey("shop_list.id"))
    list: Mapped["ShopList"] = relationship(back_populates="items", lazy='joined')
    group_open_id: Mapped[str] = mapped_column(ForeignKey("group.open_id"))
    group: Mapped["Group"] = relationship(back_populates="shop_items", lazy='joined')
