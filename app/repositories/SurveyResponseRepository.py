import sqlite3
from typing import List, Optional, Dict, Any
from ..repositories.BaseRepository import BaseRepository
from ..models.SurveyResponse import SurveyResponse


# =========================================================
# 7. SurveyResponseRepository
# =========================================================
class SurveyResponseRepository(BaseRepository):
    TABLE_NAME = "survey_responses"
    ALLOWED_FILTERS = {
        "id",
        "student_id",
        "module_id",
        "week_number",
        "stress_level",
        "hours_slept",
        "mood_comment",
        "created_at",
        "is_active",
    }

    def add(self, resp: SurveyResponse) -> SurveyResponse:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO survey_responses (
                    student_id, module_id, week_number,
                    stress_level, hours_slept, mood_comment, created_at, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    resp.student_id,
                    resp.module_id,
                    resp.week_number,
                    resp.stress_level,
                    resp.hours_slept,
                    resp.mood_comment,
                    resp.created_at,
                    1 if resp.is_active else 0,
                ),
            )
            self.conn.commit()
            resp.id = cursor.lastrowid
            return resp
        except sqlite3.Error as e:
            raise RuntimeError(f"Database insert failed (SurveyResponse.add): {e}")

    def get_by_id(self, resp_id: int) -> Optional[SurveyResponse]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, student_id, module_id, week_number,
                       stress_level, hours_slept, mood_comment, created_at, is_active
                FROM {self.TABLE_NAME}
                WHERE id = ?;
                """,
                (resp_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return SurveyResponse(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                stress_level=row[4],
                hours_slept=row[5],
                mood_comment=row[6],
                created_at=row[7],
                is_active=bool(row[8]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database fetch failed (SurveyResponse.get_by_id): {e}")

    def find_one(self, **filters) -> Optional[SurveyResponse]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       stress_level, hours_slept, mood_comment, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql}
                LIMIT 1;
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return SurveyResponse(
                id=row[0],
                student_id=row[1],
                module_id=row[2],
                week_number=row[3],
                stress_level=row[4],
                hours_slept=row[5],
                mood_comment=row[6],
                created_at=row[7],
                is_active=bool(row[8]),
            )
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_one failed (SurveyResponse.find_one): {e}")

    def find_all(self, **filters) -> List[SurveyResponse]:
        try:
            where_sql, params = self._build_where_clause(filters, add_default_is_active=True)
            sql = f"""
                SELECT id, student_id, module_id, week_number,
                       stress_level, hours_slept, mood_comment, created_at, is_active
                FROM {self.TABLE_NAME}
                {where_sql};
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                SurveyResponse(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    stress_level=row[4],
                    hours_slept=row[5],
                    mood_comment=row[6],
                    created_at=row[7],
                    is_active=bool(row[8]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database find_all failed (SurveyResponse.find_all): {e}")

    def list_all(self, include_inactive: bool = False) -> List[SurveyResponse]:
        try:
            cursor = self.conn.cursor()
            if include_inactive:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, week_number,
                           stress_level, hours_slept, mood_comment, created_at, is_active
                    FROM {self.TABLE_NAME};
                    """
                )
            else:
                cursor.execute(
                    f"""
                    SELECT id, student_id, module_id, week_number,
                           stress_level, hours_slept, mood_comment, created_at, is_active
                    FROM {self.TABLE_NAME}
                    WHERE is_active = 1;
                    """
                )
            rows = cursor.fetchall()
            return [
                SurveyResponse(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    week_number=row[3],
                    stress_level=row[4],
                    hours_slept=row[5],
                    mood_comment=row[6],
                    created_at=row[7],
                    is_active=bool(row[8]),
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database list_all failed (SurveyResponse.list_all): {e}")

    def update(self, resp: SurveyResponse) -> None:
        if resp.id is None:
            raise ValueError("SurveyResponse must have an id to be updated.")
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET student_id = ?, module_id = ?, week_number = ?,
                    stress_level = ?, hours_slept = ?, mood_comment = ?, created_at = ?, is_active = ?
                WHERE id = ?;
                """,
                (
                    resp.student_id,
                    resp.module_id,
                    resp.week_number,
                    resp.stress_level,
                    resp.hours_slept,
                    resp.mood_comment,
                    resp.created_at,
                    1 if resp.is_active else 0,
                    resp.id,
                ),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database update failed (SurveyResponse.update): {e}")