import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.AttendanceRecord import AttendanceRecord


# =========================================================
# 5. AttendanceRecordRepository
# =========================================================
class AttendanceRecordRepository(BaseRepository):
    TABLE_NAME = "attendance_records"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "week_number",
        "attended_sessions",
        "total_sessions",
        "attendance_rate",
        "is_active",
    }

    def add(self, record: AttendanceRecord) -> AttendanceRecord:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO attendance_records (
                    student_id, module_id, week_number,
                    attended_sessions, total_sessions, attendance_rate, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.student_id,
                    record.module_id,
                    record.week_number,
                    record.attended_sessions,
                    record.total_sessions,
                    record.attendance_rate,
                    1 if record.is_active else 0,
                ),
            )
            self.conn.commit()
            record.id = cursor.lastrowid
            return record
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (Attendance.add): {e}")

    def get_by_id(self, record_id: int) -> Optional[AttendanceRecord]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, student_id, module_id, week_number,
                       attended_sessions, total_sessions, attendance_rate, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (record_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return AttendanceRecord(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                attended_sessions=row[4],
                total_sessions=row[5],
                attendance_rate=row[6],
                is_active=bool(row[7]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (Attendance.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[AttendanceRecord]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       attended_sessions, total_sessions, attendance_rate, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return AttendanceRecord(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                attended_sessions=row[4],
                total_sessions=row[5],
                attendance_rate=row[6],
                is_active=bool(row[7]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed: {e}")

    def find_all(self, **filters) -> List[AttendanceRecord]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       attended_sessions, total_sessions, attendance_rate, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                AttendanceRecord(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    attended_sessions=row[4],
                    total_sessions=row[5],
                    attendance_rate=row[6],
                    is_active=bool(row[7]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed: {e}")

    def list_all(self, include_inactive: bool = False) -> List[AttendanceRecord]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, week_number,
                           attended_sessions, total_sessions, attendance_rate, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, week_number,
                           attended_sessions, total_sessions, attendance_rate, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                AttendanceRecord(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    attended_sessions=row[4],
                    total_sessions=row[5],
                    attendance_rate=row[6],
                    is_active=bool(row[7]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed: {e}")

    def update(self, record: AttendanceRecord) -> None:
        if record.id is None:
            raise ValueError("AttendanceRecord must have an id to be updated.")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, week_number = ?,
                    attended_sessions = ?, total_sessions = ?, attendance_rate = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    record.student_id,
                    record.module_id,
                    record.week_number,
                    record.attended_sessions,
                    record.total_sessions,
                    record.attendance_rate,
                    1 if record.is_active else 0,
                    record.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (Attendance.update): {e}")