import sqlite3
from typing import List, Optional, Dict, Any


class BaseRepository:
    """
    所有 Repository 的父类，封装：
    - 逻辑删除 soft_delete
    - 物理删除 hard_delete
    - 通用 WHERE 过滤构造 _build_where_clause
    """

    TABLE_NAME: str = ""
    ALLOWED_FILTERS: set[str] = set()

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def soft_delete(self, record_id: int) -> None:
        """
        逻辑删除：is_active = 0
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE {self.TABLE_NAME} SET is_active = 0 WHERE id = ?;",
                (record_id,),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database soft_delete failed ({self.TABLE_NAME}): {e}")

    def hard_delete(self, record_id: int) -> None:
        """
        物理删除：DELETE
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE id = ?;",
                (record_id,),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database hard_delete failed ({self.TABLE_NAME}): {e}")

    def _build_where_clause(
        self,
        filters: Dict[str, Any],
        add_default_is_active: bool = True,
    ) -> (str, List[Any]):
        """
        动态生成 WHERE 子句。过滤不支持的字段会抛异常。
        """
        try:
            filters = dict(filters)  # 拷贝内部安全处理

            if (
                add_default_is_active
                and "is_active" in self.ALLOWED_FILTERS
                and "is_active" not in filters
            ):
                filters["is_active"] = 1

            conditions: List[str] = []
            params: List[Any] = []

            for field, value in filters.items():
                if field not in self.ALLOWED_FILTERS:
                    raise ValueError(f"字段 {field} 不允许过滤（表 {self.TABLE_NAME}）")
                conditions.append(f"{field} = ?")
                params.append(value)

            where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""

            return where_sql, params

        except Exception as e:
            raise RuntimeError(f"Build where clause failed ({self.TABLE_NAME}): {e}")