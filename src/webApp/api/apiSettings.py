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
main_html = 'app_main.html'          #登録・推論タブを持つメイン画面
notFound_html = 'notFound.html' #404 not foundの際に表示する共通のページ
int_code_html = 'int_code.html'

init_path = '/'
entry_path = '/entry/'
inference_path = '/inference/'
int_code_path = '/intcode/'

exit_app_path = '/exit/'        #アプリ終了処理のリクエスト先
exit_entry_path = '/updateDB/'  #entryページの入力終了処理のリクエスト先
cancel_entry_path = '/api/entry/cancel/'     #未確定データの取り消し (D8.2)
prepare_model_path = '/api/model/prepare/'   #推論タブ表示時のモデル準備 (D3.2)
save_schedule_path = '/save/'   #AIの推論結果を、次の予定として記録
delete_record_path = '/api/delete/' #int_code経由でレコード削除
receive_update_path = '/api/submit/' #int_codeでレコード1件更新
receive_add_path = '/api/add/'       # int_codeでレコードを1件新規追加

#DB操作と機械学習、それぞれの窓口クラスオブジェクトを生成しておく
aiFacade = AIFacade()
dbFacade = DBFacade()

#モデルを推論できる状態にする(必要に応じて学習)
#  add_data_cnt: 今回DBに追加した件数(追加学習の対象)
#  戻り値: 'NoData'(DB0件で何もしない) / 'Setup'(初期学習) / 'AddTrain'(追加学習) / 'Ready'(学習不要)
def prepareModel(add_data_cnt: int = 0) -> str:
    if dbFacade.isNodata():
        return 'NoData'

    load_success = aiFacade.load_pt_model()
    (engine, RunDist) = dbFacade.getDBAccessInfo()

    #.ptファイルが見つからない(または読めない)場合は、DB全件で初期学習
    if not load_success:
        print('機械学習モデルをセットアップ')
        aiFacade.load_TrainingData(engine, RunDist)
        aiFacade.trainingDone()
        return 'Setup'

    #今回追加したデータ + 直近データで追加学習
    if add_data_cnt:
        print('追加でモデルトレーニングを実施')
        aiFacade.load_TrainingData(engine, RunDist, add_data_cnt)
        aiFacade.addTrain()
        return 'AddTrain'

    return 'Ready'