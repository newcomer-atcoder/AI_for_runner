# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 19:17:06 2026

@author: runningAI
"""

from src.my_modules.data import DefaultData
import pytest
import pandas

#1.load_TrainingDataメソッド

#前提1.テストケースの入力は、Csvファイルで行う(実際のデータ入力と同じ)
#前提2.Csvファイルには1ファイル1行で入力
#試験観点：ファイルの入力内容と、self.distance_conditionsとself.runnningDistsの内容が合致すること。
#　　　　　　ファイル内の数値が入力制限を満たすこと
#　　　　　　※エラーメッセージが出力されればOKとする

ERROR_POSI_MSG = "{}の{}行目。"
ERROR_ALERT_MSG = "\n不正な入力を検知しました。アプリを再起動して、学習用データファイルを修正してください。\
                   \n修正の際、以下にご注意ください。\
                   \n1.全角文字や半角英字は数値に変換できません。\
                   \n2.入力値の制限をご確認ください。\
                   \n　-距離(km)：0以上の数値(非負整数)\
                   \n　-体調(%)：0~100の整数値"
ERROR_ITEMS = "\n入力内容：[走行予定の距離(km):{}, 体調(%):{}, 実走距離(km):{}]"
FILE_PATH = "学習用データ\テスト用\テストデータ(load_TrainigData){}.csv" #ローカル配置、非公開
FILE_NAME = "テストデータ(load_TrainigData){}.csv" #ローカル配置、非公開

def test_load_TrainingData():
    #正常パターン
    #期待値
    distance, condition = 7.0, 40.0
    runningDist = 5.0
    #結果
    testDefaultData = DefaultData(FILE_PATH.format("1"))
    testDefaultData.load_TrainingData()
    [result_distance, result_condition] = testDefaultData.distance_conditions_Tensor[0]
    [result_runningDist] = testDefaultData.runningDists_Tensor[0]

    assert [distance, condition] == [result_distance, result_condition]
    assert result_runningDist == runningDist
    
    #エラーパターン
    #数値が境界値外である
    #走行予定の距離(km) < 0 or 体調(%) < 0 or 体調(%) > 100 or 実走距離(km) < 0
    #数値以外の入力
    #未入力項目
    for fileNum in range(2, 9):
        filePath = FILE_PATH.format(str(fileNum))
        with pytest.raises(ValueError) as e:
            testDefaultData = DefaultData(filePath)
            testDefaultData.load_TrainingData()
        
        df = pandas.read_csv(filePath)
        distance, condition, runnningDist = df.iloc[0, 1:] #1行目の読み込みでエラーが出る前提
        assert str(e.value) == ERROR_POSI_MSG.format(FILE_NAME.format(str(fileNum)), "2") +\
            ERROR_ITEMS.format(distance, condition, runnningDist) + ERROR_ALERT_MSG
