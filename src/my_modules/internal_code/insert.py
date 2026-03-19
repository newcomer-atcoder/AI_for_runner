import sys
from pydantic import BaseModel, Field, ValidationError
from typing import Union
import datetime
import re
from sqlalchemy import Engine
from sqlalchemy.orm import Session, DeclarativeBase

#定数(会話プロンプト)
PLEASE_INPUT_YOUR_RUNDATA = "\n「日付(yyyy/mm/dd)」「走行予定の距離(km)」「体調(%)」「実際に走った距離(km)」を、半角スペース区切りで入力してください\n(入力を終了する場合は「q」を入力):"
EXIT_CMD = "q"
EXIT_CMD_MSG = "ランニング記録の入力終了"
INSERT_OK = "登録成功"
NAN_MSG = "日付や数値ではない値が入力されました。再入力してください。"
LESS_ITEMS = "入力が不足しています。再入力してください"

#定数
DATE_INDEX = 0
DISTANCE_INDEX = 1
CONDITION_INDEX = 2
RUNNINGDIST_INDEX = 3
DIST_MIN_VALUE, CONDITION_MIN_VALUE, CONDITION_MAX_VALUE = 0, 0, 100 #0km, 0~100%

#DBに登録する値のチェック用
class ValueCheck(BaseModel):
    date : Union[datetime.date, None]
    distance : float = Field(ge=DIST_MIN_VALUE)
    condition : float = Field(ge=CONDITION_MIN_VALUE, le=CONDITION_MAX_VALUE)
    runningDist : float = Field(ge=DIST_MIN_VALUE)

#登録本体
class EnterCMD:
    def __init__(self, dbsetup_flg):
        self.dbsetup_flg = dbsetup_flg
    
    def input_runData(self):
        checkedValueList = []
        while 1:
            try:
                print(PLEASE_INPUT_YOUR_RUNDATA)
                input_datas = sys.stdin.readline().strip()
                if input_datas == EXIT_CMD and not(self.dbsetup_flg and not checkedValueList):
                    print(EXIT_CMD_MSG)
                    break
            
                input_data_list = input_datas.split()
                date_str = input_data_list[DATE_INDEX]
                if re.search(r"20[0-9][0-9]/(0[0-9]|1[0-2])/([0-2][0-9]|3[0-1])", date_str) is None:
                    nowDate = None
                else:
                    yyyy, dd, mm = map(int, date_str.split("/"))
                    nowDate = datetime.date(yyyy, dd, mm)
                checkedValues = ValueCheck(date=nowDate, distance=input_data_list[DISTANCE_INDEX], condition=input_data_list[CONDITION_INDEX], runningDist=input_data_list[RUNNINGDIST_INDEX])
                checkedValueList += [checkedValues]
                print(INSERT_OK)
        
            except ValidationError:
                print(NAN_MSG)
            
            except IndexError:
                print(LESS_ITEMS)
        
        self.checkedValueList = checkedValueList
    
    def insert_into_db(self, engine : Engine, RunDist : DeclarativeBase):
        with Session(engine) as session:
            inserts = []
            for checkedValues in self.checkedValueList:
                inserts += [RunDist(date=checkedValues.date, distance=checkedValues.distance, condition=checkedValues.condition, runningDist=checkedValues.runningDist)]
            session.add_all(inserts)
            session.commit()
