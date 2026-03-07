# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 15:49:34 2026

@author: runningAI
"""

from src.my_modules.data import Data

#定数
FILE_PASS = "学習用データ\デフォルト学習用データ.csv"
FILE_NAME = "デフォルト学習用データ.csv"

class tmpData(Data):
    def load_TrainingData(self):
        pass
    
    def getTensorDatas(self):
        pass


def test_constract():
    #userif.pyでcsvファイルが選択される前提
    testCls = tmpData(FILE_PASS)
    print("here")
    assert testCls.fileName == FILE_NAME
