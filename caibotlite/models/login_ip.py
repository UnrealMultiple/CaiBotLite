from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .user import User


class LoginIP(Base):
    __tablename__ = "login_ip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String(32))
    city: Mapped[str] = mapped_column(String(32), nullable=True)
    record_time: Mapped[datetime] = mapped_column()
    user_open_id: Mapped[str] = mapped_column(ForeignKey("user.open_id"))
    user: Mapped["User"] = relationship(back_populates="ips", lazy='joined')
