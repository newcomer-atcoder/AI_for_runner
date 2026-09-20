from ..data.loader import DefaultData
from .models import DefaultModel
import torch

class AIFacade:
    def __init__(self):
        #サブシステムクラスのセット
        self.data = DefaultData()
        self.newModel = DefaultModel()

    def load_pt_model(self):
        # 機械学習モデルをロード
        return self.newModel.load_pt_model()


    def load_TrainingData(self, engine, RunDist, add_data_cnt : int | None = None):
        #学習用データを読み取り指示
        self.data.load_TrainingData(engine, RunDist, add_data_cnt)
    
    def trainingDone(self):
        #機械学習指示
        distance_conditions, runnningDists = self.data.getTensorDatas()
        self.newModel.trainingDone(distance_conditions, runnningDists, model_setup=True)

    def addTrain(self):
        distance_conditions, runnningDists = self.data.getTensorDatas()
        self.newModel.trainingDone(distance_conditions, runnningDists)
    
    def inference(self, distance, condition):
        #推論指示
        return self.newModel.inference(distance, condition)
