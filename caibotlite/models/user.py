from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group import Group
    from .login_ip import LoginIP
    from .login_uuid import LoginUUID


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    group_open_id: Mapped[str] = mapped_column(ForeignKey("group.open_id"), index=True)
    group: Mapped["Group"] = relationship(back_populates="users", lazy='joined')
    open_id: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    money: Mapped[int] = mapped_column(default=0)
    sign_days: Mapped[int] = mapped_column(default=0)
    sign_consistency: Mapped[int] = mapped_column(default=0)
    uuids: Mapped[List["LoginUUID"]] = relationship(back_populates="user", lazy='joined', cascade="all, delete-orphan")
    uuid_list: Mapped[List[str]] = association_proxy("uuids", "uuid")
    ips: Mapped[List["LoginIP"]] = relationship(back_populates="user", lazy='joined', cascade="all, delete-orphan")
    ip_list: Mapped[List[str]] = association_proxy("ips", "ip")
    city_list: Mapped[List[str]] = association_proxy("ips", "city")
    last_login: Mapped[datetime] = mapped_column(default=datetime.min)
    last_sign: Mapped[datetime] = mapped_column(default=datetime.min)
    last_rename: Mapped[datetime] = mapped_column(default=datetime.min)
