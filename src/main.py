# -*- coding: utf-8 -*-

#自作モジュール
from my_modules.userif import select_file_in_dialog
from my_modules.facade import AIFacade

#定数(会話プロンプト)
HELLO = "こんにちは、あなたのランニングを支援します"
PLEASE_SELECT_FILE = "最初に、学習用データ(Csv)を選択してください (y/n):"
SELECT_FILE = "y"
FILE_IS_SELECTED = "学習用データ(Csv)の取得に成功しました!"
FILE_IS_NOT_SELECTED = "学習用データ(Csv)を取得できませんでした。\nアプリを再起動して、学習用データファイルを再度選択してください。"
EXIT_AI = "AIを終了します"
PLEASE_INPUT_DATAS = "\n「走行予定の距離(km)」「体調(%)」を、半角スペース区切りで入力してください\n(入力を終了する場合は「q」を入力):"
EXIT_CMD = "q"
NAN_MSG = "数値ではない値が入力されました。あるいは入力が不足しています。再入力してください。"
OUTPUT_RUNNING_DISTANCE = "本日のあなたの適正距離(km):"

#その他定数
NOFILE = ""


def main():
    #学習用データ(Csv)の入力を促す
    print(HELLO)
    print(PLEASE_SELECT_FILE)
    
    filePass = NOFILE
    if input() == SELECT_FILE:
        filePass = select_file_in_dialog()
    
    if filePass == NOFILE:
        print(FILE_IS_NOT_SELECTED)
        print(EXIT_AI)
        return
    else:
        print(FILE_IS_SELECTED)
    
    #AI処理のファサード(窓口)を生成し、AIに学習用データ(Csv)を機械学習させる
    aiFacade = AIFacade(filePass)
    aiFacade.load_TrainingData()
    aiFacade.trainingDone()
    
    #ユーザー入力、ファサード(窓口)に処理依頼、推論値出力
    while 1:
        try:
            print(PLEASE_INPUT_DATAS)
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