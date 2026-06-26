# -*- coding: utf-8 -*-
# DBFacade の C0 補完テスト
# monkeypatch で setup.DB_PATH を tmp_path 配下に差し替えることで
# 本番 src/app.db を汚さずに全メソッドを実行する。

from src.my_modules.data.facade import DBFacade
from src.my_modules.database import setup
from src.my_modules.data.entry import ValueCheck


def test_dbfacade_all_methods(monkeypatch, tmp_path):
    # 本番 DB を汚さないよう DB_PATH を一時パスに差し替え
    tmp_db = tmp_path / "test.db"
    monkeypatch.setattr(setup, "DB_PATH", tmp_db)

    facade = DBFacade()

    # setUp_Done: 初回はテーブルなし → True（かつテーブルを作成する）
    assert facade.setUp_Done() == True
    # 2回目: テーブルあり → False
    assert facade.setUp_Done() == False

    # getDBAccessInfo: engine と RunDist クラスを取得できること
    engine, RunDist = facade.getDBAccessInfo()
    assert engine is not None
    assert RunDist is not None

    # add_runData → insert_into_db（EntryRunData.add_runData を経由する）
    rec = ValueCheck(yyyy=2026, mm=3, dd=18, distance=5.0, condition=70.0, runningDist=6.0)
    facade.add_runData(rec)
    facade.insert_into_db()

    # isNodata: データあり → False
    assert not facade.isNodata()

    # getAllDatas: loader.getAllDatas を経由。登録件数が1件であること
    datas = facade.getAllDatas()
    assert len(datas) == 1

    # saveAsSchedule: SaveRunSchedule.add_runData を経由して RunSchedule テーブルへ登録
    facade.saveAsSchedule(6.0, 5.0, 70.0)

    # getSchedule: 登録済みデータを dict として取得。yyyy / mm / dd キーが含まれること
    result = facade.getSchedule()
    assert isinstance(result, dict)
    assert 'yyyy' in result
    assert 'mm' in result
    assert 'dd' in result

    # addRecord: バッファ不使用で1件直接追加（EntryRunData.addRecord を経由）
    rec2 = ValueCheck(yyyy=2026, mm=4, dd=1, distance=8.0, condition=80.0, runningDist=7.5)
    facade.addRecord(rec2)
    datas2 = facade.getAllDatas()
    assert len(datas2) == 2

    # updateRecord: 対象レコードを更新（EntryRunData.updateRecord を経由）
    target_id = datas2[0].id
    updated_rec = ValueCheck(yyyy=2026, mm=6, dd=1, distance=10.0, condition=90.0, runningDist=9.0)
    facade.updateRecord(target_id, updated_rec)

    # deleteRecord: 対象レコードを削除（EntryRunData.deleteRecord を経由）
    facade.deleteRecord(target_id)
    datas3 = facade.getAllDatas()
    assert len(datas3) == 1
