import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.Enrolment import Enrolment


# =========================================================
# 4. EnrolmentRepository
# =========================================================
class EnrolmentRepository(BaseRepository):
    TABLE_NAME = "enrolments"
    ALLOWED_FILTERS = {"id", "student_id", "module_id", "enrol_date", "is_active"}

    def add(self, enrolment: Enrolment) -> Enrolment:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO enrolments (student_id, module_id, enrol_date, is_active)
                VALUES (?, ?, ?, ?);
                """,
                (
                    enrolment.student_id,
                    enrolment.module_id,
                    enrolment.enrol_date,
                    1 if enrolment.is_active else 0,
                ),
            )
            self.conn.commit()
            enrolment.id = cursor.lastrowid
            return enrolment
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (Enrolment.add): {e}")

    def get_by_id(self, enrolment_id: int) -> Optional[Enrolment]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, student_id, module_id, enrol_date, is_active
                FROM enrolments
                WHERE id = ?;
                """,
                (enrolment_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Enrolment(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                enrol_date=row[3],
                is_active=bool(row[4]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (Enrolment.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[Enrolment]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, enrol_date, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return Enrolment(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                enrol_date=row[3],
                is_active=bool(row[4]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed: {e}")

    def find_all(self, **filters) -> List[Enrolment]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, enrol_date, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                Enrolment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    enrol_date=row[3],
                    is_active=bool(row[4]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed: {e}")

    def list_all(self, include_inactive: bool = False) -> List[Enrolment]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, enrol_date, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, enrol_date, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                Enrolment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    enrol_date=row[3],
                    is_active=bool(row[4]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed: {e}")

    def update(self, enrolment: Enrolment) -> None:
        if enrolment.id is None:
            raise ValueError("Enrolment must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, enrol_date = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    enrolment.student_id,
                    enrolment.module_id,
                    enrolment.enrol_date,
                    1 if enrolment.is_active else 0,
                    enrolment.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (Enrolment.update): {e}")