from webApp.api.apiSettings import dbFacade, htmlTemp, app, int_code_html
from webApp.api.apiSettings import int_code_path, delete_record_path

from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from pydantic import BaseModel, Field

#テーブル一覧を取得し表示する
@app.get(int_code_path, response_class=HTMLResponse)
def getMethod(request: Request):
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

    return htmlTemp.TemplateResponse(
        int_code_html,
        {
            'request' : request,
            'records' : records
        }
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
