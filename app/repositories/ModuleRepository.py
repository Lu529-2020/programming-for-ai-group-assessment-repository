import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.Module import Module


# =========================================================
# 3. ModuleRepository
# =========================================================
class ModuleRepository(BaseRepository):
    TABLE_NAME = "modules"
    ALLOWED_FILTERS = {"id", "module_code", "module_title", "credit", "academic_year", "is_active"}

    def add(self, module: Module) -> Module:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO modules (module_code, module_title, credit, academic_year, is_active)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    module.module_code,
                    module.module_title,
                    module.credit,
                    module.academic_year,
                    1 if module.is_active else 0,
                ),
            )
            self.conn.commit()
            module.id = cursor.lastrowid
            return module
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (Module.add): {e}")

    def get_by_id(self, module_id: int) -> Optional[Module]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, module_code, module_title, credit, academic_year, is_active
                FROM modules
                WHERE id = ?;
                """,
                (module_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Module(
                id=row[0],
                module_code=row[1],
                module_title=row[2],
                credit=row[3],
                academic_year=row[4],
                is_active=bool(row[5]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (Module.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[Module]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, module_code, module_title, credit, academic_year, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return Module(
                id=row[0],
                module_code=row[1],
                module_title=row[2],
                credit=row[3],
                academic_year=row[4],
                is_active=bool(row[5]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (Module.find_one): {e}")

    def find_all(self, **filters) -> List[Module]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, module_code, module_title, credit, academic_year, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                Module(
                    id=row[0],
                    module_code=row[1],
                    module_title=row[2],
                    credit=row[3],
                    academic_year=row[4],
                    is_active=bool(row[5]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (Module.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[Module]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    """
                    SELECT id, module_code, module_title, credit, academic_year, is_active
                    FROM modules;
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT id, module_code, module_title, credit, academic_year, is_active
                    FROM modules
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                Module(
                    id=row[0],
                    module_code=row[1],
                    module_title=row[2],
                    credit=row[3],
                    academic_year=row[4],
                    is_active=bool(row[5]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (Module.list_all): {e}")

    def update(self, module: Module) -> None:
        if module.id is None:
            raise ValueError("Module must have an id to be updated.")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET module_code = ?, module_title = ?, credit = ?, academic_year = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    module.module_code,
                    module.module_title,
                    module.credit,
                    module.academic_year,
                    1 if module.is_active else 0,
                    module.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (Module.update): {e}")