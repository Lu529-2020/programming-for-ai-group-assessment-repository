import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.StressEvent import StressEvent


# =========================================================
# 10. StressEventRepository
# =========================================================
class StressEventRepository(BaseRepository):
    TABLE_NAME = "stress_events"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "survey_response_id",
        "week_number",
        "stress_level",
        "cause_category",
        "description",
        "source",
        "created_at",
        "is_active",
    }

    def add(self, event: StressEvent) -> StressEvent:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO stress_events (
                    student_id, module_id, survey_response_id, week_number,
                    stress_level, cause_category, description, source,
                    created_at, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event.student_id,
                    event.module_id,
                    event.survey_response_id,
                    event.week_number,
                    event.stress_level,
                    event.cause_category,
                    event.description,
                    event.source,
                    event.created_at,
                    1 if event.is_active else 0,
                ),
            )
            self.conn.commit()
            event.id = cursor.lastrowid
            return event
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (StressEvent.add): {e}")

    def get_by_id(self, event_id: int) -> Optional[StressEvent]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, student_id, module_id, survey_response_id,
                       week_number, stress_level, cause_category, description,
                       source, created_at, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (event_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return StressEvent(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                survey_response_id=row[3],
                week_number=row[4],
                stress_level=row[5],
                cause_category=row[6],
                description=row[7],
                source=row[8],
                created_at=row[9],
                is_active=bool(row[10]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (StressEvent.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[StressEvent]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, survey_response_id,
                       week_number, stress_level, cause_category, description,
                       source, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return StressEvent(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                survey_response_id=row[3],
                week_number=row[4],
                stress_level=row[5],
                cause_category=row[6],
                description=row[7],
                source=row[8],
                created_at=row[9],
                is_active=bool(row[10]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (StressEvent.find_one): {e}")

    def find_all(self, **filters) -> List[StressEvent]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, survey_response_id,
                       week_number, stress_level, cause_category, description,
                       source, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                StressEvent(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    survey_response_id=row[3],
                    week_number=row[4],
                    stress_level=row[5],
                    cause_category=row[6],
                    description=row[7],
                    source=row[8],
                    created_at=row[9],
                    is_active=bool(row[10]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (StressEvent.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[StressEvent]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, survey_response_id,
                           week_number, stress_level, cause_category, description,
                           source, created_at, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, survey_response_id,
                           week_number, stress_level, cause_category, description,
                           source, created_at, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                StressEvent(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    survey_response_id=row[3],
                    week_number=row[4],
                    stress_level=row[5],
                    cause_category=row[6],
                    description=row[7],
                    source=row[8],
                    created_at=row[9],
                    is_active=bool(row[10]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (StressEvent.list_all): {e}")

    def update(self, event: StressEvent) -> None:
        if event.id is None:
            raise ValueError("StressEvent must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, survey_response_id = ?, week_number = ?,
                    stress_level = ?, cause_category = ?, description = ?, source = ?,
                    created_at = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    event.student_id,
                    event.module_id,
                    event.survey_response_id,
                    event.week_number,
                    event.stress_level,
                    event.cause_category,
                    event.description,
                    event.source,
                    event.created_at,
                    1 if event.is_active else 0,
                    event.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (StressEvent.update): {e}")