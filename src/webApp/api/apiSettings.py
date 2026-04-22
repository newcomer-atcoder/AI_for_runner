#自作モジュール
from my_modules.ai.facade import AIFacade
from my_modules.data.facade import DBFacade, ValueCheck

#APIライブラリ
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#その他標準モジュール
from pathlib import Path

######################################################
#
#以下にmain.pyおよびapi_xxx.pyが利用する機能を定義しておく
#
#######################################################

#APIサーバ準備
app = FastAPI()
app_dir = Path(__file__).parent.parent

#テンプレート&静的ファイルのパスを指定
htmlTemp = Jinja2Templates(directory=app_dir/'templates')
app.mount('/static', StaticFiles(directory=app_dir/'static'), 'url_static')

#htmlファイルの名称とファイルパス
init_html = 'app_init.html'
entry_html = 'app_entry.html'
inference_html = 'app_inference.html'
notFound_html = 'notFound.html' #404 not foundの際に表示する共通のページ

init_path = '/'
entry_path = '/entry/'
inference_path = '/inference/'

exit_app_path = '/exit/'        #アプリ終了処理のリクエスト先
exit_entry_path = '/updateDB/'  #entryページの入力終了処理のリクエスト先
save_schedule_path = '/save/'   #AIの推論結果を、次の予定として記録

#DB操作と機械学習、それぞれの窓口クラスオブジェクトを生成しておく
aiFacade = AIFacade()
dbFacade = DBFacade()