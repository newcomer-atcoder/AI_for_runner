#自作モジュール
from .apiSettings import init_path, inference_path, save_schedule_path, prepare_model_path
from .apiSettings import aiFacade, dbFacade, prepareModel

#APIライブラリ
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

#その他標準モジュール
import re

######################################################
#
#以下に推論タブのAPIを定義しておく
#
#######################################################

#旧 /inference/ 画面は、メイン画面の推論タブ(/?tab=inference)へリダイレクト
inferenceRouter = APIRouter()
@inferenceRouter.get(inference_path)
def redirect_inference():
    return RedirectResponse(f'{init_path}?tab=inference', status_code=status.HTTP_303_SEE_OTHER)

#推論タブを開いたときに呼ばれ、モデルを推論できる状態にする(必要に応じて初期学習)
@inferenceRouter.post(prepare_model_path)
def prepareModelApi():
    return {'prepare_result' : prepareModel()}

#推論タブのkm, 体調の入力を受ける
#422例外はjsで吸収する
@inferenceRouter.post(inference_path)
def inference(distance : float, condition : float):
    result_value = aiFacade.inference(distance, condition)
    if result_value is None:
        result_info = '数値ではない値が入力されました。あるいは入力が不足しています。再入力してください'
    else:
        result_info = f'本日のあなたの適正距離(km)：{result_value}km'
    result_info += f'(あなたの入力：{distance}km＆{condition}%)'
    return {
            'inference_result' : result_info,
            'inference_ok' : result_value is not None,
    }

#AIの推論結果を、次の予定として記録
inference_result_nums = 3
isSaved = '保存しました(AIの予測：{}km, 入力値：{}km, {}%)'
isNotSaved = '推論をやり直してください'
@inferenceRouter.post(save_schedule_path)
def saveAsSchedule(saveInfo : str):
    nums = re.findall(r'([0-9]+\.[0-9]+)', saveInfo)

    if len(nums) == inference_result_nums:
        #AIの推論結果と入力値、併せて3点を読み込み次の予定として記録する
        result = isSaved.format(*nums)
        dbFacade.saveAsSchedule(*nums)
        s = dbFacade.getSchedule()
        return {
            'result' : result,
            'schedule' : {
                'yyyy' : s['yyyy'], 'mm' : s['mm'], 'dd' : s['dd'],
                'distance' : s['distance'], 'condition' : s['condition'], 'runningDist' : s['runningDist'],
            },
        }
    #AIの推論結果と入力値、併せて3点を取得できなければ、推論をやり直す
    return {'result' : isNotSaved}
