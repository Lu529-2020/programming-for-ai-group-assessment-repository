# tests/test_repositories/test_UserRepository.py
import os
import sqlite3

import pytest

from app.repositories.UserRepository import UserRepository

# 运行本测试文件的指令：pytest -vv tests/test_repositories/test_UserRepository.py

@pytest.fixture
def conn():
    """
    打开测试数据库连接。

    默认使用项目根目录下的 db_test.sqlite3：
      /your/project/root/db_test.sqlite3

    如果你目前只有 db_dev.sqlite3，可以把 db_test.sqlite3 改成 db_dev.sqlite3。
    """
    # 找到项目根目录（tests 的上上级目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "db_test.sqlite3")  # 或改成 "db_dev.sqlite3"

    assert os.path.exists(db_path), f"Database file not found: {db_path}"

    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def test_find_user_by_username_and_password_success(conn):
    """
    场景：用户名和密码都正确，应该能查到对应用户。

    依赖数据库中已存在的数据：
        username = 'admin'
        password_hash = 'hashed_admin_password'
        role = 'admin'
    """
    repo = UserRepository(conn)

    user = repo.find_one(username="admin", password_hash="hashed_admin_password")

    # 断言 + 清晰错误信息
    assert user is not None, "Expected a User object for valid credentials, but got None"
    assert user.username == "admin", (
        f"Expected username 'admin', but got '{user.username}'"
    )
    assert user.password_hash == "hashed_admin_password", (
        f"Expected password_hash 'hashed_admin_password', "
        f"but got '{user.password_hash}'"
    )
    assert user.role == "admin", f"Expected role 'admin', but got '{user.role}'"
    assert user.is_active is True, "Expected user.is_active to be True"


def test_find_user_by_username_and_password_wrong_password(conn):
    """
    场景：用户名正确但密码错误，应该查不到用户（返回 None）。
    """
    repo = UserRepository(conn)

    user = repo.find_one(username="admin", password_hash="wrong_password")

    # 如果返回了用户，说明查找逻辑有问题
    assert user is None, (
        "Expected None for invalid password, "
        f"but got User: {getattr(user, 'username', None)!r}"
    )


def test_find_user_by_username_and_password_unknown_username(conn):
    """
    场景：用户名不存在，应该查不到用户（返回 None）。
    """
    repo = UserRepository(conn)

    user = repo.find_one(username="not_exist_user", password_hash="whatever")

    assert user is None, (
        "Expected None for unknown username, "
        f"but got User: {getattr(user, 'username', None)!r}"
    )
