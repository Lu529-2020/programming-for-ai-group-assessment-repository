import sqlite3
from typing import List, Optional
from ..repositories.BaseRepository import BaseRepository
from ..models.Alert import Alert


# =========================================================
# 9. AlertRepository
# =========================================================
class AlertRepository(BaseRepository):
    TABLE_NAME = "alerts"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "week_number",
        "reason",
        "created_at",
        "resolved",
        "is_active",
    }

    def add(self, alert: Alert) -> Alert:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts (
                    student_id, module_id, week_number,
                    reason, created_at, resolved, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    alert.student_id,
                    alert.module_id,
                    alert.week_number,
                    alert.reason,
                    alert.created_at,
                    1 if alert.resolved else 0,
                    1 if alert.is_active else 0,
                ),
            )
            self.conn.commit()
            alert.id = cursor.lastrowid
            return alert
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (AlertRepository.add): {e}")

    def get_by_id(self, alert_id: int) -> Optional[Alert]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, student_id, module_id, week_number,
                       reason, created_at, resolved, is_active
                FROM alerts
                WHERE id = ?;
                """,
                (alert_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Alert(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                reason=row[4],
                created_at=row[5],
                resolved=bool(row[6]),
                is_active=bool(row[7]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (AlertRepository.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[Alert]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       reason, created_at, resolved, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return Alert(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                reason=row[4],
                created_at=row[5],
                resolved=bool(row[6]),
                is_active=bool(row[7]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed: {e}")

    def find_all(self, **filters) -> List[Alert]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       reason, created_at, resolved, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                Alert(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    reason=row[4],
                    created_at=row[5],
                    resolved=bool(row[6]),
                    is_active=bool(row[7]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed: {e}")

    def list_all(self, include_inactive: bool = False) -> List[Alert]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    """
                    SELECT id, student_id, module_id, week_number,
                           reason, created_at, resolved, is_active
                    FROM alerts;
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT id, student_id, module_id, week_number,
                           reason, created_at, resolved, is_active
                    FROM alerts
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                Alert(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    reason=row[4],
                    created_at=row[5],
                    resolved=bool(row[6]),
                    is_active=bool(row[7]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed: {e}")

    def update(self, alert: Alert) -> None:
        if alert.id is None:
            raise ValueError("Alert must have an id to be updated.")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE alerts
                SET student_id = ?, module_id = ?, week_number = ?,
                    reason = ?, created_at = ?, resolved = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    alert.student_id,
                    alert.module_id,
                    alert.week_number,
                    alert.reason,
                    alert.created_at,
                    1 if alert.resolved else 0,
                    1 if alert.is_active else 0,
                    alert.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (AlertRepository.update): {e}")