from src.my_modules.db import dbmodels
from src.my_modules.db.dbmodels import Base, RunDist
from sqlalchemy import create_engine, inspect, delete, select
from sqlalchemy.orm import Session
from pathlib import Path

import datetime
from sqlalchemy.exc import DataError, IntegrityError, StatementError

def test_dbColumns(monkeypatch):
    #まずはrundistテーブルを生成しておく
    DB_DIR = Path(__file__).parent/"test4.db"
    engine = create_engine(
        url=f"sqlite:///{DB_DIR}",
        echo=True
    )

    tables = inspect(engine).get_table_names()
    if not tables:
        Base.metadata.create_all(engine)
    
    #DBへの登録値：「日付」「走行予定の距離(km)」「体調(%)」「実走距離(%)」
    #「id (primary_key)」は自動採番のため考慮しない

    #1.正常データの準備
    #※日付は文字列からキャストしてくれないことが判明
    safe_datas = [
        [datetime.date(2026, 3, 17), 0.0, 0.0, 0.0], #「走行予定の距離(km)」「体調(%)」「実走距離(%)」の境界値(下限)
        [None, "10.0", 100, 10.0], #「体調(%)」の境界値(上限) + 入力値キャストの確認
    ]

    #2.異常データと登録結果の準備
    error_datas = [
        [datetime.date(2026, 3, 17), -1.0, 0.0, 0.0], #境界範囲外の値
        [datetime.date(2026, 3, 17), 0.0, -1.0, 0.0],
        [datetime.date(2026, 3, 17), 0.0, 0.0, -1.0],
        [datetime.date(2026, 3, 17), 0.0, 101.0, 0.0],
        [5, 0.0, 0.0, 0.0], #型エラー
        [datetime.date(2026, 3, 17), "hoge", 0.0, 0.0],
        [datetime.date(2026, 3, 17), 0.0, "hoge", 0.0],
        [datetime.date(2026, 3, 17), 0.0, 0.0, "hoge"],
        [datetime.date(2026, 3, 17), None, 0.0, 0.0], #Null違反
        [datetime.date(2026, 3, 17), 0.0, None, 0.0],
        [datetime.date(2026, 3, 17), 0.0, 0.0, None],
    ]
    INTEGRITY_ERROR = 1 #境界範囲外の値、その他制約エラー
    DATA_ERROR = 2
    STMT_ERROR = 3 #キャスト不可能な値
    exp_results = [INTEGRITY_ERROR] * 4 + [STMT_ERROR] * 4 + [INTEGRITY_ERROR] * 3
    results = [0] * 11

    with Session(engine) as session:
        del_items = delete(RunDist)
        session.execute(del_items)
        session.commit()

        #1.正常データを登録
        #flushでエラーなしであれば検証OKとする
        registDatas = []
        for date, distance, condition, runningDist in safe_datas:
            registDatas += [RunDist(date=date, distance=distance, condition=condition, runningDist=runningDist)]
        session.add_all(registDatas)
        session.flush()

        #2.異常データを登録
        #N+1問題(データ件数分のflush)があるが無視する
        for test_index, error_data in enumerate(error_datas):
            [date, distance, condition, runningDist] = error_data
            registData = RunDist(date=date, distance=distance, condition=condition, runningDist=runningDist)
            
            try:
                session.add(registData)
                session.flush()
            
            except IntegrityError:
                results[test_index] = INTEGRITY_ERROR
            except DataError:
                results[test_index] = DATA_ERROR
            except StatementError:
                results[test_index] = STMT_ERROR
            session.rollback()
        print(*results)
        assert exp_results == results
        
