#自作モジュール
from .apiSettings import init_path, entry_path, exit_entry_path, cancel_entry_path
from .apiSettings import dbFacade, prepareModel

#APIライブラリ
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

######################################################
#
#以下にデータ登録処理(登録タブのAPI)を定義しておく
#
#######################################################

#旧 /entry/ 画面は、メイン画面の登録タブ(/?tab=entry)へリダイレクト
entryRouter = APIRouter()
@entryRouter.get(entry_path)
def redirect_entry():
    return RedirectResponse(f'{init_path}?tab=entry', status_code=status.HTTP_303_SEE_OTHER)

#登録タブのランニング記録(日付, km, 体調)の入力を受ける
#422例外はjsで吸収する
EntryValueCheck = dbFacade.ValueCheck
@entryRouter.post(entry_path)
def entry_runData(runData : EntryValueCheck, clearSchedule : str = '0'):
    dbFacade.add_runData(runData)

    #runScheduleテーブルのデータを登録済みであれば、テーブルを空にする
    if clearSchedule == '1':
        dbFacade.deleteSchedule()

    return {
            'entry_result' : f'登録成功 : {runData.yyyy}/{runData.mm}/{runData.dd}, {runData.distance}km, {runData.condition}%, {runData.runningDist}km',
            'pending_cnt' : dbFacade.getPendingCount(),
    }

#登録タブの登録終了&学習時に、内部ではDBInsertと学習を行う
@entryRouter.post(exit_entry_path)
def exitEntry():
    #DB更新(バルクINSERT)
    dbFacade.insert_into_db()
    #insert_into_dbはリストを空にしないため、ここで空にしつつ追加件数を得る
    added = dbFacade.refresh_rundata()

    if dbFacade.isNodata():
        return {'entry_exit_result' : 'NoData', 'pending_cnt' : 0}

    train_status = prepareModel(len(added))
    return {
        'entry_exit_result' : 'EntryDone',
        'train_status' : train_status,   #'Setup' / 'AddTrain' / 'Ready'
        'pending_cnt' : 0,
    }

#未確定の登録データを全件取り消す(DB・次回予定には手を加えない)
@entryRouter.post(cancel_entry_path)
def cancelEntry():
    canceled = dbFacade.refresh_rundata()
    return {
        'cancel_result' : f'未確定の記録 {len(canceled)} 件を取り消しました',
        'canceled_cnt' : len(canceled),
        'pending_cnt' : dbFacade.getPendingCount(),   #常に0
    }
