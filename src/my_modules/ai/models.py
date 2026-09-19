import torch
import torch.nn as nn
import torch.optim as optim
from pydantic import BaseModel, Field, ValidationError
from pathlib import Path

# 学習モデルの保存先
MODEL_PATH = Path(__file__).parent / 'model.pt'
SETUP_EPOCH = 500
ADD_TRAIN_EPOCH = 20
MODEL_STATE = 'model_state_dict'
OPTIM_STATE = 'optimizer_state_dict'
EPOCH_CNT = 'epoch'

#推論処理の入力値のチェック用
DIST_MIN_VALUE, CONDITION_MIN_VALUE, CONDITION_MAX_VALUE = 0, 0, 100 #0km, 0~100%
class ValueCheck_Inference(BaseModel):
    distance : float = Field(ge=DIST_MIN_VALUE)
    condition : float = Field(ge=CONDITION_MIN_VALUE, le=CONDITION_MAX_VALUE)
    

#my_modules.data.loader.DefaultDataで取得した「デフォルト形式」のデータを学習
#※以下のコメントは、AIが生成したコードを開発者が理解・イメージ内容を記載しているため
#　正確ではない内容を含みます
class DefaultModel:
    def __init__(self):
        #モデルの初期化
        InputData, outputData = 2, 1
        middleLayer = 16
        model = nn.Sequential(
            nn.Linear(InputData, middleLayer),
            nn.ReLU(),
            nn.Linear(middleLayer, outputData)
        )

        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=0.01) #重み(傾き)とバイアス(切片)をパラメータで取得

    def load_pt_model(self) -> bool:
        if not MODEL_PATH.exists():
            return False

        checkpoint = torch.load(MODEL_PATH, weights_only= False)
        self.model.load_state_dict(checkpoint[MODEL_STATE])
        self.optimizer.load_state_dict(checkpoint[OPTIM_STATE])
        self.epoch = checkpoint[EPOCH_CNT]
        return True
    
    def trainingDone(
        self,
        distance_conditions_Tensor,
        runningDists_Tensor,
        model_setup: bool = False # load_pt_modelがFalseだった場合は.ptファイルを作成
    ):
        #学習方法を定義
        loss_fn = nn.MSELoss()
        
        #機械学習開始
        epoch = SETUP_EPOCH if model_setup else ADD_TRAIN_EPOCH
        for _ in range(epoch):
            pred = self.model(distance_conditions_Tensor) #モデルの予測値（出力）を取得
            loss = loss_fn(pred, runningDists_Tensor) #正解との誤差を取得
            self.optimizer.zero_grad()  # 勾配(.grad)をリセット ※.gradはtorch内の共有メモリに保持されるため、torchに属するモジュールやオブジェクトは参照可能
            loss.backward()        # [正解との誤差]/ [重み] = 勾配(.grad) ※厳密には違うが、横軸方向の誤差?x軸を勾配(.grad)だけ動かせば誤差を補正可能
            self.optimizer.step()       # [勾配(.grad)]*[学習率(lr)]を重みに加算し、更新 ※重み(傾き)増減させて正解に近づける
        
        # 結果を保存
        torch.save(
            {
                MODEL_STATE: self.model.state_dict(),
                OPTIM_STATE: self.optimizer.state_dict(),
                EPOCH_CNT: epoch if SETUP_EPOCH else self.epoch + epoch
            },
            MODEL_PATH
        )
    
    def inference(self, distance, condition):
        #入力制限を満たすか確認する
        try:
            inputs = ValueCheck_Inference(distance=distance, condition=condition)
        
        except (ValidationError, IndexError, ValueError):
            return None

        #「実際に走る距離(km)」の推論、ランナーに「本日のあなたの適正距離(km)」として返却
        distance_condition = torch.tensor([[inputs.distance, inputs.condition]])
        runningDist = float(self.model(distance_condition))
        return f'{runningDist:.3f}'