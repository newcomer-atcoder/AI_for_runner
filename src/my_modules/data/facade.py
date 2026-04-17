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

