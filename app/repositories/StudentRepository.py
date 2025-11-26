import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.Student import Student


# =========================================================
# 2. StudentRepository
# =========================================================
class StudentRepository(BaseRepository):
    TABLE_NAME = "students"
    ALLOWED_FILTERS = {
        "id",
        "student_number",
        "full_name",
        "email",
        "course_name",
        "year_of_study",
        "is_active",
    }

    def add(self, student: Student) -> Student:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO students (
                    student_number, full_name, email, course_name, year_of_study, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    student.student_number,
                    student.full_name,
                    student.email,
                    student.course_name,
                    student.year_of_study,
                    1 if student.is_active else 0,
                ),
            )
            self.conn.commit()
            student.id = cursor.lastrowid
            return student
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (Student.add): {e}")

    def get_by_id(self, student_id: int) -> Optional[Student]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, student_number, full_name, email, course_name, year_of_study, is_active
                FROM students
                WHERE id = ?;
                """,
                (student_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Student(
                id=row[0],
                student_number=row[1],
                full_name=row[2],
                email=row[3],
                course_name=row[4],
                year_of_study=row[5],
                is_active=bool(row[6]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (Student.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[Student]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_number, full_name, email, course_name, year_of_study, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return Student(
                id=row[0],
                student_number=row[1],
                full_name=row[2],
                email=row[3],
                course_name=row[4],
                year_of_study=row[5],
                is_active=bool(row[6]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (Student.find_one): {e}")

    def find_all(self, **filters) -> List[Student]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_number, full_name, email, course_name, year_of_study, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                Student(
                    id=row[0],
                    student_number=row[1],
                    full_name=row[2],
                    email=row[3],
                    course_name=row[4],
                    year_of_study=row[5],
                    is_active=bool(row[6]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (Student.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[Student]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    """
                    SELECT id, student_number, full_name, email, course_name, year_of_study, is_active
                    FROM students;
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT id, student_number, full_name, email, course_name, year_of_study, is_active
                    FROM students
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                Student(
                    id=row[0],
                    student_number=row[1],
                    full_name=row[2],
                    email=row[3],
                    course_name=row[4],
                    year_of_study=row[5],
                    is_active=bool(row[6]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (Student.list_all): {e}")

    def update(self, student: Student) -> None:
        if student.id is None:
            raise ValueError("Student must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE students
                SET student_number = ?, full_name = ?, email = ?, course_name = ?,
                    year_of_study = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    student.student_number,
                    student.full_name,
                    student.email,
                    student.course_name,
                    student.year_of_study,
                    1 if student.is_active else 0,
                    student.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (Student.update): {e}")