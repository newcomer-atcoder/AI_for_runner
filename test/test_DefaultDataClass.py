# -*- coding: utf-8 -*-

from src.my_modules.data import DefaultData
from src.my_modules import data
from sqlalchemy import create_engine, select, Integer, Float, Date, CheckConstraint as check
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import datetime
from pathlib import Path
import torch

#テスト環境作成
DIST_MIN_VALUE = 0 #0km
CONDITION_MIN_VALUE = 0 #0%
CONDITION_MAX_VALUE = 100 #100%
DB_PATH = Path(__file__).parent/"test5.db"
TEST_DATA_DISTANCE_CONDITIONS = [
    [5.0, 50.0],
    [11.0, 60.0]
]
TEST_DATA_RUNNINGDISTS = [
    [5.0],
    [7.0]
]


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

def setUpTestEnv(engine):
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        registor = []
        for [distance, condition], [runningDist] in zip(TEST_DATA_DISTANCE_CONDITIONS, TEST_DATA_RUNNINGDISTS):
            registor += [MocRunDist(distance=distance, condition=condition, runningDist=runningDist)]
        session.add_all(registor)
        session.commit()


#ここからテストコード
#1.load_TrainingDataメソッド
def test_load_TrainingData(monkeypatch):
    engine = create_engine(
        url=f"sqlite:///{DB_PATH}",
        echo=True
    )
    if not DB_PATH.exists():
        setUpTestEnv(engine)
    
    #期待値
    exp_distance_conditions = torch.tensor(TEST_DATA_DISTANCE_CONDITIONS, dtype=torch.float32)
    exp_runningDists = torch.tensor(TEST_DATA_RUNNINGDISTS, dtype=torch.float32)

    #結果
    testData = DefaultData()
    testData.load_TrainingData(engine, MocRunDist)
    
    for exps, results in zip(exp_distance_conditions, testData.distance_conditions_Tensor):
        for i, exp in enumerate(exps):
            assert exp == results[i]
    
    for exps, results in zip(exp_runningDists, testData.runningDists_Tensor):
        for i, exp in enumerate(exps):
            assert exp == results[i]

    