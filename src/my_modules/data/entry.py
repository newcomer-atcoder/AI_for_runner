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
YEAR_MIN_VALUE = 1900
MONTH_MIN_VALUE, MONTH_MAX_VALUE = 1, 12
DAY_MIN_VALUE, DAY_MAX_VALUE = 1, 31

#DBに登録する値のチェック用
class ValueCheck(BaseModel):
    yyyy : int = Field(ge=YEAR_MIN_VALUE)
    mm : int = Field(ge=MONTH_MIN_VALUE, le=MONTH_MAX_VALUE)
    dd : int = Field(ge=DAY_MIN_VALUE, le=DAY_MAX_VALUE)
    distance : float = Field(ge=DIST_MIN_VALUE)
    condition : float = Field(ge=CONDITION_MIN_VALUE, le=CONDITION_MAX_VALUE)
    runningDist : float = Field(ge=DIST_MIN_VALUE)

#登録本体
class EntryRunData:
    def __init__(self, dbsetup_flg):
        self.dbsetup_flg = dbsetup_flg
        self.checkedValueList = [] #ValueCheckクラス変数を格納
    
    #jsからValueCheckクラス変数を受け取る
    def add_runData(self, runData : ValueCheck):
        self.checkedValueList += [runData]
    
    def insert_into_db(self, engine : Engine, RunDist : DeclarativeBase):
        with Session(engine) as session:
            inserts = []
            for checkedValues in self.checkedValueList:
                nowDate = datetime.date(checkedValues.yyyy, checkedValues.dd, checkedValues.mm)
                inserts += [RunDist(date=nowDate, distance=checkedValues.distance, condition=checkedValues.condition, runningDist=checkedValues.runningDist)]
            session.add_all(inserts)
            session.commit()
