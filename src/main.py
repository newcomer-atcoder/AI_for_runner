# -*- coding: utf-8 -*-

#自作モジュール
from my_modules.ai.facade import AIFacade
from my_modules.data.facade import DBFacade

#APIライブラリ
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response

#その他
import uvicorn
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor as thread
import webbrowser

#APIサーバ準備
app = FastAPI()

#jsファイルの設定
app_dir = Path(__file__).parent
app.mount('/static', StaticFiles(directory=app_dir/'webApp'/'static'), 'url_static')

#htmlとパスの設定
htmlTemp = Jinja2Templates(directory=app_dir/'webApp'/'templates')

init_html = 'app_init.html'; init_path = '/';
entry_html = 'app_entry.html'; entry_path = 'entry';
inference_html = 'app_inference.html'; inference_path = 'inference';
code200_pairs = {
    entry_path : entry_html,
    inference_path : inference_html
}

exit_app_path = '/exit/'
exit_entry_path = '/updateDB/'
notFound_html = 'notFound.html'

#faviconを回避
@app.get('/favicon.ico')
def favicon():
    return Response(status_code=204)  # No Content

#アプリ実行直後にapp_init画面を表示
dbFacade = DBFacade()
dbsetup_flg = dbFacade.setUp_Done()
EntryValueCheck = dbFacade.ValueCheck
def loadApp():
    time.sleep(3)
    webbrowser.open('http://127.0.0.1:8000')

@app.get(init_path, response_class=HTMLResponse)
def init_app(request : Request):
    return htmlTemp.TemplateResponse(
        init_html,
        {'request' : request, 'dbsetup_flg' : dbsetup_flg}
    )

#app_entry/app_inference画面にリダイレクト
#上記とapp_init画面以外は404例外
aiFacade = AIFacade()
@app.get('/{path_id}/', response_class=HTMLResponse)
def goto_nextPage(request : Request, path_id, result=None):
    if path_id not in code200_pairs:
        raise HTTPException(status_code=404)
    
    if path_id == inference_path and result == None:
        #機械学習
        (engine, RunDist) = dbFacade.getDBAccessInfo()
        aiFacade.load_TrainingData(engine, RunDist)
        aiFacade.trainingDone()

    return_dict = {'request' : request, 'result' : '' if result is None else result}
    return htmlTemp.TemplateResponse(
        code200_pairs[path_id],
        return_dict
    )

#404 Not Found
@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    return htmlTemp.TemplateResponse(
        notFound_html,
        {'request': request},
        status_code=404
    )

#app_entry画面の入力を受ける
#422例外はjsで吸収
@app.post(f'/{entry_path}/')
def entry_runData(runData : EntryValueCheck):
    dbFacade.add_runData(runData)
    return {
            'entry_result' : f'登録成功 : {runData.yyyy}/{runData.mm}/{runData.dd}, {runData.distance}km, {runData.condition}%, {runData.runningDist}km'
    }

#app_entry画面の登録終了時に、内部ではDBInsertを行う
#AIFacadeの準備(データ変換と機械学習)も行う
@app.post(exit_entry_path)
def exitEntry():
    #DB更新
    dbFacade.insert_into_db()
    return {'entry_exit_result' : 'DB更新&機械学習完了'}

#app_inference画面の入力を受ける
#422例外はjsで吸収
@app.post(f'/{inference_path}/')
def inference(distance : float, condition : float):
    result_value = aiFacade.inference(distance, condition)
    if result_value is None:
        result_info = '数値ではない値が入力されました。あるいは入力が不足しています。再入力してください'
    else:
        result_info = f'本日のあなたの適正距離(km)：{result_value}km'
    result_info += f'(あなたの入力：{distance}km＆{condition}%)'
    return {
            'inference_result' : result_info
    }

#アプリ終了ボタン
@app.post(exit_app_path)
def exitApp():
    app.state.server.should_exit = True
    return {'message': 'exit app'}

if __name__ == "__main__":
    config = uvicorn.Config(app, host='127.0.0.1', port=8000)
    server = uvicorn.Server(config)
    app.state.server = server

    with thread(max_workers=2) as executor:
        executor.submit(loadApp)
        executor.submit(server.run)
    