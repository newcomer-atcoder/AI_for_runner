import torch
from abc import ABC, abstractmethod
from sqlalchemy import select, Engine, desc
from sqlalchemy.orm import Session, DeclarativeBase

REPLAY_CNT = 20

class Data(ABC):
    @abstractmethod
    def load_TrainingData(self):
        pass
    
    @abstractmethod
    def getTensorDatas(self):
        pass

#初期(Default)ver
#「走行予定の距離(km)」「体調(%)」「実際に走った距離(km)」を管理
class DefaultData(Data):
    def load_TrainingData(
        self, engine : Engine, RunDist : DeclarativeBase,
        add_data_cnt
    ):
        #フィールド値の初期化
        distance_conditions = []
        runningDists = []
        
        #DBから全件取得
        with Session(engine) as session:
            stmt = select(RunDist)
            if add_data_cnt is not None:
                # モデル更新の場合、追加のデータ + 既存のデータ (直近`REPLAY_CNT`件) をロード
                limit = add_data_cnt + REPLAY_CNT
                stmt = stmt.order_by(desc(RunDist.id)).limit(limit)

            TrainingDatas = session.scalars(statement=stmt)
        
            #「走行予定の距離(km)」「体調(%)」と「実際に走った距離(km)」をそれぞれの配列にセット
            for TrainingData in TrainingDatas:
                distance_conditions += [[TrainingData.distance, TrainingData.condition]]
                runningDists += [[TrainingData.runningDist]]

        #tensor型に変換してセット
        self.distance_conditions_Tensor = torch.tensor(distance_conditions, dtype=torch.float32)
        self.runningDists_Tensor = torch.tensor(runningDists, dtype=torch.float32)

    def getTensorDatas(self):
        return self.distance_conditions_Tensor, self.runningDists_Tensor
    
#内部コード(int_code.py)用にレコード全件取得
def getAllDatas(engine : Engine, RunDist : DeclarativeBase) -> list[DeclarativeBase]:
    allDatas = []
    with Session(engine) as session:
        stmt = select(RunDist)
        allDatas = session.scalars(stmt).all()
    
    return allDatas #list[DeclarativeBase]型