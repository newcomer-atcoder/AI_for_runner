# -*- coding: utf-8 -*-
# AIFacade の C0 補完テスト
# load_TrainingData → trainingDone → inference を一連で実行することで
# DefaultModel.trainingDone と DefaultData.getTensorDatas の漏れも同時に解消する。

import datetime
from sqlalchemy import create_engine, Integer, Float, Date, CheckConstraint as check
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from src.my_modules.ai.facade import AIFacade
from src.my_modules.ai import models

#テスト用 ORM モック（本番 RunDist を流用しない）
DIST_MIN_VALUE = 0
CONDITION_MIN_VALUE = 0
CONDITION_MAX_VALUE = 100

class Base(DeclarativeBase):
    pass

class MocRunDist(Base):
    __tablename__ = "runDist"

    id : Mapped[int] = mapped_column(
        Integer,
        check("id > 0"),
        primary_key=True
    )
    date : Mapped[datetime.date] = mapped_column(Date, nullable=True)
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


def _setup_db(engine):
    """テーブル作成＋学習用データを数件 INSERT する"""
    Base.metadata.create_all(engine)
    training_records = [
        MocRunDist(distance=5.0,  condition=70.0, runningDist=6.0),
        MocRunDist(distance=8.0,  condition=80.0, runningDist=7.5),
        MocRunDist(distance=10.0, condition=60.0, runningDist=9.0),
    ]
    with Session(engine) as session:
        session.add_all(training_records)
        session.commit()


def test_aifacade_pipeline(tmp_db_path, tmp_model_path, monkeypatch):
    # tmp_path 配下に一時 DB を用意（本番 src/app.db を汚さない）
    engine = create_engine(f"sqlite:///{tmp_db_path}", echo=True)
    _setup_db(engine)

    # tmp_path 配下に一時モデルを用意（本番 src/checkpoint.pt を汚さない）
    monkeypatch.setattr(models, 'MODEL_PATH', tmp_model_path)
    ai = AIFacade()

    # load_pt_model: DefaultModel.load_pt_model を経由 (この段階では.ptファイル未作成のためロード失敗する)
    assert ai.load_pt_model() == False

    # load_TrainingData: DefaultData.load_TrainingData を経由
    ai.load_TrainingData(engine, MocRunDist)

    # trainingDone: DefaultData.getTensorDatas → DefaultModel.trainingDone を経由
    # モデルの初期セットアップも行う
    ai.trainingDone()

    # inference: 正常値で推論結果が得られること（None でないこと）
    result = ai.inference(5.0, 70.0)
    assert result is not None

    # 異常値では None が返ること
    result_invalid = ai.inference(-1.0, 70.0)
    assert result_invalid is None

    # モデルへ追加指示する (2026/0921追加)
    assert ai.load_pt_model() == True
    ai.load_TrainingData(engine, MocRunDist, 1)
    ai.addTrain()

    # inference: 正常値で推論結果が得られること（None でないこと）
    result = ai.inference(5.0, 70.0)
    assert result is not None

    # 異常値では None が返ること
    result_invalid = ai.inference(-1.0, 70.0)
    assert result_invalid is None
