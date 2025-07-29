from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .base import Base
    from .user import User


class LoginUUID(Base):
    __tablename__ = "login_uuid"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    uuid: Mapped[str] = mapped_column(String(32), unique=True)
    record_time: Mapped[datetime] = mapped_column()
    user_open_id: Mapped[str] = mapped_column(ForeignKey("user.open_id"))
    user: Mapped["User"] = relationship(back_populates="uuids", lazy='joined')
