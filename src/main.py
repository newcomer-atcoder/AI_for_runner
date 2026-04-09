# -*- coding: utf-8 -*-

#自作モジュール
from webApp.api.api_entry import entryRouter
from webApp.api.api_inference import inferenceRouter
from webApp.api.api_init import initRouter
from webApp.api.apiSettings import app

#その他標準モジュール
import uvicorn
import time
from concurrent.futures import ThreadPoolExecutor as thread
import webbrowser

#src/webApp/api以下の各APIRouterをインクルードして、mainでリクエストを受け取り可にする
app.include_router(initRouter)
app.include_router(entryRouter)
app.include_router(inferenceRouter)

#アプリ実行直後にapp_init画面を表示
def loadApp():
    time.sleep(3)
    webbrowser.open('http://127.0.0.1:8000')

def main():
    config = uvicorn.Config(app, host='127.0.0.1', port=8000)
    server = uvicorn.Server(config)
    app.state.server = server

    with thread(max_workers=2) as executor:
        executor.submit(loadApp)
        executor.submit(server.run)

if __name__ == "__main__":
    main()
