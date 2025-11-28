import os
from app import create_app
from app.api.routes import _get_db_path


def test_get_db_path_prefers_env(monkeypatch, tmp_path):
    """
    DATABASE 环境变量存在时，应该优先使用它并解析 sqlite:/// 前缀。
    """
    custom = tmp_path / "custom.sqlite3"
    custom.write_text("")  # 创建空文件以确保路径存在

    monkeypatch.setenv("DATABASE", f"sqlite:///{custom}")
    app = create_app()
    with app.app_context():
        path = _get_db_path()

    assert path == str(custom)
    monkeypatch.delenv("DATABASE", raising=False)


def test_get_db_path_falls_back_to_dev(monkeypatch):
    """
    没有 DATABASE 时，应回退到项目根的 db_dev.sqlite3（预置开发库）。
    """
    monkeypatch.delenv("DATABASE", raising=False)
    app = create_app()
    with app.app_context():
        path = _get_db_path()

    assert path.endswith("db_dev.sqlite3"), "Fallback should point to db_dev.sqlite3"
    assert os.path.exists(path), f"Expected fallback DB to exist at {path}"
