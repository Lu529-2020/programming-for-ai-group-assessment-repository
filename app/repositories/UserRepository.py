import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.User import User


# =========================================================
# 1. UserRepository
# =========================================================
class UserRepository(BaseRepository):
    TABLE_NAME = "users"
    # 注意：我们在表结构中其实没有 email 字段，只有 username。
    # 如果你之后给 users 增加 email 字段，可以在这里加上 "email"。
    ALLOWED_FILTERS = {"id", "username", "password_hash", "role", "created_at", "is_active"}

    def add(self, user: User) -> User:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, created_at, is_active)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    user.username,
                    user.password_hash,
                    user.role,
                    user.created_at,
                    1 if user.is_active else 0,
                ),
            )
            self.conn.commit()
            user.id = cursor.lastrowid
            return user
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (User.add): {e}")

    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, username, password_hash, role, created_at, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (user_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return User(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                role=row[3],
                created_at=row[4],
                is_active=bool(row[5]),
                full_name="",  # Person 的字段这里简化不使用
                email=None,
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (User.get_by_id): {e}")

    # 通用查询：find_one / find_all
    def find_one(self, **filters) -> Optional[User]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, username, password_hash, role, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return User(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                role=row[3],
                created_at=row[4],
                is_active=bool(row[5]),
                full_name="",
                email=None,
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (User.find_one): {e}")

    def find_all(self, **filters) -> List[User]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, username, password_hash, role, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=row[3],
                    created_at=row[4],
                    is_active=bool(row[5]),
                    full_name="",
                    email=None,
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (User.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[User]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, username, password_hash, role, created_at, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, username, password_hash, role, created_at, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=row[3],
                    created_at=row[4],
                    is_active=bool(row[5]),
                    full_name="",
                    email=None,
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (User.list_all): {e}")

    def update(self, user: User) -> None:
        if user.id is None:
            raise ValueError("User must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET username = ?, password_hash = ?, role = ?, created_at = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    user.username,
                    user.password_hash,
                    user.role,
                    user.created_at,
                    1 if user.is_active else 0,
                    user.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (User.update): {e}")