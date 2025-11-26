# manage_db.py
import os
import sqlite3
import random
from datetime import date, timedelta, datetime
from typing import Optional, Dict, Tuple


# =======================
# 1. 统一的建库/重置函数
# =======================
def init_database(db_path: str) -> sqlite3.Connection:
    """
    初始化学生福祉分析系统的 SQLite 数据库，并预置一些模拟数据。
    同时根据压力问卷生成 stress_events 和 alerts。

    - 如果指定路径已存在数据库文件：删除已有的相关表并重新建表。
    - 如果数据库文件不存在：新建数据库文件并创建所有表。
    """
    db_exists = os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 先删表再重建
    drop_statements = [
        "DROP TABLE IF EXISTS stress_events;",
        "DROP TABLE IF EXISTS alerts;",
        "DROP TABLE IF EXISTS grades;",
        "DROP TABLE IF EXISTS survey_responses;",
        "DROP TABLE IF EXISTS submission_records;",
        "DROP TABLE IF EXISTS attendance_records;",
        "DROP TABLE IF EXISTS enrolments;",
        "DROP TABLE IF EXISTS modules;",
        "DROP TABLE IF EXISTS students;",
        "DROP TABLE IF EXISTS users;",
    ]
    for stmt in drop_statements:
        cursor.execute(stmt)

    # ================
    # 创建各个表（含 is_active 字段）
    # ================

    # 用户表
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    # 学生表
    cursor.execute(
        """
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT,
            course_name TEXT,
            year_of_study INTEGER,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    # 模块表
    cursor.execute(
        """
        CREATE TABLE modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_code TEXT NOT NULL UNIQUE,
            module_title TEXT NOT NULL,
            credit INTEGER,
            academic_year TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    # 选课表
    cursor.execute(
        """
        CREATE TABLE enrolments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            enrol_date TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        """
    )

    # 出勤记录表
    cursor.execute(
        """
        CREATE TABLE attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            attended_sessions INTEGER,
            total_sessions INTEGER,
            attendance_rate REAL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        """
    )

    # 作业提交记录表
    cursor.execute(
        """
        CREATE TABLE submission_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            assessment_name TEXT NOT NULL,
            due_date TEXT,
            submitted_date TEXT,
            is_submitted INTEGER NOT NULL DEFAULT 0,
            is_late INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        """
    )

    # 福祉问卷记录表
    cursor.execute(
        """
        CREATE TABLE survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER,
            week_number INTEGER NOT NULL,
            stress_level INTEGER NOT NULL,
            hours_slept REAL,
            mood_comment TEXT,
            created_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL
        );
        """
    )

    # 成绩表
    cursor.execute(
        """
        CREATE TABLE grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            assessment_name TEXT NOT NULL,
            grade REAL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        """
    )

    # 预警表（连续两周高压力）
    cursor.execute(
        """
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER,
            week_number INTEGER,
            reason TEXT NOT NULL,
            created_at TEXT,
            resolved INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL
        );
        """
    )

    # 单次高压力事件表
    cursor.execute(
        """
        CREATE TABLE stress_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER,
            survey_response_id INTEGER,
            week_number INTEGER,
            stress_level INTEGER NOT NULL,
            cause_category TEXT NOT NULL,
            description TEXT,
            source TEXT NOT NULL,
            created_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL,
            FOREIGN KEY (survey_response_id) REFERENCES survey_responses(id) ON DELETE SET NULL
        );
        """
    )

    conn.commit()

    if db_exists:
        print(f"[init_database] 数据库已存在：已清空并重建表结构 -> {db_path}")
    else:
        print(f"[init_database] 数据库不存在：已新建并创建表结构 -> {db_path}")

    # 插入模拟数据
    seed_demo_data(conn)
    # 基于问卷生成单次高压力事件
    seed_stress_events(conn, threshold=4)
    # 基于问卷生成“连续两周高压力”预警（每个学生仅保留最近一条）
    generate_stress_alerts(conn, threshold=4, clear_old=True)

    return conn


# =======================
# 2. 插入基础模拟数据
# =======================
def seed_demo_data(conn: sqlite3.Connection) -> None:
    """
    插入：
    - 3 个用户
    - 50 学生
    - 8 门课程
    - 随机选课
    - 出勤、作业、成绩、福祉问卷数据
    """
    cursor = conn.cursor()
    random.seed(42)

    # 2.1 用户
    users = [
        ("admin", "hashed_admin_password", "admin"),
        ("course_director", "hashed_cd_password", "course_director"),
        ("wellbeing_officer", "hashed_swo_password", "wellbeing_officer"),
    ]
    for username, pwd, role in users:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, created_at, is_active)
            VALUES (?, ?, ?, ?, 1);
            """,
            (username, pwd, role, "2025-01-01T09:00:00"),
        )

    # 2.2 课程（8 门）
    module_codes = [f"MOD10{i}" for i in range(1, 9)]
    module_titles = [
        "Introduction to Programming",
        "Data Structures and Algorithms",
        "Database Systems",
        "Machine Learning Fundamentals",
        "Deep Learning Basics",
        "Data Visualisation",
        "Software Engineering",
        "AI Ethics and Society",
    ]
    module_ids = []
    for code, title in zip(module_codes, module_titles):
        cursor.execute(
            """
            INSERT INTO modules (module_code, module_title, credit, academic_year, is_active)
            VALUES (?, ?, ?, ?, 1);
            """,
            (code, title, 15, "2025/2026"),
        )
        module_ids.append(cursor.lastrowid)

    # 2.3 学生（50 人）
    course_options = ["MSc Applied AI", "MSc Data Science", "MSc Cyber Security"]
    student_ids = []
    for i in range(1, 51):
        student_number = f"S{i:04d}"
        full_name = f"Student {i}"
        email = f"student{i}@example.com"
        course_name = random.choice(course_options)
        year_of_study = random.randint(1, 2)
        cursor.execute(
            """
            INSERT INTO students (student_number, full_name, email, course_name, year_of_study, is_active)
            VALUES (?, ?, ?, ?, ?, 1);
            """,
            (student_number, full_name, email, course_name, year_of_study),
        )
        student_ids.append(cursor.lastrowid)

    # 2.4 选课
    enrolments = []
    base_enrol_date = date(2025, 1, 10)
    for sid in student_ids:
        k = random.randint(3, 5)
        chosen_modules = random.sample(module_ids, k)
        for mid in chosen_modules:
            enrol_date = base_enrol_date + timedelta(days=random.randint(0, 10))
            cursor.execute(
                """
                INSERT INTO enrolments (student_id, module_id, enrol_date, is_active)
                VALUES (?, ?, ?, 1);
                """,
                (sid, mid, enrol_date.isoformat()),
            )
            enrolments.append((sid, mid))

    # 2.5 出勤 + 问卷 + 作业 + 成绩
    weeks = list(range(1, 11))
    base_week_date = date(2025, 2, 3)
    assessment_names = ["Assignment 1", "Assignment 2"]

    for sid, mid in enrolments:
        # 每个学生-课程 10 周的出勤 & 问卷
        for w in weeks:
            # 出勤
            total_sessions = 2
            attended_sessions = random.randint(0, total_sessions)
            attendance_rate = attended_sessions / total_sessions if total_sessions > 0 else None
            cursor.execute(
                """
                INSERT INTO attendance_records (
                    student_id, module_id, week_number,
                    attended_sessions, total_sessions, attendance_rate, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, 1);
                """,
                (sid, mid, w, attended_sessions, total_sessions, attendance_rate),
            )

            # 问卷（压力 & 睡眠）
            if attendance_rate is not None:
                base_stress = 3 + (1 - attendance_rate) * 2
                stress_level = int(round(max(1, min(5, random.gauss(base_stress, 0.8)))))
            else:
                stress_level = random.randint(1, 5)

            base_sleep = 7 + (attendance_rate or 0)
            hours_slept = max(3.0, min(10.0, random.gauss(base_sleep, 1.0)))

            week_date = base_week_date + timedelta(weeks=w - 1)
            created_at = f"{week_date.isoformat()}T21:00:00"

            cursor.execute(
                """
                INSERT INTO survey_responses (
                    student_id, module_id, week_number,
                    stress_level, hours_slept, mood_comment, created_at, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1);
                """,
                (sid, mid, w, stress_level, hours_slept, None, created_at),
            )

        # 作业 & 成绩
        for idx, aname in enumerate(assessment_names, start=1):
            due_week = 4 if idx == 1 else 8
            due_date = base_week_date + timedelta(weeks=due_week - 1)
            due_date_str = due_date.isoformat()

            is_submitted = 1 if random.random() < 0.9 else 0
            is_late = 0
            submitted_date_str: Optional[str] = None

            if is_submitted:
                if random.random() < 0.8:
                    delta_days = -random.randint(0, 2)
                    is_late = 0
                else:
                    delta_days = random.randint(1, 5)
                    is_late = 1
                submitted_date = due_date + timedelta(days=delta_days)
                submitted_date_str = submitted_date.isoformat()

            if is_submitted:
                base_grade = random.uniform(45, 90)
                if is_late:
                    base_grade -= random.uniform(5, 15)
                grade_value = max(0.0, min(100.0, base_grade))
            else:
                grade_value = random.uniform(0, 35)

            cursor.execute(
                """
                INSERT INTO submission_records (
                    student_id, module_id, assessment_name,
                    due_date, submitted_date, is_submitted, is_late, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1);
                """,
                (sid, mid, aname, due_date_str, submitted_date_str, is_submitted, is_late),
            )

            cursor.execute(
                """
                INSERT INTO grades (
                    student_id, module_id, assessment_name, grade, is_active
                )
                VALUES (?, ?, ?, ?, 1);
                """,
                (sid, mid, aname, grade_value),
            )

    conn.commit()
    print("[seed_demo_data] 已插入示例用户、学生、课程、选课、出勤、作业、成绩与福祉数据。")


# =======================
# 3. 从问卷生成 stress_events
# =======================
def seed_stress_events(conn: sqlite3.Connection, threshold: int = 4) -> None:
    """
    根据 survey_responses 中的高压力记录生成 stress_events：
    - is_active = 1
    - stress_level >= threshold 视为一次单独的高压力事件
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, student_id, module_id, week_number, stress_level, created_at
        FROM survey_responses
        WHERE is_active = 1 AND stress_level >= ?;
        """,
        (threshold,),
    )
    rows = cursor.fetchall()

    if not rows:
        print("[seed_stress_events] 没有高压力问卷记录，未生成 stress_events。")
        return

    cause_categories = ["academic", "personal", "health", "financial", "other"]
    events_to_insert = []

    for survey_id, student_id, module_id, week_number, stress_level, created_at in rows:
        cause_category = random.choice(cause_categories)
        description = f"High stress reported (level {stress_level}) in week {week_number}."
        source = "system"
        events_to_insert.append(
            (
                student_id,
                module_id,
                survey_id,
                week_number,
                stress_level,
                cause_category,
                description,
                source,
                created_at,
                1,  # is_active
            )
        )

    cursor.executemany(
        """
        INSERT INTO stress_events (
            student_id, module_id, survey_response_id, week_number,
            stress_level, cause_category, description, source,
            created_at, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        events_to_insert,
    )

    conn.commit()
    print(f"[seed_stress_events] 已生成 {len(events_to_insert)} 条 stress_events 记录。")


