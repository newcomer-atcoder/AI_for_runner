from webApp.api.apiSettings import dbFacade, htmlTemp, app, int_code_html, ValueCheck
from webApp.api.apiSettings import (
    int_code_path, delete_record_path, update_display_page_path,
    receive_update_path, receive_add_path,
)

from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from pydantic import BaseModel, Field

#テーブル一覧
unit = 10
class TableDisplay:
    _instance = None

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, records: list[dict] = None):
        if records is not None:
            self.setInitTables(records)

    def setInitTables(self, records: list[dict]):
        tables = [] #ランニング記録を10件づつ記録するための配列
        for i in range(0, len(records), unit):
            tables += records[i : min(len(records), i + unit)]
        self.tables = tables
        self.display_index = 0 #表示する情報の範囲を、tablesのindexで表す
    
    def setIndex(self, index):
        self.display_index = index
        print(self.display_index)
    
    def getIndex(self):
        return self.display_index
    
    def getTable(self):
        #10件取得
        unit = 10
        Len = len(self.tables)
        index = self.display_index
        return self.tables[index * unit : min(Len, (index + 1) * unit)]
    
    def getTableLength(self):
        if getattr(self, 'tables', None) is None:
            return 0
        return len(self.tables)

#テーブル一覧を取得し表示する
#ランニング記録を10件表示
@app.get(int_code_path, response_class=HTMLResponse)
def getMethod(request: Request, page: int = None):
    #初期表示
    if page is None:
        db_infos = dbFacade.getAllDatas()
        records = []
        for db_info in db_infos:
            record = {
                'id': db_info.id,
                'date': db_info.date,
                'planned_distance': db_info.distance,
                'condition': db_info.condition,
                'actual_distance' : db_info.runningDist
            }
            records += [record]
        
        #一覧を保存
        tables = TableDisplay(records)
    
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
    
    nowPage = tables.getIndex()
    LEN = tables.getTableLength()
    first_page: bool = nowPage == 0
    last_page: bool = nowPage == LEN // unit + (0 if LEN % unit > 0 else -1)
        
    return htmlTemp.TemplateResponse(
        int_code_html,
        {
            'request' : request,
            'records' : tables.getTable(),
            'page' : tables.getIndex(),
            'first_page' : first_page,
            'last_page' : last_page
        }
    )

#テーブル一覧で表示する範囲を更新
@app.get(update_display_page_path)
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

@app.delete(delete_record_path)
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

@app.put(receive_update_path)
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

@app.post(receive_add_path)
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