from typing import TYPE_CHECKING

from sqlalchemy import *
from sqlalchemy.orm import *

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group import Group


class GroupConfig(Base):
    __tablename__ = "group_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    group_open_id: Mapped[int] = mapped_column(ForeignKey("group.open_id"))
    group: Mapped["Group"] = relationship(back_populates="config", lazy="joined")
    allow_default_getmapimage: Mapped[bool] = mapped_column(default=False)
    allow_default_getmapfile: Mapped[bool] = mapped_column(default=False)
    allow_default_getworldfile: Mapped[bool] = mapped_column(default=False)
    show_ip_location: Mapped[bool] = mapped_column(default=False)
    allow_admin_addadmin: Mapped[bool] = mapped_column(default=True)
    disabled_whitelist_cooldown: Mapped[bool] = mapped_column(default=False)
    disabled_show_playerlist: Mapped[bool] = mapped_column(default=False)
    # 金额相关字段可被设为超过 int32 的值, 统一用 64 位整数
    max_sign_coins: Mapped[int] = mapped_column(BigInteger, default=1000)
    min_sign_coins: Mapped[int] = mapped_column(BigInteger, default=0)
    constant_sign_reward: Mapped[int] = mapped_column(BigInteger, default=10)
