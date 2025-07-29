from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.sqltypes import JSON

from caibotlite.models import Base


class StatisticData(Base):
    __tablename__ = "statistic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(JSON)