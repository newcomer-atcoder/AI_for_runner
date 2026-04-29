from pydantic import BaseModel, Field
import datetime
from sqlalchemy import Engine, select, delete
from sqlalchemy.orm import Session, DeclarativeBase
from abc import ABC, abstractmethod

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

#雛形
class EntryBase(ABC):
    def __init__(self):
        self.checkedValueList = [] #ValueCheckクラス変数を格納
    
    #WEBアプリで入力した値をValueCheckクラス変数で受け取る
    @abstractmethod
    def add_runData(self):
        pass

    #データ登録
    @abstractmethod
    def insert_into_db(self):
        pass


#全てのランニング記録を管理
class EntryRunData(EntryBase):
    def add_runData(self, runData : ValueCheck):
        self.checkedValueList += [runData]
    
    def insert_into_db(self, engine : Engine, RunDist : DeclarativeBase):
        with Session(engine) as session:
            inserts = []
            for checkedValues in self.checkedValueList:
                nowDate = datetime.date(checkedValues.yyyy, checkedValues.mm, checkedValues.dd)
                inserts += [RunDist(date=nowDate, distance=checkedValues.distance, condition=checkedValues.condition, runningDist=checkedValues.runningDist)]
            session.add_all(inserts)
            session.commit()
    
    #データ登録件数の確認
    #データ0件か否かを判定し、0件であればWEB画面(app_inference)の遷移を禁止する
    def isNodata(self, engine : Engine, Rundist : DeclarativeBase):
        with Session(engine) as session:
            stmt = select(Rundist)
            result = session.scalars(stmt)
            resultLen = len(result.all())
        return  resultLen == 0

#次回のランニングの予定を1件管理する
class SaveRunSchedule(EntryBase):
    def add_runData(self, runData : ValueCheck):
        #1件のみ登録する
        self.checkedValueList = [runData]
    
    def insert_into_db(self, engine : Engine, RunSchedule : DeclarativeBase):
        with Session(engine) as session:
            #delete
            stmt = delete(RunSchedule)
            session.execute(stmt)

            #insert
            #現在の日付と、画面側(=app_inference)から取得した値を登録
            checkedValues = self.checkedValueList[0]
            nowDate = datetime.date(checkedValues.yyyy, checkedValues.mm, checkedValues.dd)
            insert_one = RunSchedule(date=nowDate, distance=checkedValues.distance, condition=checkedValues.condition, runningDist=checkedValues.runningDist)
            session.add(insert_one)
            session.commit()
    
    def getSchedule(self, engine : Engine, RunSchedule : DeclarativeBase)\
        -> dict|None:
        with Session(engine) as session:
            stmt = select(RunSchedule)
            result = session.scalars(stmt).one_or_none()
        return  result if result is None else result.__dict__