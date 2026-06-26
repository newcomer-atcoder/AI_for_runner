import pytest
from pathlib import Path

# 関数ごとに独立した一時 DB パスを返す。
# tmp_path は pytest 標準フィクスチャ（テスト後に自動削除される）。
@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"
