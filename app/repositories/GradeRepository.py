import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.Grade import Grade


# =========================================================
# 8. GradeRepository
# =========================================================
class GradeRepository(BaseRepository):
    TABLE_NAME = "grades"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "assessment_name",
        "grade",
        "is_active",
    }

    def add(self, grade: Grade) -> Grade:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO grades (
                    student_id, module_id, assessment_name, grade, is_active
                )
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    grade.student_id,
                    grade.module_id,
                    grade.assessment_name,
                    grade.grade,
                    1 if grade.is_active else 0,
                ),
            )
            self.conn.commit()
            grade.id = cursor.lastrowid
            return grade
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (Grade.add): {e}")

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, student_id, module_id, assessment_name, grade, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (grade_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Grade(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                assessment_name=row[3],
                grade=row[4],
                is_active=bool(row[5]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (Grade.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[Grade]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, assessment_name, grade, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return Grade(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                assessment_name=row[3],
                grade=row[4],
                is_active=bool(row[5]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (Grade.find_one): {e}")

    def find_all(self, **filters) -> List[Grade]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, assessment_name, grade, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                Grade(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    assessment_name=row[3],
                    grade=row[4],
                    is_active=bool(row[5]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (Grade.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[Grade]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, assessment_name, grade, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, assessment_name, grade, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                Grade(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    assessment_name=row[3],
                    grade=row[4],
                    is_active=bool(row[5]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (Grade.list_all): {e}")

    def update(self, grade: Grade) -> None:
        if grade.id is None:
            raise ValueError("Grade must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, assessment_name = ?, grade = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    grade.student_id,
                    grade.module_id,
                    grade.assessment_name,
                    grade.grade,
                    1 if grade.is_active else 0,
                    grade.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (Grade.update): {e}")