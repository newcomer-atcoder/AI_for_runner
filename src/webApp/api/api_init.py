#自作モジュール
from .apiSettings import init_html, init_path, notFound_html, exit_app_path
from .apiSettings import app
from .apiSettings import htmlTemp
from .apiSettings import dbFacade

#APIライブラリ
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

######################################################
#
#以下にapp_init画面機能と、共通処理を定義しておく
#
#######################################################

initRouter = APIRouter()

#faviconを回避
@initRouter.get('/favicon.ico')
def favicon():
    return Response(status_code=204)  # No Content

@initRouter.get(init_path, response_class=HTMLResponse)
def init_app(request : Request):
    return htmlTemp.TemplateResponse(
        init_html,
        {'request' : request, 'dbsetup_flg' : dbFacade.setUp_Done()}
    )

"""
#404 Not Found
@initRouter.exception_handler(404)
def not_found_handler(request: Request, exc):
    return htmlTemp.TemplateResponse(
        notFound_html,
        {'request': request},
        status_code=404
    )
"""

#アプリ終了ボタン
@initRouter.post(exit_app_path)
def exitApp():
    app.state.server.should_exit = True
    return {'message': 'exit app'}