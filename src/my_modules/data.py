# -*- coding: utf-8 -*-

import torch
from abc import ABC, abstractmethod
import pandas
import re
from pydantic import BaseModel, Field, ValidationError
from typing import Union

#定数(エラーメッセージ)
##共通部品
ERROR_MSG_HEADER = "\nエラー発生："
ERROR_LOG_HEADER = "\n以下のエラーログを確認しました："

##load_TrainingDataで使用
ERROR_POSI_MSG = "{}の{}行目。"
ERROR_ALERT_MSG = "\n不正な入力を検知しました。アプリを再起動して、学習用データファイルを修正してください。\
                   \n修正の際、以下にご注意ください。\
                   \n1.全角文字や半角英字は数値に変換できません。\
                   \n2.入力値の制限をご確認ください。\
                   \n　-距離(km)：0以上の数値(非負整数)\
                   \n　-体調(%)：0~100の整数値"

#定数(validation check)
DIST_MIN_VALUE = 0 #0km
CONDITION_MIN_VALUE = 0 #0%
CONDITION_MAX_VALUE = 100 #100%

#学習用データ取得
class Data(ABC):
    def __init__(self, filePath):
        self.filePath = filePath
        fileName_match = re.search(r"[^\\]+\.csv", filePath)
        self.fileName = fileName_match.group()

    @abstractmethod
    def load_TrainingData(self):
        pass
    
    @abstractmethod
    def getTensorDatas(self):
        pass

#簡易処理ver

#distance:走行予定の距離(km)は0以上の数値であるか
#condition:体調(%)は0~100の整数値であるか
#runningDist:実走距離(km)は0以上の数値であるか
class CheckDefaultData(BaseModel):
    distance : Union[int, float] = Field(ge=DIST_MIN_VALUE)
    condition : int = Field(ge=CONDITION_MIN_VALUE, le=CONDITION_MAX_VALUE)
    runningDist : Union[int, float] = Field(ge=DIST_MIN_VALUE)

class DefaultData(Data):
    def load_TrainingData(self):
        #csvのカラム名
        distance_colName = "走行予定の距離(km)"
        condition_colName = "体調(%)"
        runningDist_colName = "実走距離(km)"

        #上記カラムのデータを抜粋
        df = pandas.read_csv(self.filePath)
        df_TrainingData = df.loc[:, distance_colName:runningDist_colName]
        
        #フィールド値の初期化
        distance_conditions = []
        runningDists = []
        
        #入力制限を満たすか確認
        fix_index_to_row = 2
        for rowInfo in df_TrainingData.itertuples():
            distance, condition, runningDist = rowInfo[1:]
            try:
                checkedDatas = CheckDefaultData(distance=distance, condition=condition, runningDist=runningDist)
                distance_conditions += [[checkedDatas.distance, checkedDatas.condition]]
                runningDists += [[checkedDatas.runningDist]]
            
            except ValidationError:
                ERROR_ITEMS = f"\n入力内容：[{distance_colName}:{distance}, {condition_colName}:{condition}, {runningDist_colName}:{runningDist}]"
                Validation_Is_Error = ERROR_POSI_MSG.format(self.fileName, rowInfo.Index + fix_index_to_row) + ERROR_ITEMS + ERROR_ALERT_MSG
                print(ERROR_MSG_HEADER)
                print(Validation_Is_Error)
                print(ERROR_LOG_HEADER)
                raise ValueError(Validation_Is_Error)

        # データを、numpyからtensorに変換
        self.distance_conditions_Tensor = torch.tensor(distance_conditions, dtype=torch.float32)
        self.runningDists_Tensor = torch.tensor(runningDists, dtype=torch.float32)

    def getTensorDatas(self):
        return self.distance_conditions_Tensor, self.runningDists_Tensor
