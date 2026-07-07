from pathlib import Path
from sqlalchemy import create_engine, inspect
from .models import Base
import sys

#定数
NO_DB_OR_TABLES = False

#DBの絶対パス指定
dbname = "app.db"
if getattr(sys, 'frozen', False):
    #exe化(PyInstaller)時: exeファイルと同じフォルダにapp.dbを作る
    BASE_DIR = Path(sys.executable).parent
else:
    #開発時: 従来どおり src/app.db
    BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR/dbname

#セットアップすべきテーブルの数
TABLES = 2

class DBSetUp:
    def __init__(self):
        #エンジン作成時点で.dbファイルが自動作成されるため、ファイルの存在チェックが不要
        engine = create_engine(
            url=f"sqlite:///{DB_PATH}",
        )

        self.engine = engine


    def setUp_Done(self):
        #テーブルの有無をチェック
        #DBファイルがない場合はここで自動生成される
        tables = inspect(self.engine).get_table_names()
        
        setupflg = len(tables) < TABLES
        if setupflg:
            print("初回セットアップ実行")
            Base.metadata.create_all(self.engine)
        else:
            print("設定済みのデータベースがありました")
        return setupflg
