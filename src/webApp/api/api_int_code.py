from webApp.api.apiSettings import dbFacade, htmlTemp, int_code_html, ValueCheck, aiFacade
from webApp.api.apiSettings import (
    int_code_path, delete_record_path,
    receive_update_path, receive_add_path,
)

from fastapi import status, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from pydantic import BaseModel, Field
import datetime

intCodeRouter = APIRouter()

######################################################
#
#以下に開発者向け管理画面(int_code)機能を定義しておく
#main.py から intCodeRouter を include して /intcode/ で表示する
#
#表示範囲(ページ)と月次レポートの絞り込みは int_code.js が担当する。
#サーバはレコード全件と、月次レポート選択肢ごとのヘッダ集計値を返すだけ。
#
######################################################

#基準日から back ヶ月前の(年, 月)を返す(年またぎを正しく処理する)
def shiftMonth(base: datetime.date, back: int) -> tuple[int, int]:
    total = base.year * 12 + (base.month - 1) - back
    return total // 12, total % 12 + 1

#指定した年月のヘッダ項目(総記録数, 平均体調, 合計走行距離)を整形して返す
def buildMonthStats(records: list[dict], yyyy: int, mm: int) -> dict:
    ym = f'{yyyy}/{mm}'
    targets = [record for record in records if record['ym'] == ym]

    #該当月に記録が無い場合
    if not targets:
        no_record_str = '-'
        return {
            'ym': ym,
            'run_cnt': no_record_str,
            'condition_ave': no_record_str,
            'actual_distance_sum': no_record_str,
        }

    run_cnt = len(targets)
    condition_ave = sum(target['condition'] for target in targets) / run_cnt
    return {
        'ym': ym,
        'run_cnt': f'{run_cnt}回',
        'condition_ave': f'{round(condition_ave, 1)}%',
        'actual_distance_sum': f'{sum(target["actual_distance"] for target in targets)}km',
    }

#テーブル一覧を取得し表示する
#ランニング記録は全件返し、10件ずつの出し分けは int_code.js が行う
@intCodeRouter.get(int_code_path, response_class=HTMLResponse)
def getMethod(request: Request):
    records = [
        {
            'id': db_info.id,
            'date': db_info.date,
            'ym': f'{db_info.date.year}/{db_info.date.month}',
            'planned_distance': db_info.distance,
            'condition': db_info.condition,
            'actual_distance': db_info.runningDist,
        }
        for db_info in dbFacade.getAllDatas()
    ]

    #月次レポートの選択肢(今月・先月・先々月)ごとのヘッダ項目
    today = datetime.date.today()
    monthItems = {
        key: buildMonthStats(records, *shiftMonth(today, back))
        for key, back in (('this_month', 0), ('last_month', 1), ('last_two_month', 2))
    }

    return htmlTemp.TemplateResponse(
        int_code_html,
        {
            'request': request,
            'records': records,
            'monthItems': monthItems,
        }
    )

#レコード削除
class Json(BaseModel):
    id : int = Field(ge=1)

@intCodeRouter.delete(delete_record_path)
def deleteMethod(req: Json):
    id = req.id
    dbFacade.deleteRecord(id)

    return RedirectResponse(
        url= int_code_path,
        status_code=status.HTTP_303_SEE_OTHER
    )

# レコード更新
class Row(BaseModel):
    id: int = Field(ge=1)
    yyyy: int = Field(ge=1)
    mm: int = Field(ge=1)
    dd: int = Field(ge=1)
    planned_distance: float = Field(ge=1)
    condition: float = Field(ge=1)
    actual_distance: float = Field(ge=1)

@intCodeRouter.put(receive_update_path)
def updateMethod(req: Row):
    row = ValueCheck(
        yyyy=req.yyyy,
        mm=req.mm,
        dd=req.dd,
        distance=req.planned_distance,
        condition=req.condition,
        runningDist=req.actual_distance
    )

    dbFacade.updateRecord(req.id, row)

    return RedirectResponse(
        int_code_path,
        status_code=status.HTTP_303_SEE_OTHER
    )

# 新規追加で受け取るリクエストボディ(idは無し=自動採番)
class NewRow(BaseModel):
    yyyy: int = Field(ge=1)
    mm: int = Field(ge=1)
    dd: int = Field(ge=1)
    planned_distance: float = Field(ge=0)
    condition: float = Field(ge=0)
    actual_distance: float = Field(ge=0)

@intCodeRouter.post(receive_add_path)
def addMethod(req: NewRow):
    # ValueCheck で範囲検証(体調0〜100、距離>=0 など)
    runData = ValueCheck(
        yyyy=req.yyyy, mm=req.mm, dd=req.dd,
        distance=req.planned_distance,
        condition=req.condition,
        runningDist=req.actual_distance,
    )

    # 新設の専用メソッドで1件INSERT
    dbFacade.addRecord(runData)

    # データ登録と機械学習は同時に行う
    # 従って管理画面は登録ごとに学習を行う
    load_success = aiFacade.load_pt_model()
    if load_success:
        (engine, RunDist) = dbFacade.getDBAccessInfo()
        aiFacade.load_TrainingData(engine, RunDist, 1)
        aiFacade.addTrain()

    # getMethod(クエリなしの'/')へ
    return RedirectResponse(
        int_code_path,
        status_code=status.HTTP_303_SEE_OTHER,
    )