#標準ライブラリ
from pydantic import ValidationError

#自作モジュール
from ..database.setup import DBSetUp
from ..database.models import RunDist
from .entry import ValueCheck, EntryRunData

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
        self.ValueCheck = ValueCheck
    
    #DBの初回セットアップが行われたか判定する
    def setUp_Done(self):
        return self.setup.setUp_Done()
    
    #DB操作に必要なengine(connector)とORMクラスを渡す
    def getDBAccessInfo(self):
        return self.setup.engine, RunDist
    
    #WEBアプリで入力された値がself.entryに保管される
    def add_runData(self, runData : ValueCheck):
        self.entry.add_runData(runData)
    
    #self.entryに保管されたデータを登録
    def insert_into_db(self):
        self.entry.insert_into_db(self.setup.engine, RunDist)
    
