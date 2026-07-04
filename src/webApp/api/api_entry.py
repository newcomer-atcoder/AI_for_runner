#標準ライブラリ
import datetime

#自作モジュール
from .apiSettings import entry_html, entry_path, exit_entry_path
from .apiSettings import htmlTemp
from .apiSettings import dbFacade

#APIライブラリ
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

######################################################
#
#以下にapp_entry画面機能と、データ登録処理を定義しておく
#
#######################################################

#app_initからapp_entry画面にリダイレクト
entryRouter = APIRouter()
@entryRouter.get(entry_path, response_class=HTMLResponse)
def goto_nextPage(request : Request, result=None):
    return_dict = {'request' : request, 'result' : '' if result is None else result}
    
    #以前登録したランニングの予定がある場合、登録画面に自動入力する
    if result is None:
        #クエリパラメータなし：これまで通り runSchedule の予定を自動入力
        schedule : dict | None = dbFacade.getSchedule()
        return_dict['schedule'] = schedule
    else:
        #クエリパラメータあり：今日の年月日のみを自動入力（距離・体調・実走距離は空欄）
        today = datetime.date.today()
        return_dict['schedule'] = {
            'yyyy' : today.year,
            'mm' : today.month,
            'dd' : today.day,
        }

    return htmlTemp.TemplateResponse(
        entry_html,
        return_dict
    )

#app_entry画面のランニング記録(日付, km, 体調)の入力を受ける
#422例外はjsで吸収あと、goto_nextPage関数に"/entry/?result=登録失敗"として飛ばす
EntryValueCheck = dbFacade.ValueCheck
@entryRouter.post(entry_path)
def entry_runData(runData : EntryValueCheck, clearSchedule : bool = False):
    dbFacade.add_runData(runData)

    #クエリパラメータなしの状態からの登録時は、runSchedule テーブルを空にする
    if clearSchedule:
        dbFacade.deleteSchedule()

    return {
            'entry_result' : f'登録成功 : {runData.yyyy}/{runData.mm}/{runData.dd}, {runData.distance}km, {runData.condition}%, {runData.runningDist}km'
    }

#app_entry画面の登録終了時に、内部ではDBInsertを行う
@entryRouter.post(exit_entry_path)
def exitEntry():
    #DB更新
    dbFacade.insert_into_db()

    #更新後のメッセージ
    entry_status = 'NoData'\
        if dbFacade.isNodata() else 'EntryDone'

    return {'entry_exit_result' : entry_status}