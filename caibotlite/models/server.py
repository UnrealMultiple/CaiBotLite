from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .group import Group


class Server(Base):
    __tablename__ = "server"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    group_open_id: Mapped[str] = mapped_column(ForeignKey("group.open_id"), index=True)
    group: Mapped["Group"] = relationship(back_populates="servers", lazy="joined")
    token: Mapped[str] = mapped_column(String(36), index=True)
    # 该列同时存 IP 和域名 (域名最长 253 字符), 不限制长度
    ip: Mapped[str] = mapped_column(Text)
    port: Mapped[int] = mapped_column()
