from typing import List, Optional, Dict, Any
from datetime import datetime

from utils.db_connect_util import get_conn
from app.repositories.AttendanceRecordRepository import AttendanceRecordRepository
from app.repositories.GradeRepository import GradeRepository
from app.repositories.SurveyResponseRepository import SurveyResponseRepository


class AnalysisServiceRepository:
    """
    数据分析服务类（Analysis）。
    - 每个功能块前都有“分割注释”，便于快速定位。
    - 当前已实现：统计学生平均出勤率。
    """

    def __init__(self, conn=None):
        """
        初始化数据库连接与仓储。
        - conn: 可外部注入，方便测试；未提供则使用默认测试库连接。
        """
        self.conn = conn or get_conn()
        self.attendance_repo = AttendanceRecordRepository(self.conn)
        self.survey_repo = SurveyResponseRepository(self.conn)
        self.grade_repo = GradeRepository(self.conn)

    def test(self):
        return "test pass"

    # ------------------------------------------------------------------
    # 功能：统计学生平均出勤率（所有学生）
    # ------------------------------------------------------------------
    def get_students_average_attendance(
        self,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        统计“所有学生”的平均出勤率（attendance_rate 的平均值）。

        参数：
        - module_id：可选，指定课程时只统计该课程的数据；不填则统计全部课程。
        - include_inactive：是否包含 is_active=0 的记录；默认 False 仅看活跃数据。

        返回：
        [
            {"student_id": 1, "average_attendance_rate": 0.75},
            {"student_id": 2, "average_attendance_rate": 0.6},
            ...
        ]
        """
        try:
            cursor = self.conn.cursor()

            # 组装 WHERE 子句（条件可选）
            conditions: List[str] = []
            params: List[Any] = []

            if not include_inactive:
                conditions.append("is_active = 1")

            if module_id is not None:
                conditions.append("module_id = ?")
                params.append(module_id)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # SQL：按 student_id 分组求 AVG(attendance_rate)
            cursor.execute(
                f"""
                SELECT student_id, AVG(attendance_rate) AS avg_attendance
                FROM attendance_records
                {where_clause}
                GROUP BY student_id;
                """,
                params,
            )
            rows = cursor.fetchall()

            return [
                {"student_id": row[0], "average_attendance_rate": row[1]}
                for row in rows
            ]
        except Exception as e:
            raise RuntimeError(f"计算平均出勤率失败: {e}")

    # ------------------------------------------------------------------
    # 功能：统计单个学生的平均出勤率
    # ------------------------------------------------------------------
    def get_student_average_attendance(
        self,
        student_id: int,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> Optional[float]:
        """
        统计“单个学生”的平均出勤率；可选按课程过滤。

        返回：
        - float：该学生的平均出勤率
        - None：如果没有记录
        """
        try:
            cursor = self.conn.cursor()

            conditions = ["student_id = ?"]
            params: List[Any] = [student_id]

            if not include_inactive:
                conditions.append("is_active = 1")

            if module_id is not None:
                conditions.append("module_id = ?")
                params.append(module_id)

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(
                f"""
                SELECT AVG(attendance_rate) AS avg_attendance
                FROM attendance_records
                {where_clause};
                """,
                params,
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            raise RuntimeError(
                f"计算学生 {student_id} 的平均出勤率失败: {e}"
            )

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # 功能：展示学生压力变化曲线（按周列表）
    # ------------------------------------------------------------------
    def get_student_stress_trend(
        self,
        student_id: int,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        获取单个学生的压力曲线（按周升序）。
        参数：
        - student_id：必填
        - module_id：可选，仅限该课程
        - include_inactive：是否包含 is_active=0，默认 False
        返回示例：[{"week_number": 1, "stress_level": 3, "created_at": "..."}]
        """
        try:
            cursor = self.conn.cursor()

            conditions = ["student_id = ?"]
            params: List[Any] = [student_id]

            if not include_inactive:
                conditions.append("is_active = 1")

            if module_id is not None:
                conditions.append("module_id = ?")
                params.append(module_id)

            where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(
                f"""
                SELECT week_number, stress_level, created_at
                FROM survey_responses
                {where_clause}
                ORDER BY week_number ASC;
                """,
                params,
            )
            rows = cursor.fetchall()

            return [
                {
                    "week_number": row[0],
                    "stress_level": row[1],
                    "created_at": row[2],
                }
                for row in rows
            ]
        except Exception as e:
            raise RuntimeError(f"获取学生 {student_id} 的压力变化曲线失败: {e}")

    # ------------------------------------------------------------------
    # 功能：检测连续两周压力 >= threshold 的学生
    # ------------------------------------------------------------------
    def detect_consecutive_high_stress(
        self,
        threshold: int = 4,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        检测“连续两周压力等级都 >= threshold”的情形，返回详细列表。

        参数：
        - threshold：阈值，默认 4。
        - module_id：可选，只检测某门课；不填则按“学生 + 课程”组合分别检测。
        - include_inactive：是否包含 is_active=0 的问卷记录。

        返回（列表，每一条代表一次“连续两周高压”事件）：
        [
            {
                "student_id": 1,
                "module_id": 101,
                "week_start": 2,     # 第一周
                "week_next": 3,      # 第二周（= 第一周 + 1）
                "stress_prev": 4,    # 第一周压力值
                "stress_curr": 5,    # 第二周压力值
            },
            ...
        ]

        处理思路（给初学者）：
        1. 按 student_id、module_id、week_number 排序取出问卷数据。
        2. 对相邻两条记录，若周次连续且两次压力都 >= threshold，则记为一次命中。
        3. module_id 不填时，依然按“学生 + 课程”组合分组，避免跨课程串联周次。
        """
        try:
            cursor = self.conn.cursor()

            conditions = []
            params: List[Any] = []

            if not include_inactive:
                conditions.append("is_active = 1")

            if module_id is not None:
                conditions.append("module_id = ?")
                params.append(module_id)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            cursor.execute(
                f"""
                SELECT student_id, module_id, week_number, stress_level
                FROM survey_responses
                {where_clause}
                ORDER BY student_id ASC, module_id ASC, week_number ASC;
                """,
                params,
            )
            rows = cursor.fetchall()

            results: List[Dict[str, Any]] = []

            prev_student: Optional[int] = None
            prev_module: Optional[int] = None
            prev_week: Optional[int] = None
            prev_stress: Optional[int] = None

            for student_id_val, module_id_val, week_num, stress_val in rows:
                # 当学生或课程发生变化时，重置“前一条”状态
                if (student_id_val != prev_student) or (module_id_val != prev_module):
                    prev_student = student_id_val
                    prev_module = module_id_val
                    prev_week = week_num
                    prev_stress = stress_val
                    continue

                # 判断是否为连续周次且两周压力都 >= threshold
                if (
                    prev_week is not None
                    and week_num == prev_week + 1
                    and prev_stress is not None
                    and prev_stress >= threshold
                    and stress_val >= threshold
                ):
                    results.append(
                        {
                            "student_id": student_id_val,
                            "module_id": module_id_val,
                            "week_start": prev_week,
                            "week_next": week_num,
                            "stress_prev": prev_stress,
                            "stress_curr": stress_val,
                        }
                    )

                # 更新“前一条”状态，继续扫描后续数据
                prev_week = week_num
                prev_stress = stress_val

            return results
        except Exception as e:
            raise RuntimeError(
                f"检测连续高压失败: {e}"
            )

    # ------------------------------------------------------------------
    # 功能：自动创建预警记录（基于连续两周高压）
    # ------------------------------------------------------------------
    def create_high_stress_alerts(
        self,
        threshold: int = 4,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
        clear_old: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        自动生成压力预警（写入 alerts 表）。

        规则：同一学生、同一课程，连续两周 stress_level >= threshold 即视为高压事件。

        参数：
        - threshold：压力阈值，默认 4。
        - module_id：可选，仅对某门课生成；不填则对所有课程分别处理。
        - include_inactive：是否包含 is_active=0 的问卷。
        - clear_old：生成前是否清空旧预警（默认 True，防止重复）。

        返回：已插入的预警记录列表（字典），示例：
        [
            {"student_id": 1, "module_id": 101, "week_number": 4, "reason": "...", "resolved": 0, "created_at": "..."},
            ...
        ]

        实现步骤：
        1) 复用 detect_consecutive_high_stress 找到所有命中事件。
        2) 每个 (student_id, module_id) 只保留“最新”的一条（week_next 最大）。
        3) 视 clear_old 决定是否先删旧 alerts（全表或按 module_id）。
        4) 插入新的预警记录并返回结果。
        """
        try:
            cursor = self.conn.cursor()

            # 步骤 1：先找出所有命中的连续高压事件
            events = self.detect_consecutive_high_stress(
                threshold=threshold,
                module_id=module_id,
                include_inactive=include_inactive,
            )

            # 步骤 2：对每个 (student_id, module_id) 只保留“最新”的一条（week_next 最大）
            latest_by_key: Dict[tuple, Dict[str, Any]] = {}
            for evt in events:
                key = (evt["student_id"], evt["module_id"])
                if key not in latest_by_key or evt["week_next"] > latest_by_key[key]["week_next"]:
                    latest_by_key[key] = evt

            # 如果没有命中，直接返回空列表
            if not latest_by_key:
                return []

            # 步骤 3：根据 clear_old 决定是否清空旧 alerts
            if clear_old:
                if module_id is None:
                    cursor.execute("DELETE FROM alerts;")
                else:
                    cursor.execute("DELETE FROM alerts WHERE module_id = ?;", (module_id,))

            # 步骤 4：插入新预警
            now_ts = datetime.now().isoformat(timespec="seconds")
            to_insert = []
            for evt in latest_by_key.values():
                reason = (
                    f"Stress >= {threshold} in consecutive weeks "
                    f"{evt['week_start']} and {evt['week_next']} "
                    f"(module_id={evt['module_id']})."
                )
                to_insert.append(
                    (
                        evt["student_id"],
                        evt["module_id"],
                        evt["week_next"],  # 记录“第二周”的周次，便于定位最新
                        reason,
                        now_ts,
                        0,  # resolved
                        1,  # is_active
                    )
                )

            cursor.executemany(
                """
                INSERT INTO alerts (student_id, module_id, week_number, reason, created_at, resolved, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                to_insert,
            )
            self.conn.commit()

            # 返回易用的字典列表
            results = []
            for idx, evt in enumerate(latest_by_key.values()):
                results.append(
                    {
                        "student_id": evt["student_id"],
                        "module_id": evt["module_id"],
                        "week_number": evt["week_next"],
                        "reason": to_insert[idx][3],
                        "resolved": 0,
                        "created_at": now_ts,
                    }
                )
            return results
        except Exception as e:
            raise RuntimeError(f"创建预警记录失败: {e}")

    # ------------------------------------------------------------------
    # 功能：对比不同模块的压力与成绩关系
    # ------------------------------------------------------------------
    def compare_stress_grade_by_module(
        self,
        module_ids: Optional[List[int]] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        对比不同模块学生群体的压力与成绩关系，返回均值与简单皮尔逊相关系数。

        返回示例：
        [
            {
                "module_id": 101,
                "average_stress_level": 3.2,
                "average_grade": 75.5,
                "sample_size": 5,          # 联合记录条数（student+module 交集）
                "pearson_corr": 0.42,      # n>=2 时给出相关系数，否则 None
            },
            ...
        ]
        """
        try:
            cursor = self.conn.cursor()

            conditions: List[str] = []
            params: List[Any] = []

            if not include_inactive:
                conditions.append("sr.is_active = 1")
                conditions.append("g.is_active = 1")

            if module_ids:
                placeholders = ",".join(["?"] * len(module_ids))
                conditions.append(f"sr.module_id IN ({placeholders})")
                params.extend(module_ids)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            cursor.execute(
                f"""
                SELECT sr.module_id,
                       COUNT(*) AS n,
                       AVG(sr.stress_level) AS avg_stress,
                       AVG(g.grade) AS avg_grade,
                       SUM(sr.stress_level * 1.0 * g.grade) AS sum_xy,
                       SUM(sr.stress_level * 1.0 * sr.stress_level) AS sum_x2,
                       SUM(g.grade * 1.0 * g.grade) AS sum_y2
                  FROM survey_responses sr
                  INNER JOIN grades g
                    ON sr.student_id = g.student_id
                   AND sr.module_id = g.module_id
                {where_clause}
                 GROUP BY sr.module_id
                 ORDER BY sr.module_id ASC;
                """,
                params,
            )
            rows = cursor.fetchall()

            return [
                self._build_corr_row(row) for row in rows
            ]
        except Exception as e:
            raise RuntimeError(f"对比压力与成绩失败: {e}")

    @staticmethod
    def _build_corr_row(row: tuple) -> Dict[str, Any]:
        module_id, n, avg_stress, avg_grade, sum_xy, sum_x2, sum_y2 = row
        if n is None or n < 2:
            corr = None
        else:
            # 皮尔逊相关系数公式： (sum_xy - n*mx*my) / sqrt((sum_x2 - n*mx^2)*(sum_y2 - n*my^2))
            numerator = sum_xy - n * avg_stress * avg_grade
            denom_left = sum_x2 - n * (avg_stress ** 2)
            denom_right = sum_y2 - n * (avg_grade ** 2)
            denominator = (denom_left * denom_right) ** 0.5
            corr = None if denominator == 0 else numerator / denominator

        return {
            "module_id": module_id,
            "average_stress_level": avg_stress,
            "average_grade": avg_grade,
            "sample_size": n,
            "pearson_corr": corr,
        }

    # ------------------------------------------------------------------
    # 功能：成绩分布（柱状图/饼图）
    # ------------------------------------------------------------------
    def get_grade_distribution(
        self,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
        bins: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Count grade buckets. Default bins: 0-60, 60-70, 70-80, 80-90, 90-100.
        Returns: [{"label": "80-90", "count": 5}, ...]
        """
        bins = bins or [(0, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
        try:
            cursor = self.conn.cursor()
            conditions: List[str] = []
            params: List[Any] = []

            if not include_inactive:
                conditions.append("is_active = 1")

            if module_id is not None:
                conditions.append("module_id = ?")
                params.append(module_id)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            cursor.execute(
                f"""
                SELECT grade
                  FROM grades
                {where_clause};
                """,
                params,
            )
            grades = [row[0] for row in cursor.fetchall()]

            results = []
            for low, high in bins:
                label = f"{int(low)}-{int(high) if high != 101 else 100}"
                results.append({"label": label, "count": 0})

            for g in grades:
                for idx, (low, high) in enumerate(bins):
                    if low <= g < high:
                        results[idx]["count"] += 1
                        break
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to build grade distribution: {e}")

    # ------------------------------------------------------------------
    # 功能：显示应力等级下的散点图
    # ------------------------------------------------------------------
    def get_stress_grade_pairs(
        self,
        module_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Join survey_responses and grades on student_id+module_id and return raw points.
        Each row: student_id, module_id, week_number, stress_level, grade.
        """
        try:
            cursor = self.conn.cursor()
            conditions: List[str] = []
            params: List[Any] = []

            if not include_inactive:
                conditions.append("sr.is_active = 1")
                conditions.append("g.is_active = 1")

            if module_id is not None:
                conditions.append("sr.module_id = ?")
                params.append(module_id)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            cursor.execute(
                f"""
                SELECT sr.student_id,
                       sr.module_id,
                       sr.week_number,
                       sr.stress_level,
                       g.grade
                  FROM survey_responses sr
                  INNER JOIN grades g
                    ON sr.student_id = g.student_id
                   AND sr.module_id = g.module_id
                {where_clause}
                 ORDER BY sr.student_id ASC, sr.module_id ASC, sr.week_number ASC;
                """,
                params,
            )
            rows = cursor.fetchall()
            return [
                {
                    "student_id": row[0],
                    "module_id": row[1],
                    "week_number": row[2],
                    "stress_level": row[3],
                    "grade": row[4],
                }
                for row in rows
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch stress-grade pairs: {e}")
