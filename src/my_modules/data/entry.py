from pydantic import BaseModel, Field
import datetime
from sqlalchemy import Engine
from sqlalchemy.orm import Session, DeclarativeBase

#定数(DBに登録する値のチェック用)
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
    def __init__(self):
        self.checkedValueList = [] #ValueCheckクラス変数を格納
    
    #WEBアプリで入力した値をValueCheckクラス変数で受け取る
    def add_runData(self, runData : ValueCheck):
        self.checkedValueList += [runData]
    
    #データ登録
    def insert_into_db(self, engine : Engine, RunDist : DeclarativeBase):
        with Session(engine) as session:
            inserts = []
            for checkedValues in self.checkedValueList:
                nowDate = datetime.date(checkedValues.yyyy, checkedValues.mm, checkedValues.dd)
                inserts += [RunDist(date=nowDate, distance=checkedValues.distance, condition=checkedValues.condition, runningDist=checkedValues.runningDist)]
            session.add_all(inserts)
            session.commit()
