import sqlite3
import os


"""
这个方法用于建立数据库连接，测试环境使用test，开发环境使用dev
"""


def get_conn():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # dev_db_path = os.path.join(base_dir, "db_dev.sqlite3")
    test_db_path = os.path.join(base_dir, "db_test.sqlite3")
    conn = sqlite3.connect(test_db_path)
    return conn





