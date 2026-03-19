from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, Date, CheckConstraint as check
import datetime

#定数(validation check)
DIST_MIN_VALUE = 0 #0km
CONDITION_MIN_VALUE = 0 #0%
CONDITION_MAX_VALUE = 100 #100%

class Base(DeclarativeBase):
    pass

#「id (primary_key)」「日付」「走行予定の距離(km)」「体調(%)」「実走距離(%)」
class RunDist(Base):
    __tablename__ = "runDist"

    #カラム定義

    #自動採番
    id : Mapped[int] = mapped_column(
        Integer,
        check("id > 0"),
        primary_key=True
    )

    date : Mapped[datetime.date] = mapped_column(
        Date,
        nullable=True
    )

    distance : Mapped[float] = mapped_column(
        Float,
        check(f"distance >= {DIST_MIN_VALUE}"),
        nullable=False
    )

    condition : Mapped[int] = mapped_column(
        Float,
        check(f"{CONDITION_MIN_VALUE} <= condition AND condition <= {CONDITION_MAX_VALUE}"),
        nullable=False
    )

    runningDist : Mapped[float] = mapped_column(
        Float,
        check(f"runningDist >= {DIST_MIN_VALUE}"),
        nullable=False
    )