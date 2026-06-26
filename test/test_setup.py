from src.my_modules.database.setup import DBSetUp
from src.my_modules.database import setup
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, create_engine

#モック作成
class MocBase(DeclarativeBase):
    pass

class MocUser(MocBase):
    __tablename__ = "moc_table"

    name : Mapped[str] = mapped_column(String, primary_key=True)

class MocUser2(MocBase):
    __tablename__ = "moc_table2"

    name : Mapped[str] = mapped_column(String, primary_key=True)

def test_setUp_Done(monkeypatch, tmp_path):
    no_db  = tmp_path / "empty.db"   # テーブル無し → True 期待
    ready  = tmp_path / "ready.db"   # 2テーブル作成済み → False 期待

    #準備: ready.db に MocUser / MocUser2 の2テーブルを作成（= TABLES(2)相当）
    engine = create_engine(
        url=f"sqlite:///{ready}",
        echo=True
    )
    MocBase.metadata.create_all(engine) # 毎回まっさらなので無条件に作成

    #1.DBがない時(True) / 2.DBが既にある時(False)
    monkeypatch.setattr(setup, "Base", MocBase)
    for moc_db, exp in zip([no_db, ready], [True, False]):
        monkeypatch.setattr(setup, "DB_PATH", moc_db)
        db = DBSetUp()
        assert db.setUp_Done() == exp
