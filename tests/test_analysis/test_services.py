
import sqlite3
import sys
from pathlib import Path
from typing import Dict

import pytest

# ----------------------------------------------------------------------
# 测试环境准备：补充 sys.path，确保能找到顶层的 app 包
# ----------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.analysis.services import AnalysisServiceRepository


# ----------------------------------------------------------------------
# 功能块：测试“统计学生平均出勤率”
# 说明：使用内存数据库（:memory:）手动建表、插样本数据，确保可控。
# ----------------------------------------------------------------------


@pytest.fixture
def memory_conn():
    """
    准备一个内存 SQLite 连接，创建 attendance_records 表并插入测试数据。
    """
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            attended_sessions INTEGER,
            total_sessions INTEGER,
            attendance_rate REAL,
            is_active INTEGER NOT NULL
        );
        """
    )
    rows = [
        # student 1 在 module 101 有两周记录：0.5 和 1.0 -> 平均 0.75
        (1, 101, 1, 1, 2, 0.5, 1),
        (1, 101, 2, 2, 2, 1.0, 1),
        # student 2：module 101 一条 0.25，module 102 一条 0.75
        (2, 101, 1, 1, 4, 0.25, 1),
        (2, 102, 1, 1, 4, 0.75, 1),
        # student 3：只有一条非活跃记录 0.9
        (3, 103, 1, 1, 1, 0.9, 0),
    ]
    conn.executemany(
        """
        INSERT INTO attendance_records (
            student_id, module_id, week_number,
            attended_sessions, total_sessions, attendance_rate, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
    yield conn
    conn.close()


def _to_map(rows) -> Dict[int, float]:
    """把 [{'student_id': x, 'average_attendance_rate': y}] 转成 {x: y}，便于断言。"""
    return {item["student_id"]: item["average_attendance_rate"] for item in rows}


def test_get_students_average_attendance_basic(memory_conn):
    service = AnalysisServiceRepository(conn=memory_conn)

    result = service.get_students_average_attendance()
    data = _to_map(result)

    # student 1: (0.5 + 1.0) / 2 = 0.75
    assert data[1] == pytest.approx(0.75)
    # student 2: (0.25 + 0.75) / 2 = 0.5
    assert data[2] == pytest.approx(0.5)
    # student 3 只有 is_active=0 的记录，默认不应该出现
    assert 3 not in data


def test_get_students_average_attendance_module_filter(memory_conn):
    service = AnalysisServiceRepository(conn=memory_conn)

    result = service.get_students_average_attendance(module_id=101)
    data = _to_map(result)

    # 只算 module 101
    assert data[1] == pytest.approx(0.75)  # student 1 只有 101 的两条
    assert data[2] == pytest.approx(0.25)  # student 2 在 101 只有一条 0.25
    assert 3 not in data


def test_get_students_average_attendance_include_inactive(memory_conn):
    service = AnalysisServiceRepository(conn=memory_conn)

    result = service.get_students_average_attendance(include_inactive=True)
    data = _to_map(result)

    # 现在应包含 student 3 的非活跃记录
    assert data[3] == pytest.approx(0.9)


def test_get_student_average_attendance_single_student(memory_conn):
    service = AnalysisServiceRepository(conn=memory_conn)

    # student 2 在 module 102 的平均值就是 0.75（只有一条记录）
    avg = service.get_student_average_attendance(student_id=2, module_id=102)
    assert avg == pytest.approx(0.75)

    # 不存在的模块筛选，应该返回 None
    avg_none = service.get_student_average_attendance(student_id=2, module_id=999)
    assert avg_none is None


# ----------------------------------------------------------------------
# 功能块：展示学生压力变化曲线
# ----------------------------------------------------------------------

@pytest.fixture
def survey_conn():
    """
    内存 SQLite，包含 survey_responses，用于压力曲线测试。
    """
    conn = sqlite3.connect(":memory:")
    conn.execute(
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
            is_active INTEGER NOT NULL
        );
        """
    )
    rows = [
        # student 1, module 101：周次乱序，用于测试排序
        (1, 101, 3, 5, 7.0, None, "2025-02-17T21:00:00", 1),
        (1, 101, 1, 3, 7.5, None, "2025-02-03T21:00:00", 1),
        (1, 101, 2, 4, 6.5, None, "2025-02-10T21:00:00", 1),
        # student 1, module 102：用于测试 module 过滤
        (1, 102, 1, 2, 8.0, None, "2025-02-03T22:00:00", 1),
        # student 2, module 101：不同学生
        (2, 101, 1, 4, 7.0, None, "2025-02-03T21:00:00", 1),
        # student 3：非活跃记录
        (3, 103, 1, 5, 5.0, None, "2025-02-03T21:00:00", 0),
    ]
    conn.executemany(
        """
        INSERT INTO survey_responses (
            student_id, module_id, week_number,
            stress_level, hours_slept, mood_comment, created_at, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
    yield conn
    conn.close()


def test_get_student_stress_trend_basic_sorted(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    data = service.get_student_stress_trend(student_id=1, module_id=101)

    weeks = [item["week_number"] for item in data]
    assert weeks == [1, 2, 3]

    stress_levels = [item["stress_level"] for item in data]
    assert stress_levels == [3, 4, 5]


def test_get_student_stress_trend_module_filter(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    data = service.get_student_stress_trend(student_id=1, module_id=102)

    assert len(data) == 1
    assert data[0]["week_number"] == 1
    assert data[0]["stress_level"] == 2


def test_get_student_stress_trend_include_inactive(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    data_default = service.get_student_stress_trend(student_id=3)
    assert data_default == []

    data_all = service.get_student_stress_trend(student_id=3, include_inactive=True)
    assert len(data_all) == 1
    assert data_all[0]["stress_level"] == 5

    service = AnalysisServiceRepository(conn=survey_conn)

    data = service.get_student_stress_trend(student_id=1, module_id=102)

    # 只应返回 module 102 的记录（一个周次）
    assert len(data) == 1
    assert data[0]["week_number"] == 1
    assert data[0]["stress_level"] == 2


def test_get_student_stress_trend_include_inactive(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    # student 3 默认不包含非活跃记录 -> 空列表
    data_default = service.get_student_stress_trend(student_id=3)
    assert data_default == []

    # include_inactive=True 时应能取到一条
    data_all = service.get_student_stress_trend(student_id=3, include_inactive=True)
    assert len(data_all) == 1
    assert data_all[0]["stress_level"] == 5


# ----------------------------------------------------------------------
# 功能块：测试“检测连续两周压力 >= 阈值 的学生”
# 说明：复用 survey_conn 样本数据，验证阈值与课程过滤。
# ----------------------------------------------------------------------

def test_detect_consecutive_high_stress_basic(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    # 只看 module 101，student 1 在周 2 和 3 满足 >=4
    events = service.detect_consecutive_high_stress(module_id=101)
    assert len(events) == 1
    evt = events[0]
    assert evt["student_id"] == 1
    assert evt["module_id"] == 101
    assert evt["week_start"] == 2
    assert evt["week_next"] == 3
    assert evt["stress_prev"] == 4
    assert evt["stress_curr"] == 5


def test_detect_consecutive_high_stress_threshold_higher(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    # 提高阈值到 5，则周 2(4) 和周 3(5) 不同时满足，结果应为空
    events = service.detect_consecutive_high_stress(threshold=5, module_id=101)
    assert events == []


def test_detect_consecutive_high_stress_all_modules(survey_conn):
    service = AnalysisServiceRepository(conn=survey_conn)

    # 不限定 module，结果仍应只有 student 1 的 101 模块事件
    events = service.detect_consecutive_high_stress()
    assert len(events) == 1
    assert events[0]["module_id"] == 101


# ----------------------------------------------------------------------
# 功能块：测试“自动创建预警记录”（alerts）
# ----------------------------------------------------------------------

@pytest.fixture
def alerts_conn():
    """
    准备 survey_responses + alerts 的内存库，方便验证预警生成。
    """
    conn = sqlite3.connect(":memory:")
    # survey_responses
    conn.execute(
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
            is_active INTEGER NOT NULL
        );
        """
    )
    # alerts
    conn.execute(
        """
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER,
            week_number INTEGER,
            reason TEXT NOT NULL,
            created_at TEXT,
            resolved INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    # 填充问卷数据：确保 student 1 有多次连续命中，student 2 一次命中
    survey_rows = [
        # student 1, module 101 -> 连续 (2,3) 和 (3,4)，应取最新 (3,4)
        (1, 101, 1, 3, 7.0, None, "2025-02-03T21:00:00", 1),
        (1, 101, 2, 4, 7.0, None, "2025-02-10T21:00:00", 1),
        (1, 101, 3, 5, 7.0, None, "2025-02-17T21:00:00", 1),
        (1, 101, 4, 5, 7.0, None, "2025-02-24T21:00:00", 1),
        # student 2, module 102 -> 连续 (1,2) 命中
        (2, 102, 1, 5, 8.0, None, "2025-02-03T21:00:00", 1),
        (2, 102, 2, 5, 8.0, None, "2025-02-10T21:00:00", 1),
        # student 3, module 103 -> 非连续，不应产生预警
        (3, 103, 1, 4, 6.0, None, "2025-02-03T21:00:00", 1),
        (3, 103, 3, 5, 6.0, None, "2025-02-17T21:00:00", 1),
    ]
    conn.executemany(
        """
        INSERT INTO survey_responses (
            student_id, module_id, week_number,
            stress_level, hours_slept, mood_comment, created_at, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        survey_rows,
    )

    # 预先放一条旧的 alerts，验证 clear_old 的效果
    conn.execute(
        """
        INSERT INTO alerts (student_id, module_id, week_number, reason, created_at, resolved, is_active)
        VALUES (1, 101, 2, 'old alert', '2025-02-11T10:00:00', 0, 1);
        """
    )
    conn.commit()
    yield conn
    conn.close()


def _fetch_all_alerts(conn):
    return conn.execute(
        """
        SELECT student_id, module_id, week_number, reason, resolved, is_active
        FROM alerts
        ORDER BY student_id, module_id, week_number;
        """
    ).fetchall()


def test_create_high_stress_alerts_basic(alerts_conn):
    service = AnalysisServiceRepository(conn=alerts_conn)

    inserted = service.create_high_stress_alerts(clear_old=True)

    # 应插入两条：student 1 (周3->4, week_number=4)，student 2 (周1->2, week_number=2)
    rows = _fetch_all_alerts(alerts_conn)
    assert len(rows) == 2

    # 方便断言
    rows_map = {(r[0], r[1]): r for r in rows}
    s1 = rows_map[(1, 101)]
    assert s1[2] == 4
    # 找到对应 student 1 的插入记录，检查 reason 含周次
    reason_map = {(item["student_id"], item["module_id"]): item["reason"] for item in inserted}
    assert "consecutive weeks 3 and 4" in reason_map[(1, 101)]
    assert s1[4] == 0 and s1[5] == 1

    s2 = rows_map[(2, 102)]
    assert s2[2] == 2
    assert s2[4] == 0 and s2[5] == 1


def test_create_high_stress_alerts_no_clear_old_duplicates(alerts_conn):
    service = AnalysisServiceRepository(conn=alerts_conn)

    # 第一次不清理旧的 -> 旧 alert + 新生成两条 = 3
    _ = service.create_high_stress_alerts(clear_old=False)
    rows_first = _fetch_all_alerts(alerts_conn)
    assert len(rows_first) == 3

    # 再执行一次（仍然不清理） -> 再加两条新插入，总计 5
    _ = service.create_high_stress_alerts(clear_old=False)
    rows_second = _fetch_all_alerts(alerts_conn)
    assert len(rows_second) == 5


def test_create_high_stress_alerts_module_filter(alerts_conn):
    service = AnalysisServiceRepository(conn=alerts_conn)

    # 只针对 module 101 生成，应该只新增 student 1 的一条（且清理旧的 module 101 的 alert）
    inserted = service.create_high_stress_alerts(module_id=101, clear_old=True)

    rows = _fetch_all_alerts(alerts_conn)
    # 只应该剩下 module 101 的一条
    assert len(rows) == 1
    assert rows[0][0] == 1 and rows[0][1] == 101
    assert rows[0][2] == 4
    reason_map = {(item["student_id"], item["module_id"]): item["reason"] for item in inserted}
    assert "module_id=101" in reason_map[(1, 101)]

# ----------------------------------------------------------------------
# 新增功能块：对比不同学生群体（模块）的压力与成绩关系
# ----------------------------------------------------------------------

import sqlite3
import pytest


@pytest.fixture
def stress_grade_conn():
    """
    内存库，包含 survey_responses 与 grades 两张表，用于对比压力-成绩。
    """
    conn = sqlite3.connect(":memory:")
    conn.execute(
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
            is_active INTEGER NOT NULL
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            assessment_name TEXT,
            grade REAL NOT NULL,
            is_active INTEGER NOT NULL
        );
        """
    )

    survey_rows = [
        # module 101：student 1 两周、student 2 一周（均活跃）
        (1, 101, 1, 4, 7.5, None, "2025-02-03T21:00:00", 1),
        (1, 101, 2, 2, 7.0, None, "2025-02-10T21:00:00", 1),
        (2, 101, 1, 3, 6.5, None, "2025-02-03T21:00:00", 1),
        # module 102：student 3 一条活跃、一条非活跃
        (3, 102, 1, 5, 8.0, None, "2025-02-03T21:00:00", 1),
        (3, 102, 2, 4, 7.5, None, "2025-02-10T21:00:00", 0),
    ]
    conn.executemany(
        """
        INSERT INTO survey_responses (
            student_id, module_id, week_number,
            stress_level, hours_slept, mood_comment, created_at, is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        survey_rows,
    )

    grade_rows = [
        (1, 101, "final", 80.0, 1),
        (2, 101, "final", 60.0, 1),
        (3, 102, "final", 90.0, 1),
    ]
    conn.executemany(
        """
        INSERT INTO grades (
            student_id, module_id, assessment_name, grade, is_active
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        grade_rows,
    )
    conn.commit()
    yield conn
    conn.close()


def _to_module_map(rows):
    return {item["module_id"]: item for item in rows}


def test_compare_stress_grade_by_module_basic(stress_grade_conn):
    service = AnalysisServiceRepository(conn=stress_grade_conn)

    data = service.compare_stress_grade_by_module()
    assert len(data) == 2

    mapped = _to_module_map(data)
    m101 = mapped[101]
    # stress: (4 + 2 + 3) / 3 = 3.0
    assert m101["average_stress_level"] == pytest.approx(3.0)
    # grade: (80 + 80 + 60) / 3 = 73.333...
    assert m101["average_grade"] == pytest.approx(73.333, rel=1e-3)
    assert m101["sample_size"] == 3
    # corr: x=[4,2,3], y=[80,80,60]; 协方差为 0 -> 相关系数 0
    assert m101["pearson_corr"] == pytest.approx(0.0)

    m102 = mapped[102]
    assert m102["average_stress_level"] == pytest.approx(5.0)
    assert m102["average_grade"] == pytest.approx(90.0)
    assert m102["sample_size"] == 1
    assert m102["pearson_corr"] is None  # 样本数不足 2


def test_compare_stress_grade_by_module_filter_and_inactive(stress_grade_conn):
    service = AnalysisServiceRepository(conn=stress_grade_conn)

    # 模块过滤
    filtered = service.compare_stress_grade_by_module(module_ids=[101])
    assert len(filtered) == 1
    assert filtered[0]["module_id"] == 101

    # 包含非活跃记录后，module 102 应计入第二条 stress=4
    include_all = service.compare_stress_grade_by_module(include_inactive=True)
    mapped = _to_module_map(include_all)
    m102 = mapped[102]
    # stress: (5 + 4)/2 = 4.5
    assert m102["average_stress_level"] == pytest.approx(4.5)
    # grade 仍为 90，两条记录重复 grade -> 90
    assert m102["average_grade"] == pytest.approx(90.0)
    assert m102["sample_size"] == 2
    # corr: x=[5,4], y=[90,90] -> denominator 0 -> None
    assert m102["pearson_corr"] is None


# ----------------------------------------------------------------------
# 新增功能块：成绩分布 & 压力-成绩散点
# ----------------------------------------------------------------------

@pytest.fixture
def grade_distribution_conn():
    """
    内存库，仅含 grades 表，验证分布统计。
    """
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            assessment_name TEXT,
            grade REAL NOT NULL,
            is_active INTEGER NOT NULL
        );
        """
    )
    rows = [
        (1, 101, "final", 50.0, 1),  # 0-60
        (2, 101, "final", 65.0, 1),  # 60-70
        (3, 101, "final", 75.0, 1),  # 70-80
        (4, 101, "final", 85.0, 1),  # 80-90
        (5, 101, "final", 95.0, 1),  # 90-100
        (6, 102, "final", 55.0, 0),  # inactive
    ]
    conn.executemany(
        """
        INSERT INTO grades (student_id, module_id, assessment_name, grade, is_active)
        VALUES (?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
    yield conn
    conn.close()


def _to_label_map(rows):
    return {item["label"]: item["count"] for item in rows}


def test_get_grade_distribution_default_bins(grade_distribution_conn):
    service = AnalysisServiceRepository(conn=grade_distribution_conn)

    data = service.get_grade_distribution()
    label_map = _to_label_map(data)

    assert label_map["0-60"] == 1
    assert label_map["60-70"] == 1
    assert label_map["70-80"] == 1
    assert label_map["80-90"] == 1
    assert label_map["90-100"] == 1


def test_get_grade_distribution_module_filter_and_inactive(grade_distribution_conn):
    service = AnalysisServiceRepository(conn=grade_distribution_conn)

    # 只看 101
    data = service.get_grade_distribution(module_id=101)
    assert sum(_to_label_map(data).values()) == 5

    # 包含非活跃 -> 101 的 5 条 + 102 的 1 条
    data_all = service.get_grade_distribution(include_inactive=True)
    assert sum(_to_label_map(data_all).values()) == 6


def test_get_stress_grade_pairs_basic(stress_grade_conn):
    service = AnalysisServiceRepository(conn=stress_grade_conn)

    data = service.get_stress_grade_pairs()
    # 默认不含非活跃 -> 4 条（101 的 3 条 + 102 的 1 条）
    assert len(data) == 4
    # 顺序应按 student_id, module_id, week_number
    assert data[0]["student_id"] == 1 and data[0]["week_number"] == 1
    assert data[1]["student_id"] == 1 and data[1]["week_number"] == 2
    assert data[2]["student_id"] == 2 and data[2]["week_number"] == 1
    assert data[3]["student_id"] == 3 and data[3]["week_number"] == 1


def test_get_stress_grade_pairs_filter_and_inactive(stress_grade_conn):
    service = AnalysisServiceRepository(conn=stress_grade_conn)

    filtered = service.get_stress_grade_pairs(module_id=101)
    assert len(filtered) == 3
    assert all(item["module_id"] == 101 for item in filtered)

    all_rows = service.get_stress_grade_pairs(include_inactive=True)
    # 多了一条 module 102 的非活跃记录
    assert len(all_rows) == 5
