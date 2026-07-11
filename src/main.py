# -*- coding: utf-8 -*-

#自作モジュール
from webApp.api.api_entry import entryRouter
from webApp.api.api_inference import inferenceRouter
from webApp.api.api_init import initRouter
from webApp.api.api_int_code import intCodeRouter
from webApp.api.apiSettings import app

#その他標準モジュール
import uvicorn
import time
import os
import sys
import socket
import multiprocessing
from concurrent.futures import ThreadPoolExecutor as thread
import webbrowser

#--noconsole(-w)ビルド時はsys.stdout/sys.stderrがNoneになり、
#uvicornのログ出力(StreamHandler)が起動時にクラッシュするため、devnullへ逃がす
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

#src/webApp/api以下の各APIRouterをインクルードして、mainでリクエストを受け取り可にする
app.include_router(initRouter)
app.include_router(entryRouter)
app.include_router(inferenceRouter)
app.include_router(intCodeRouter)

#アプリ実行直後にapp_init画面を表示
def loadApp():
    #固定sleepではなく、サーバが起動するまで最大30秒待ってからブラウザを開く
    #(exe化するとtorchのロードで起動が3秒を超え、ブラウザが先に開いて接続失敗するため)
    for _ in range(60):
        try:
            with socket.create_connection(('127.0.0.1', 8000), timeout=0.5):
                break
        except OSError:
            time.sleep(0.5)
    webbrowser.open('http://127.0.0.1:8000')

def main():
    config = uvicorn.Config(app, host='127.0.0.1', port=8000)
    server = uvicorn.Server(config)
    app.state.server = server

    with thread(max_workers=2) as executor:
        executor.submit(loadApp)
        executor.submit(server.run)

if __name__ == "__main__":
    #PyInstaller製exeが子プロセス起動時に自分自身を再帰実行する事故を防ぐ(定番対策)
    multiprocessing.freeze_support()
    main()