from src.my_modules.db.settings import DBSetUp
from src.my_modules.db import settings
from pathlib import Path
import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, inspect

#モック作成
MOC_DB_PATH1 = Path(__file__).parent/"test1.db"
MOC_DB_PATH2 = Path(__file__).parent/"test2.db"
MOC_DB_PATH3 = Path(__file__).parent/"test3.db"
class MocBase(DeclarativeBase):
    pass

class MocUser(MocBase):
    __tablename__ = "moc_users"

    name : Mapped[str] = mapped_column(String, primary_key=True)



def test_createTable(monkeypatch):
    monkeypatch.setattr(settings, "DB_PATH", MOC_DB_PATH1) #test直下に変更
    monkeypatch.setattr(settings, "Base", MocBase)
    db = DBSetUp()
    db.createTable()

    #DBとテーブルを作成できたか確認
    assert MOC_DB_PATH1.exists()

    table = inspect(db.engine).get_table_names()
    assert table[0] == "moc_users"


def test_check_db_and_table_exists(monkeypatch):
    #C0
    #テーブルの登録が0件の場合
    monkeypatch.setattr(settings, "DB_PATH", MOC_DB_PATH2) #test直下に変更
    db = DBSetUp()
    print(f"DBの場所 = {settings.DB_PATH}")
    assert not db.check_table_exists()

    #テーブルの登録が1件以上の場合
    monkeypatch.setattr(settings, "DB_PATH", MOC_DB_PATH1) #test直下に変更
    db = DBSetUp()
    print(f"DBの場所 = {settings.DB_PATH}")
    assert db.check_table_exists()


def test_setupDB(monkeypatch):
    #dbファイルがいつ自動生成されるか確認
    monkeypatch.setattr(settings, "DB_PATH", MOC_DB_PATH3) #test直下に変更
    db = DBSetUp()

    #create_engine
    print(f"DBの場所 = {settings.DB_PATH}")
    assert not MOC_DB_PATH3.exists()

    #inspectでテーブルを参照する際に、DBが自動生成される
    table = inspect(db.engine).get_table_names()
    assert MOC_DB_PATH3.exists()