from src.my_modules.database.setup import DBSetUp
from src.my_modules.database import setup
from pathlib import Path
import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, create_engine

#モック作成
MOC_DB_PATH1 = Path(__file__).parent/"testDB"/"test1.db"
MOC_DB_PATH2 = Path(__file__).parent/"testDB"/"test2.db"
MOC_DB_PATH3 = Path(__file__).parent/"testDB"/"test3.db"
class MocBase(DeclarativeBase):
    pass

class MocUser(MocBase):
    __tablename__ = "moc_table"

    name : Mapped[str] = mapped_column(String, primary_key=True)

class MocUser2(MocBase):
    __tablename__ = "moc_table2"

    name : Mapped[str] = mapped_column(String, primary_key=True)

def test_setUp_Done(monkeypatch):
    #準備
    engine = create_engine(
        url=f"sqlite:///{MOC_DB_PATH2}",
        echo=True
    )
    MocBase.metadata.create_all(engine)

    #1.DBがない時
    #2.DBが既にある時
    monkeypatch.setattr(setup, "Base", MocBase)
    for moc_db, exp in zip([MOC_DB_PATH1, MOC_DB_PATH2], [True, False]):
        monkeypatch.setattr(setup, "DB_PATH", moc_db)
        db = DBSetUp()
        result = db.setUp_Done()
        assert result == exp
