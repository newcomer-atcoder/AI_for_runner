#自作モジュール
from my_modules.ai.facade import AIFacade
from my_modules.data.facade import DBFacade, ValueCheck

#APIライブラリ
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#その他標準モジュール
from pathlib import Path
import sys

######################################################
#
#以下にmain.pyおよびapi_xxx.pyが利用する機能を定義しておく
#
#######################################################

#APIサーバ準備
app = FastAPI()
if getattr(sys, 'frozen', False):
    #exe化時: PyInstallerの展開先(_MEIPASS)にバンドルされたwebApp/を参照
    app_dir = Path(sys._MEIPASS)/'webApp'
else:
    app_dir = Path(__file__).parent.parent

#テンプレート&静的ファイルのパスを指定
htmlTemp = Jinja2Templates(directory=app_dir/'templates')
app.mount('/static', StaticFiles(directory=app_dir/'static'), 'url_static')

#htmlファイルの名称とファイルパス
init_html = 'app_init.html'
entry_html = 'app_entry.html'
inference_html = 'app_inference.html'
notFound_html = 'notFound.html' #404 not foundの際に表示する共通のページ
int_code_html = 'int_code.html'

init_path = '/'
entry_path = '/entry/'
inference_path = '/inference/'
int_code_path = '/intcode/'

exit_app_path = '/exit/'        #アプリ終了処理のリクエスト先
exit_entry_path = '/updateDB/'  #entryページの入力終了処理のリクエスト先
save_schedule_path = '/save/'   #AIの推論結果を、次の予定として記録
delete_record_path = '/api/delete/' #int_code経由でレコード削除
update_display_page_path = '/api/updPage/' #int_codeで表示する範囲(=10件のレコード)を更新する
receive_update_path = '/api/submit/' #int_codeでレコード1件更新
receive_add_path = '/api/add/'       # int_codeでレコードを1件新規追加

#DB操作と機械学習、それぞれの窓口クラスオブジェクトを生成しておく
aiFacade = AIFacade()
dbFacade = DBFacade()