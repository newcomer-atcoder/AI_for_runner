from webApp.api.apiSettings import dbFacade, htmlTemp, int_code_html, ValueCheck
from webApp.api.apiSettings import (
    int_code_path, delete_record_path, update_display_page_path,
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
######################################################

#テーブル一覧
unit = 10 #1ページで表示する件数
class TableDisplay:
    _instance = None

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, records: list[dict] | None = None):
        if records is not None:
            self.setInitTables(records)

    def setInitTables(self, records: list[dict]):
        tables = [] #ランニング記録を10件づつ記録するための配列
        for i in range(0, len(records), unit):
            tables += records[i : min(len(records), i + unit)]
        self.tables = tables
        self.display_index = 0 #表示する情報の範囲を、tablesのindexで表す
        self.headerItems = {}

    def setHeaderItems(self, headerItems: dict):
        self.headerItems = headerItems

    def getHeaderItems(self) -> dict:
        return getattr(self, 'headerItems', {})
    
    def setIndex(self, index):
        self.display_index = index
        print(self.display_index)
    
    def getIndex(self):
        return self.display_index
    
    def getTable(self):
        #10件取得
        Len = len(self.tables)
        index = self.display_index
        return self.tables[index * unit : min(Len, (index + 1) * unit)]
    
    def getTableLength(self):
        if getattr(self, 'tables', None) is None:
            return 0
        return len(self.tables)

#テーブル一覧を取得し表示する
#ランニング記録を10件表示
@intCodeRouter.get(int_code_path, response_class=HTMLResponse)
def getMethod(request: Request, page: int | None = None, month: str | None = None):
    tables = TableDisplay() # ここに10件単位で🏃記録を保存
    isMonthlyReport = month is not None and month in tables.getHeaderItems()
    print(f'デバッグ: {month} / {isMonthlyReport}')

    #初期表示
    if page is None:
        db_infos = dbFacade.getAllDatas()
        records = [] # 全ランニング記録
        no_record = 0

        nowYear, nowMonth = datetime.datetime.now().year, datetime.datetime.now().month
        
        if isMonthlyReport:
            yyyy, mm = map(int, tables.getHeaderItems().get(month).split('/'))
            isSelect = True
        else:
            yyyy, mm = nowYear, nowMonth
            isSelect = False
        print(f'デバッグ: {yyyy}/{mm}')

        #ヘッダ項目(年月, 総記録数, 平均体調, 合計走行距離) + 月次レポートの選択肢
        headerItems = {
            'yyyymm': f'{yyyy}/{mm}',
            'this_month': f'{nowYear}/{nowMonth}',
            'last_month': f'{nowYear}/{nowMonth - 1}' if nowMonth > 1 else f'{nowYear - 1}/12',
            'last_two_month': f'{nowYear}/{nowMonth - 2}' if nowMonth > 2 else f'{nowYear - 2}/12',
            'isSelect': isSelect,
            'run_cnt': no_record,
            'condition_ave': no_record,
            'actual_distance_sum': no_record
        }

        for db_info in db_infos:
            # 全レコードの情報を取得
            record = {
                'id': db_info.id,
                'date': db_info.date,
                'planned_distance': db_info.distance,
                'condition': db_info.condition,
                'actual_distance' : db_info.runningDist
            }

            if not (
                    isMonthlyReport and
                    not(db_info.date.year == yyyy and db_info.date.month == mm)
                ):
                records += [record]

            # 当月分の記録を取得
            if db_info.date.year == yyyy and db_info.date.month == mm:
                headerItems['run_cnt'] += 1
                headerItems['condition_ave'] += db_info.condition
                headerItems['actual_distance_sum'] += db_info.runningDist
        
        #一覧を保存
        tables.setInitTables(records)

        # 当月分の記録の平均値算出と整形
        run_cnt = headerItems['run_cnt']
        if run_cnt != no_record:
            condition_ave = headerItems['condition_ave'] / run_cnt
            headerItems['run_cnt'] = f'{headerItems["run_cnt"]}回'
            headerItems['condition_ave'] = f'{round(condition_ave, 1)}%'
            headerItems['actual_distance_sum'] = f'{headerItems["actual_distance_sum"]}km'
        else:
            no_record_str = '-'
            headerItems['run_cnt'] = no_record_str
            headerItems['condition_ave'] = no_record_str
            headerItems['actual_distance_sum'] = no_record_str
        tables.setHeaderItems(headerItems)
    
    #ページスクロールした場合
    else:
        tables = TableDisplay()

        #サーバ起動後に最初から"http://127.0.0.1:8000/?page=3"などをリロードした場合は
        #クエリパラメータなしのURLに飛ぶように誘導する
        if tables.getTableLength() == 0:
            return RedirectResponse(
                url=int_code_path,
                status_code=status.HTTP_303_SEE_OTHER
            )

        headerItems = tables.getHeaderItems()
    
    nowPage = tables.getIndex()
    LEN = tables.getTableLength()
    first_page: bool = nowPage == 0
    if LEN == 0:
        last_page = True
        last_page_num = 0
    else:
        last_page_num = LEN // unit + (0 if LEN % unit > 0 else -1)
        last_page: bool = nowPage == last_page_num
        
    return htmlTemp.TemplateResponse(
        int_code_html,
        {
            'request' : request,
            'records' : tables.getTable(),
            'headerItems': headerItems,
            'page' : tables.getIndex(),
            'first_page' : first_page,
            'last_page' : last_page,
            'last_page_num' : last_page_num
        }
    )

#テーブル一覧で表示する範囲を更新
@intCodeRouter.get(update_display_page_path)
def updPage(page: str):
    tables = TableDisplay()
    tables.setIndex(int(page))

    return RedirectResponse(
        url=int_code_path + f'?page={page}',
        status_code=status.HTTP_303_SEE_OTHER
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

    # getMethod(クエリなしの'/')へ
    return RedirectResponse(
        int_code_path,
        status_code=status.HTTP_303_SEE_OTHER,
    )