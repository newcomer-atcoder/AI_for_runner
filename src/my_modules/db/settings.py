from pathlib import Path
from sqlalchemy import create_engine, inspect
from .dbmodels import Base

#定数
NO_DB_OR_TABLES = False

#DBの絶対パス指定
dbname = "app.db"
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR/dbname

class DBSetUp:
    def __init__(self):
        #エンジン作成時点で.dbファイルが自動作成されるため、ファイルの存在チェックが不要
        engine = create_engine(
            url=f"sqlite:///{DB_PATH}",
            echo=True
        )

        self.engine = engine


    def check_table_exists(self) -> bool:
        #テーブルの有無をチェック
        #DBファイルがない場合はここで自動生成される
        tables = inspect(self.engine).get_table_names()
        return tables
    
    def createTable(self):
        Base.metadata.create_all(self.engine)