#自作モジュール
from .apiSettings import inference_html, inference_path
from .apiSettings import htmlTemp
from .apiSettings import aiFacade, dbFacade

#APIライブラリ
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

######################################################
#
#以下にapp_inference画面機能を定義しておく
#
#######################################################

##app_initからapp_inference画面にリダイレクト
inferenceRouter = APIRouter()
@inferenceRouter.get(inference_path, response_class=HTMLResponse)
def goto_nextPage(request : Request, result=None):
    if result == None:
        #entryページから遷移するタイミングで機械学習
        (engine, RunDist) = dbFacade.getDBAccessInfo()
        aiFacade.load_TrainingData(engine, RunDist)
        aiFacade.trainingDone()

    return_dict = {'request' : request, 'result' : '' if result is None else result}
    return htmlTemp.TemplateResponse(
        inference_html,
        return_dict
    )


#app_inference画面のkm, 体調の入力を受ける
#422例外はjsで吸収あと、goto_nextPage関数に"/inference/?result=入力エラー"として飛ばす
@inferenceRouter.post(inference_path)
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
