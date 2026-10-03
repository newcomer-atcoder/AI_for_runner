import sys
from pathlib import Path

import pytest
import torch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

#webApp側は src 起点(from my_modules...)でimportするため、src を sys.path に加える
SRC_DIR = Path(__file__).parent.parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from webApp.api import apiSettings          # noqa: E402
from my_modules.ai import models            # noqa: E402  (src.my_modules.ai.models とは別物。こちらを差し替える)
from my_modules.ai.models import DefaultModel  # noqa: E402
from my_modules.data.entry import EntryRunData, ValueCheck  # noqa: E402
import main                                  # noqa: E402  (全routerをinclude済みのapp)


@pytest.fixture
def client(monkeypatch, tmp_path, tmp_model_path):
    #本番の src/app.db・src/checkpoint.pt を汚さないよう、共有オブジェクトの属性を差し替える
    monkeypatch.setattr(apiSettings.dbFacade.setup, 'engine', create_engine(f'sqlite:///{tmp_path / "test.db"}'))
    monkeypatch.setattr(apiSettings.dbFacade, 'entry', EntryRunData())
    monkeypatch.setattr(apiSettings.aiFacade, 'newModel', DefaultModel())
    monkeypatch.setattr(models, 'MODEL_PATH', tmp_model_path)
    monkeypatch.setattr(models, 'SETUP_EPOCH', 10)   #テスト時間を短くする
    apiSettings.dbFacade.setUp_Done()                 #テーブル作成
    return TestClient(main.app)


#未確定データに1件追加する(POST /entry/)
def entry_one(client, distance=10.0, condition=80.0, runningDist=9.2):
    return client.post('/entry/?clearSchedule=0', json={
        'yyyy': 2026, 'mm': 10, 'dd': 3,
        'distance': distance, 'condition': condition, 'runningDist': runningDist,
    })


#DBに直接1件入れる(未確定リストは使わない)
def add_record_direct():
    apiSettings.dbFacade.addRecord(ValueCheck(
        yyyy=2026, mm=10, dd=3, distance=10.0, condition=80.0, runningDist=9.2,
    ))


#GET / (最初に開くタブの判定)
def test_root_no_record_opens_entry(client):
    res = client.get('/')
    assert res.status_code == 200
    assert 'data-initial-tab="entry"' in res.text
    assert 'data-record-exists="0"' in res.text


def test_root_record_opens_inference(client):
    add_record_direct()
    res = client.get('/')
    assert res.status_code == 200
    assert 'data-initial-tab="inference"' in res.text
    assert 'data-record-exists="1"' in res.text


def test_root_schedule_opens_entry(client):
    add_record_direct()
    apiSettings.dbFacade.saveAsSchedule(9.4, 10.0, 80.0)   #(runningDist, distance, condition)
    res = client.get('/')
    assert res.status_code == 200
    assert 'data-initial-tab="entry"' in res.text
    assert 'data-record-exists="1"' in res.text


def test_root_tab_param(client):
    #0件で ?tab=inference を指定しても、推論タブは押せないので登録タブ
    res = client.get('/?tab=inference')
    assert 'data-initial-tab="entry"' in res.text

    #記録があれば ?tab=entry を指定すると登録タブ(予定がなくても)
    add_record_direct()
    res = client.get('/?tab=entry')
    assert 'data-initial-tab="entry"' in res.text


#旧URLのリダイレクト
def test_old_urls_redirect(client):
    res = client.get('/entry/', follow_redirects=False)
    assert res.status_code == 303
    assert res.headers['location'] == '/?tab=entry'

    res = client.get('/inference/', follow_redirects=False)
    assert res.status_code == 303
    assert res.headers['location'] == '/?tab=inference'


#未確定の件数と取り消し (D2.4, D8.2, D8.8)
def test_entry_and_cancel(client):
    assert entry_one(client).json()['pending_cnt'] == 1
    assert entry_one(client).json()['pending_cnt'] == 2

    res = client.post('/api/entry/cancel/')
    assert res.status_code == 200
    body = res.json()
    assert body['canceled_cnt'] == 2
    assert body['pending_cnt'] == 0

    #DBには何も書き込まれていない
    assert apiSettings.dbFacade.isNodata()


#登録終了&学習 (D3.1)
def test_update_db_no_data(client, tmp_model_path):
    res = client.post('/updateDB/')
    assert res.status_code == 200
    assert res.json()['entry_exit_result'] == 'NoData'
    assert not tmp_model_path.exists()


def test_update_db_setup_then_add_train(client, tmp_model_path):
    #1件目: モデルがないので初期学習
    entry_one(client)
    res = client.post('/updateDB/')
    body = res.json()
    assert body['entry_exit_result'] == 'EntryDone'
    assert body['train_status'] == 'Setup'
    assert body['pending_cnt'] == 0
    assert torch.load(tmp_model_path, weights_only=True)['epoch'] == models.SETUP_EPOCH

    #2件目: モデルがあるので追加学習
    entry_one(client, distance=12.0, runningDist=11.5)
    res = client.post('/updateDB/')
    body = res.json()
    assert body['entry_exit_result'] == 'EntryDone'
    assert body['train_status'] == 'AddTrain'
    assert body['pending_cnt'] == 0
    assert torch.load(tmp_model_path, weights_only=True)['epoch'] == models.SETUP_EPOCH + models.ADD_TRAIN_EPOCH


#推論タブのモデル準備 (D3.2)
def test_prepare(client, tmp_model_path):
    #DB0件では何もしない
    assert client.post('/api/model/prepare/').json()['prepare_result'] == 'NoData'
    assert not tmp_model_path.exists()

    #記録があり、checkpointがなければ初期学習
    add_record_direct()
    assert client.post('/api/model/prepare/').json()['prepare_result'] == 'Setup'
    assert tmp_model_path.exists()

    #もう一度呼ぶと学習は不要
    assert client.post('/api/model/prepare/').json()['prepare_result'] == 'Ready'


#推論結果の予定保存 (D4.1, A1)
def test_save_schedule(client):
    info = '本日のあなたの適正距離(km)：9.400km(あなたの入力：10.0km＆80.0%)'
    res = client.post('/save/', params={'saveInfo': info})
    assert res.status_code == 200
    body = res.json()
    assert 'schedule' in body
    assert body['schedule']['distance'] == 10.0
    assert body['schedule']['condition'] == 80.0
    assert body['schedule']['runningDist'] == 9.4

    #数値を3つ取り出せない文字列は保存せず、schedule も返さない
    res = client.post('/save/', params={'saveInfo': '不正な文字列'})
    body = res.json()
    assert 'schedule' not in body
    assert body['result'] == '推論をやり直してください'
