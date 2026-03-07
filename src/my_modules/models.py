# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.optim as optim

#my_modules.data.DefaultDataで取得した「デフォルト形式」のデータを学習
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
    
    def trainingDone(self, distance_conditions_Tensor, runningDists_Tensor):
        #学習方法を定義
        model = self.model
        optimizer = optim.Adam(model.parameters(), lr=0.01) #重み(傾き)とバイアス(切片)をパラメータで取得
        loss_fn = nn.MSELoss()
        
        #機械学習開始
        trainingCnt = 500
        for _ in range(trainingCnt):
            pred = model(distance_conditions_Tensor) #モデルの予測値（出力）を取得
            loss = loss_fn(pred, runningDists_Tensor) #正解との誤差を取得
            optimizer.zero_grad()  # 勾配(.grad)をリセット ※.gradはtorch内の共有メモリに保持されるため、torchに属するモジュールやオブジェクトは参照可能
            loss.backward()        # [正解との誤差]/ [重み] = 勾配(.grad) ※厳密には違うが、横軸方向の誤差?x軸を勾配(.grad)だけ動かせば誤差を補正可能
            optimizer.step()       # [勾配(.grad)]*[学習率(lr)]を重みに加算し、更新 ※重み(傾き)増減させて正解に近づける
        
        self.model = model
    
    def inference(self, distance, condition):
        #「実走距離(km)」の推論、ランナーに「おすすめの距離(km)」として返却
        distance_condition = torch.tensor([[distance, condition]])
        return self.model(distance_condition)