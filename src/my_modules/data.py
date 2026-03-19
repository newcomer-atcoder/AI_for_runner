# -*- coding: utf-8 -*-

import torch
from abc import ABC, abstractmethod
from sqlalchemy import select, Engine
from sqlalchemy.orm import Session, DeclarativeBase

class Data(ABC):
    @abstractmethod
    def load_TrainingData(self):
        pass
    
    @abstractmethod
    def getTensorDatas(self):
        pass

#初期(Default)ver
#「走行予定の距離(km)」「体調(%)」「実走距離(%)」を管理
class DefaultData(Data):
    def load_TrainingData(self, engine : Engine, RunDist : DeclarativeBase):
        #フィールド値の初期化
        distance_conditions = []
        runningDists = []
        
        #DBから全件取得
        with Session(engine) as session:
            stmt = select(RunDist)
            TrainingDatas = session.scalars(statement=stmt)
        
            #「走行予定の距離(km)」「体調(%)」と「実走距離(%)」をそれぞれの配列にセット
            for TrainingData in TrainingDatas:
                distance_conditions += [[TrainingData.distance, TrainingData.condition]]
                runningDists += [[TrainingData.runningDist]]

        #tensor型に変換してセット
        self.distance_conditions_Tensor = torch.tensor(distance_conditions, dtype=torch.float32)
        self.runningDists_Tensor = torch.tensor(runningDists, dtype=torch.float32)

    def getTensorDatas(self):
        return self.distance_conditions_Tensor, self.runningDists_Tensor