# =======================
# 4. 从问卷生成连续两周高压力预警（alerts）
# =======================
def generate_stress_alerts(conn: sqlite3.Connection, threshold: int = 4, clear_old: bool = True) -> None:
    """
    根据 survey_responses 检测连续两周高压力，并生成 alerts。
    规则：
        - 对每个 (student_id, module_id)：
          如果某两周 week 和 week+1 的 stress_level >= threshold，则视为一次高压力预警事件。
        - 但对每个学生（student_id），只保留最新的一条预警记录写入 alerts。
    """
    cursor = conn.cursor()

    if clear_old:
        cursor.execute("DELETE FROM alerts;")

    cursor.execute(
        """
        SELECT student_id, module_id, week_number, stress_level
        FROM survey_responses
        WHERE is_active = 1
        ORDER BY student_id, module_id, week_number;
        """
    )
    rows = cursor.fetchall()

    prev_student_id: Optional[int] = None
    prev_module_id: Optional[int] = None
    prev_week: Optional[int] = None
    prev_stress: Optional[int] = None

    latest_alert_by_student: Dict[int, Tuple[int, Optional[int], int, str, str, int]] = {}

    for student_id, module_id, week_number, stress_level in rows:
        if (student_id != prev_student_id) or (module_id != prev_module_id):
            prev_student_id = student_id
            prev_module_id = module_id
            prev_week = week_number
            prev_stress = stress_level
            continue

        if (
            prev_week is not None
            and week_number == prev_week + 1
            and prev_stress is not None
            and prev_stress >= threshold
            and stress_level >= threshold
        ):
            reason = (
                f"Stress level >= {threshold} for two consecutive weeks "
                f"({prev_week} and {week_number}) in module_id={module_id}."
            )
            created_at = datetime.now().isoformat(timespec="seconds")
            candidate = (student_id, module_id, week_number, reason, created_at, 0)

            if student_id not in latest_alert_by_student:
                latest_alert_by_student[student_id] = candidate
            else:
                _, _, existing_week, *_ = latest_alert_by_student[student_id]
                if week_number > existing_week:
                    latest_alert_by_student[student_id] = candidate

        prev_week = week_number
        prev_stress = stress_level

    alerts_to_insert = list(latest_alert_by_student.values())

    if alerts_to_insert:
        cursor.executemany(
            """
            INSERT INTO alerts (student_id, module_id, week_number, reason, created_at, resolved)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            alerts_to_insert,
        )

    conn.commit()
    print(f"[generate_stress_alerts] 已为 {len(alerts_to_insert)} 名学生生成最近一次连续两周高压力预警。")


# =======================
# 5. 一键初始化开发库 + 测试库
# =======================
def init_dev_and_test_databases():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dev_db_path = os.path.join(base_dir, "db_dev.sqlite3")
    test_db_path = os.path.join(base_dir, "db_test.sqlite3")

    print("=== 初始化开发数据库 ===")
    dev_conn = init_database(dev_db_path)
    dev_conn.close()

    print("=== 初始化测试数据库 ===")
    test_conn = init_database(test_db_path)
    test_conn.close()

    print("=== 所有数据库初始化完成 ===")


if __name__ == "__main__":
    init_dev_and_test_databases()