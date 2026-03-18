# -*- coding: utf-8 -*-

from .data import DefaultData
from .models import DefaultModel

class AIFacade:
    def __init__(self,):
        #サブシステムクラスのセット
        self.data = DefaultData()
        self.newModel = DefaultModel()
    
    def load_TrainingData(self):
        #学習用データを読み取り指示
        self.data.load_TrainingData()
    
    def trainingDone(self):
        #機械学習指示
        distance_conditions, runnningDists = self.data.getTensorDatas()
        self.newModel.trainingDone(distance_conditions, runnningDists)
    
    def inference(self, distance, condition):
        #推論指示
        return self.newModel.inference(distance, condition)
