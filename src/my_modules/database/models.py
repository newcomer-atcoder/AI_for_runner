from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, Date, CheckConstraint as check
import datetime

#定数(validation check)
DIST_MIN_VALUE = 0 #0km
CONDITION_MIN_VALUE = 0 #0%
CONDITION_MAX_VALUE = 100 #100%

class Base(DeclarativeBase):
    pass

#共通のカラム定義
#「id (primary_key)」「日付」「走行予定の距離(km)」「体調(%)」「実際に走った距離(km)」
class Common:
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

#全てのランニング記録を保持
class RunDist(Base, Common):
    __tablename__ = "runDist"

#推論画面(=app_inference)の回答と入力値を、1行保存するためのテーブル
class RunSchedule(Base, Common):
    __tablename__ = "runSchedule"