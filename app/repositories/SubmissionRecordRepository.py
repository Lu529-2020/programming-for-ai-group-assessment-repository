import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.SubmissionRecord import SubmissionRecord


# =========================================================
# 6. SubmissionRecordRepository
# =========================================================
class SubmissionRecordRepository(BaseRepository):
    TABLE_NAME = "submission_records"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "assessment_name",
        "due_date",
        "submitted_date",
        "is_submitted",
        "is_late",
        "is_active",
    }

    def add(self, record: SubmissionRecord) -> SubmissionRecord:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO submission_records (
                    student_id, module_id, assessment_name,
                    due_date, submitted_date, is_submitted, is_late, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.student_id,
                    record.module_id,
                    record.assessment_name,
                    record.due_date,
                    record.submitted_date,
                    1 if record.is_submitted else 0,
                    1 if record.is_late else 0,
                    1 if record.is_active else 0,
                ),
            )
            self.conn.commit()
            record.id = cursor.lastrowid
            return record
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (SubmissionRecord.add): {e}")

    def get_by_id(self, record_id: int) -> Optional[SubmissionRecord]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, student_id, module_id, assessment_name,
                       due_date, submitted_date, is_submitted, is_late, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (record_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return SubmissionRecord(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                assessment_name=row[3],
                due_date=row[4],
                submitted_date=row[5],
                is_submitted=bool(row[6]),
                is_late=bool(row[7]),
                is_active=bool(row[8]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (SubmissionRecord.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[SubmissionRecord]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, assessment_name,
                       due_date, submitted_date, is_submitted, is_late, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return SubmissionRecord(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                assessment_name=row[3],
                due_date=row[4],
                submitted_date=row[5],
                is_submitted=bool(row[6]),
                is_late=bool(row[7]),
                is_active=bool(row[8]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (SubmissionRecord.find_one): {e}")

    def find_all(self, **filters) -> List[SubmissionRecord]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, assessment_name,
                       due_date, submitted_date, is_submitted, is_late, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                SubmissionRecord(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    assessment_name=row[3],
                    due_date=row[4],
                    submitted_date=row[5],
                    is_submitted=bool(row[6]),
                    is_late=bool(row[7]),
                    is_active=bool(row[8]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (SubmissionRecord.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[SubmissionRecord]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, assessment_name,
                           due_date, submitted_date, is_submitted, is_late, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, assessment_name,
                           due_date, submitted_date, is_submitted, is_late, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                SubmissionRecord(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    assessment_name=row[3],
                    due_date=row[4],
                    submitted_date=row[5],
                    is_submitted=bool(row[6]),
                    is_late=bool(row[7]),
                    is_active=bool(row[8]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (SubmissionRecord.list_all): {e}")

    def update(self, record: SubmissionRecord) -> None:
        if record.id is None:
            raise ValueError("SubmissionRecord must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, assessment_name = ?,
                    due_date = ?, submitted_date = ?, is_submitted = ?, is_late = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    record.student_id,
                    record.module_id,
                    record.assessment_name,
                    record.due_date,
                    record.submitted_date,
                    1 if record.is_submitted else 0,
                    1 if record.is_late else 0,
                    1 if record.is_active else 0,
                    record.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (SubmissionRecord.update): {e}")