#自作モジュール
from .apiSettings import main_html, init_path, notFound_html, exit_app_path
from .apiSettings import app
from .apiSettings import htmlTemp
from .apiSettings import dbFacade

#APIライブラリ
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

######################################################
#
#以下にメイン画面(登録・推論タブ)の表示と、共通処理を定義しておく
#
#######################################################

initRouter = APIRouter()

#faviconを回避
@initRouter.get('/favicon.ico')
def favicon():
    return Response(status_code=204)  # No Content

@initRouter.get(init_path, response_class=HTMLResponse)
def init_app(request : Request, tab : str | None = None):
    #テーブル自動生成の副作用があるため、最初に呼ぶ
    dbFacade.setUp_Done()

    schedule = dbFacade.getSchedule()
    has_schedule = 'distance' in schedule
    record_exists = not dbFacade.isNodata()

    #最初に開くタブ (D2.1, D1.3)
    if tab == 'entry':
        initial_tab = 'entry'
    elif tab == 'inference' and record_exists:
        initial_tab = 'inference'
    elif (not record_exists) or has_schedule:
        initial_tab = 'entry'   #?tab=inference でも推論タブを押せない場合はここに来る
    else:
        initial_tab = 'inference'

    return htmlTemp.TemplateResponse(
        main_html,
        {
            'request' : request,
            'initial_tab' : initial_tab,
            'record_exists' : 1 if record_exists else 0,
            'pending_cnt' : dbFacade.getPendingCount(),
            'schedule' : schedule,
            'schedule_date' : f"{schedule['yyyy']:04d}-{schedule['mm']:02d}-{schedule['dd']:02d}",  #<input type="date">用
            'fromSchedule' : 1 if has_schedule else 0,
        }
    )


#404 Not Found
@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    return htmlTemp.TemplateResponse(
        notFound_html,
        {'request': request},
        status_code=404
    )


#アプリ終了ボタン
@initRouter.post(exit_app_path)
def exitApp():
    app.state.server.should_exit = True
    return {'message': 'exit app'}