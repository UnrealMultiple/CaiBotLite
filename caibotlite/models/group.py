from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group_conifg import GroupConfig
    from .server import Server
    from .shop_item import ShopItem
    from .shop_list import ShopList
    from .user import User


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    open_id: Mapped[str] = mapped_column(String(32), unique=True)
    admins: Mapped[List["str"]] = mapped_column(MutableList.as_mutable(JSON), default=[])
    black_list: Mapped[List["str"]] = mapped_column(MutableList.as_mutable(JSON), default=[])
    config: Mapped["GroupConfig"] = relationship(back_populates="group", lazy='joined', uselist=False,
                                                 cascade="all, delete-orphan")
    servers: Mapped[List["Server"]] = relationship(back_populates="group", lazy='joined')
    users: Mapped[List["User"]] = relationship(back_populates="group", lazy='raise')
    shop_items: Mapped[List["ShopItem"]] = relationship(back_populates="group", lazy='raise')
    shop_lists: Mapped[List["ShopList"]] = relationship(back_populates="group", lazy='raise')

    parent_open_id: Mapped[Optional[str]] = mapped_column(ForeignKey("group.open_id"), nullable=True)
    parent_group: Mapped[Optional["Group"]] = relationship(
        "Group",
        foreign_keys=[parent_open_id],
        remote_side=[open_id],
        back_populates="child_groups",
        lazy='joined'
    )

    child_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="parent_group",
        remote_side=[parent_open_id],
        lazy='raise'
    )
