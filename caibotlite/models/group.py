from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ARRAY, String
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    # unique=True 会生成内联 UNIQUE 约束(自带索引), 供本表自引用外键使用;
    # 不能加 index=True, 否则会变成建表后才创建的唯一索引, PG 上自引用外键会建表失败
    open_id: Mapped[str] = mapped_column(String(32), unique=True)
    # PG 原生数组; 元素不限长, 避免历史脏数据超长导致迁移/写入失败
    admins: Mapped[List["str"]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)), default=[]
    )
    black_list: Mapped[List["str"]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)), default=[]
    )
    config: Mapped["GroupConfig"] = relationship(
        back_populates="group",
        lazy="joined",
        uselist=False,
        cascade="all, delete-orphan",
    )
    servers: Mapped[List["Server"]] = relationship(
        back_populates="group", lazy="joined"
    )
    users: Mapped[List["User"]] = relationship(back_populates="group", lazy="raise")
    shop_items: Mapped[List["ShopItem"]] = relationship(
        back_populates="group", lazy="raise"
    )
    shop_lists: Mapped[List["ShopList"]] = relationship(
        back_populates="group", lazy="raise"
    )

    parent_open_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("group.open_id"), nullable=True
    )
    parent_group: Mapped[Optional["Group"]] = relationship(
        "Group",
        foreign_keys=[parent_open_id],
        remote_side=[open_id],
        back_populates="child_groups",
        lazy="joined",
    )

    child_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="parent_group",
        remote_side=[parent_open_id],
        lazy="raise",
    )
