# -*- coding: utf-8 -*-

#自作モジュール
from my_modules.database.setup import DBSetUp
from my_modules.database.models import RunDist
from my_modules.data.entry import EnterCMD
from my_modules.ai.facade import AIFacade

#定数(会話プロンプト)
HELLO = "こんにちは、あなたのランニングを支援します"
ASK_YOU_INPUT_YOUR_RUNDATA = "AIに過去のランニング記録を入力しますか (y/n):"
INPUT_MY_RUNDATA = "y"
YOU_MUST_INPUT_YOUR_RUNDATA = "DBの初回セットアップが完了しました\n続けてAIに過去のランニング記録を入力してください"
PLEASE_INPUT_DISTANCE_AND_CONDITION = "\n「走行予定の距離(km)」「体調(%)」を、半角スペース区切りで入力してください\n(入力を終了する場合は「q」を入力):"
EXIT_CMD = "q"
EXIT_AI = "AIを終了します"
NAN_MSG = "数値ではない値が入力されました。あるいは入力が不足しています。再入力してください。"
OUTPUT_RUNNING_DISTANCE = "本日のあなたの適正距離(km):"


def main():
    #DBの初回セットアップ(バックグラウンド処理)
    dbsetup = DBSetUp()
    dbsetup_flg = dbsetup.setUp_Done()
    engine = dbsetup.engine

    #アプリ起動(ユーザ側に最初に表示)
    print(HELLO)
    if not dbsetup_flg:
        print(ASK_YOU_INPUT_YOUR_RUNDATA)
        isInput_my_rundata = input() == INPUT_MY_RUNDATA
    else:
        #DBセットアップ時はランニング記録の入力必須
        print(YOU_MUST_INPUT_YOUR_RUNDATA)
        isInput_my_rundata = True
    
    if isInput_my_rundata:
        cmd_mode = EnterCMD(dbsetup_flg)
        cmd_mode.input_runData()
        cmd_mode.insert_into_db(engine, RunDist)
    
    #AI処理のファサード(窓口)を生成し、AIに学習用データ(Csv)を機械学習させる
    aiFacade = AIFacade()
    aiFacade.load_TrainingData(engine, RunDist)
    aiFacade.trainingDone()
    
    #ユーザー入力、ファサード(窓口)に処理依頼、推論値出力
    while 1:
        try:
            print(PLEASE_INPUT_DISTANCE_AND_CONDITION)
            input_datas = input()
            if input_datas == EXIT_CMD:
                print(EXIT_AI)
                break
            
            distance, condition = map(float, input_datas.split())
            x = aiFacade.inference(distance, condition)
            print(OUTPUT_RUNNING_DISTANCE)
            print(float(x))
        
        except ValueError:
            print(NAN_MSG)

if __name__ == "__main__":
    main()