#標準ライブラリ
from pydantic import ValidationError
import datetime

#自作モジュール
from ..database.setup import DBSetUp
from ..database.models import RunDist, RunSchedule
from .entry import ValueCheck, EntryRunData, SaveRunSchedule

#定数(DBエントリーで用いるカラム名)
yyyy = 'yyyy'
mm = 'mm'
dd = 'dd'
distance = 'distance'
condition = 'condition'
runningDist = 'runningDist'

#DBのセットアップからエントリー・ダウンロード操作などを担う
class DBFacade:
    def __init__(self):
        self.setup = DBSetUp()
        self.entry = EntryRunData()
        self.schedule = SaveRunSchedule()
        self.ValueCheck = ValueCheck
    
    #DBの初回セットアップが行われたか判定する
    def setUp_Done(self):
        return self.setup.setUp_Done()
    
    #DB操作に必要なengine(connector)とORMクラスを、ai/側のfacadeに渡す
    def getDBAccessInfo(self):
        return self.setup.engine, RunDist
    
    #WEBアプリで入力された値がself.entryに追加・保管される
    def add_runData(self, runData : ValueCheck):
        self.entry.add_runData(runData)
    
    #self.entryに保管されたデータを登録
    def insert_into_db(self):
        self.entry.insert_into_db(self.setup.engine, RunDist)
    
    #self.entry経由で現在DBの登録件数が0件か否か判定
    def isNodata(self):
        return self.entry.isNodata(self.setup.engine, RunDist)
    
    #AIの推論結果を、次の予定として記録
    #DB登録処理について補足：N+1問題を内包（アプリ自体が軽いため無視する）
    def saveAsSchedule(self, *args):
        (runningDist, distance, condition) = args
        print(f'check!{args}')
        now = datetime.datetime.now()
        runData = ValueCheck(yyyy=now.year, mm=now.month, dd=now.day, distance=distance, condition=condition, runningDist=runningDist)
        self.schedule.add_runData(runData)
        self.schedule.insert_into_db(self.setup.engine, RunSchedule)
    
    #登録画面を呼び出す際、過去に記録したランニング予定を取得する
    def getSchedule(self):
        return_dict = self.schedule.getSchedule(self.setup.engine, RunSchedule)
        return_dict['yyyy'] = return_dict['date'].year
        return_dict['mm'] = return_dict['date'].month
        return_dict['dd'] = return_dict['date'].day
        return return_dict

