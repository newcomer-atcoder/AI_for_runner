from sqlalchemy import create_engine, select, Integer, Float, Date, CheckConstraint as check
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from pathlib import Path

from src.my_modules.data.entry import EntryRunData, ValueCheck

import datetime

#insert_into_db
#環境構築
DIST_MIN_VALUE = 0
CONDITION_MIN_VALUE = 0
CONDITION_MAX_VALUE = 100
DB_PATH = Path(__file__).parent/"testDB"/"test6.db"

class Base(DeclarativeBase):
    pass

class MocRunDist(Base):
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

#ここからテストコード
def test_insert_into_db(monkeypatch):
    engine = create_engine(
        url=f"sqlite:///{DB_PATH}",
        echo=True
    )
    if not DB_PATH.exists():
        Base.metadata.create_all(engine)
    
    testInsert = EntryRunData()

    #期待値
    exp_values = [
        ValueCheck(yyyy=2026, mm=3, dd=18, distance=5.0, condition=70.0, runningDist=6.0),
        ValueCheck(yyyy=2026, mm=4, dd=30, distance=11.0, condition=70.0, runningDist=11.0)
    ]

    #結果
    #期待値通りの値を登録できるか
    testInsert.checkedValueList = exp_values
    testInsert.insert_into_db(engine, MocRunDist)
    
    with Session(engine) as session:
        stmt = select(MocRunDist)
        results = session.scalars(statement=stmt)
        for result, exp_value in zip(results, exp_values):
            assert result.date == datetime.date(exp_value.yyyy, exp_value.mm, exp_value.dd)
            assert result.distance == exp_value.distance
            assert result.condition == exp_value.condition
            assert result.runningDist == exp_value.runningDist

    