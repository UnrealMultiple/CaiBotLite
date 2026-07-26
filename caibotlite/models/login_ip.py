from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .base import Base


class LoginIP(Base):
    __tablename__ = "login_ip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    # IPv6 最长 45 字符, 不限制长度
    ip: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(32), nullable=True)
    record_time: Mapped[datetime] = mapped_column()
    # user.open_id 在多个群中会重复, 不能作为 PG 外键引用目标, 故只建索引不建外键
    user_open_id: Mapped[str] = mapped_column(String(32), index=True)
