from sqlalchemy import create_engine, select, Integer, Float, Date, CheckConstraint as check, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from src.my_modules.data.entry import EntryRunData, ValueCheck, SaveRunSchedule

import datetime

#insert_into_db
#環境構築
DIST_MIN_VALUE = 0
CONDITION_MIN_VALUE = 0
CONDITION_MAX_VALUE = 100

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
def test_insert_into_db(tmp_db_path):
    engine = create_engine(
        url=f"sqlite:///{tmp_db_path}",
        echo=True
    )
    Base.metadata.create_all(engine) # 毎回まっさらなので無条件に作成

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

def test_isNodata(tmp_db_path):
    engine = create_engine(f"sqlite:///{tmp_db_path}", echo=True)
    Base.metadata.create_all(engine) # 毎回まっさらなので無条件に作成
    entry = EntryRunData()

    #test1: データを1件入れてから判定 → False 期待（前テストの残存データに依存しない）
    entry.checkedValueList = [ValueCheck(yyyy=2026, mm=3, dd=18,
                                         distance=5.0, condition=70.0, runningDist=6.0)]
    entry.insert_into_db(engine, MocRunDist)
    assert not entry.isNodata(engine, MocRunDist) #False想定

    #test2: 全削除してから判定 → True 期待
    with Session(engine) as session:
        session.execute(delete(MocRunDist))
        session.commit()
    assert entry.isNodata(engine, MocRunDist) #True想定

#2026/4/29追加
#SaveRunScheduleクラスのテスト
def test_insert_into_db_save(tmp_db_path):
    engine = create_engine(
        url=f"sqlite:///{tmp_db_path}",
        echo=True
    )
    Base.metadata.create_all(engine) # 毎回まっさらなので無条件に作成

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

def test_getSchedule(tmp_db_path):
    engine = create_engine(f"sqlite:///{tmp_db_path}", echo=True)
    Base.metadata.create_all(engine) # 毎回まっさらなので無条件に作成
    test_schedule = SaveRunSchedule()

    #test1: 1件登録してから取得 → dict 期待（前テストの残存データに依存しない）
    test_schedule.checkedValueList = [
        ValueCheck(yyyy=2026, mm=4, dd=29, distance=1.0, condition=70.0, runningDist=1.0)
    ]
    test_schedule.insert_into_db(engine, MocRunDist)
    result1 = test_schedule.getSchedule(engine, MocRunDist)
    assert type(result1) == dict #何かしらの辞書を取得

    #test2: 全削除してから取得 → None 期待
    with Session(engine) as session:
        session.execute(delete(MocRunDist))
        session.commit()
    result2 = test_schedule.getSchedule(engine, MocRunDist)
    assert result2 is None #データなし

#2026/6/21追加
#EntryRunData.addRecord / updateRecord / deleteRecord のテスト

#共通ヘルパー
def _make_engine(tmp_db_path):
    return create_engine(f"sqlite:///{tmp_db_path}", echo=True)

def _clear(engine):
    #テーブルを空にする(テスト間の独立性確保)
    with Session(engine) as session:
        session.execute(delete(MocRunDist))
        session.commit()

def _fetch_all(engine):
    with Session(engine) as session:
        return session.scalars(select(MocRunDist)).all()

def test_addRecord(tmp_db_path):
    engine = _make_engine(tmp_db_path)
    Base.metadata.create_all(engine)
    _clear(engine)

    entry = EntryRunData()

    #1件目を追加
    rec1 = ValueCheck(yyyy=2026, mm=6, dd=21, distance=8.0, condition=65.0, runningDist=7.5)
    entry.addRecord(rec1, engine, MocRunDist)

    rows = _fetch_all(engine)
    assert len(rows) == 1                      #ちょうど1件
    assert rows[0].date == datetime.date(2026, 6, 21)
    assert rows[0].distance == 8.0
    assert rows[0].condition == 65.0
    assert rows[0].runningDist == 7.5

    #2件目を追加 → バッファを使わないので"重複せず"2件になる
    rec2 = ValueCheck(yyyy=2026, mm=6, dd=22, distance=10.0, condition=80.0, runningDist=9.0)
    entry.addRecord(rec2, engine, MocRunDist)

    rows = _fetch_all(engine)
    assert len(rows) == 2                      #1件目が重複していない=合計2件
    dists = sorted(r.distance for r in rows)
    assert dists == [8.0, 10.0]

def test_updateRecord(tmp_db_path):
    engine = _make_engine(tmp_db_path)
    Base.metadata.create_all(engine)
    _clear(engine)

    entry = EntryRunData()

    #更新対象を1件用意し、自動採番された id を取得
    before = ValueCheck(yyyy=2026, mm=1, dd=10, distance=5.0, condition=50.0, runningDist=4.0)
    entry.addRecord(before, engine, MocRunDist)
    target_id = _fetch_all(engine)[0].id       #idは固定値を仮定せずDBから取得

    #更新を実行
    after = ValueCheck(yyyy=2026, mm=12, dd=31, distance=20.0, condition=90.0, runningDist=18.0)
    entry.updateRecord(target_id, after, engine, MocRunDist)

    rows = _fetch_all(engine)
    assert len(rows) == 1                       #件数は増減しない
    updated = rows[0]
    assert updated.id == target_id              #同じ行が更新された
    assert updated.date == datetime.date(2026, 12, 31)
    assert updated.distance == 20.0
    assert updated.condition == 90.0
    assert updated.runningDist == 18.0

def test_deleteRecord(tmp_db_path):
    engine = _make_engine(tmp_db_path)
    Base.metadata.create_all(engine)
    _clear(engine)

    entry = EntryRunData()

    #2件用意する
    entry.addRecord(ValueCheck(yyyy=2026, mm=2, dd=1, distance=3.0, condition=40.0, runningDist=3.0),
                    engine, MocRunDist)
    entry.addRecord(ValueCheck(yyyy=2026, mm=3, dd=1, distance=6.0, condition=60.0, runningDist=6.0),
                    engine, MocRunDist)

    rows = _fetch_all(engine)
    assert len(rows) == 2
    delete_id = rows[0].id                      #消す対象
    keep_id   = rows[1].id                      #残る対象

    #削除を実行
    entry.deleteRecord(delete_id, engine, MocRunDist)

    rows_after = _fetch_all(engine)
    remaining_ids = [r.id for r in rows_after]
    assert delete_id not in remaining_ids       #対象は消えた
    assert remaining_ids == [keep_id]           #もう一方は残っている
