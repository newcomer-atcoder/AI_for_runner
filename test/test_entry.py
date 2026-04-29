from sqlalchemy import create_engine, select, Integer, Float, Date, CheckConstraint as check, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from pathlib import Path

from src.my_modules.data.entry import EntryRunData, ValueCheck, SaveRunSchedule

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

    #dbデータを削除したうえで確認
    with Session(engine) as session:
        stmt = delete(MocRunDist)
        session.execute(stmt)
        session.commit()

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

def test_isNodata():
    test_entry = EntryRunData()
    engine = create_engine(
        f'sqlite:///{DB_PATH}',
        echo=True
    )

    #test1.DBの登録データが1件以上
    #test_insert_into_db実行後のデータを想定
    result1 = test_entry.isNodata(engine, MocRunDist)
    assert not result1 #False想定

    #test2.DBの登録データが0件

    #dbデータを一時的に削除したうえで確認
    with Session(engine) as session:
        stmt = delete(MocRunDist)
        session.execute(stmt)
        session.commit()

    result2 = test_entry.isNodata(engine, MocRunDist)
    assert result2 #True想定

#2026/4/29追加
#SaveRunScheduleクラスのテスト
def test_insert_into_db_save(monkeypatch):
    engine = create_engine(
        url=f"sqlite:///{DB_PATH}",
        echo=True
    )
    if not DB_PATH.exists():
        Base.metadata.create_all(engine)
    
    testInsert = SaveRunSchedule()

    #期待値
    exp_values = [
        ValueCheck(yyyy=2026, mm=4, dd=29, distance=1.0, condition=70.0, runningDist=1.0)
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

def test_getSchedule():
    test_schedule = SaveRunSchedule()
    engine = create_engine(
        f'sqlite:///{DB_PATH}',
        echo=True
    )

    #test1.DBの登録データが1件以上
    #test_insert_into_db_save実行後のデータを想定
    exp_values = [
        ValueCheck(yyyy=2026, mm=4, dd=29, distance=1.0, condition=70.0, runningDist=1.0)
    ]
    #期待値
    result1 = test_schedule.getSchedule(engine, MocRunDist)
    assert type(result1) == dict #何かしらの辞書を取得

    #test2.DBの登録データが0件

    #dbデータを一時的に削除したうえで確認
    with Session(engine) as session:
        stmt = delete(MocRunDist)
        session.execute(stmt)
        session.commit()

    result2 = test_schedule.getSchedule(engine, MocRunDist)
    assert result2 is None #データなし