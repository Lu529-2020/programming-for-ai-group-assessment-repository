# tests/utils/test_json_helper.py
from dataclasses import dataclass
from typing import Optional

import json

from utils.json_convert_util import JsonHelper

# 测试执行语句：pytest tests/test_utils/test_json_convert_util.py -vv


# ====== 模拟两张表的数据对象 ======

@dataclass
class TestStudent:
    """
    模拟 students 表的数据结构：
    id, student_number, full_name, email, course_name, year_of_study, is_active
    """
    id: int
    student_number: str
    full_name: str
    email: str
    course_name: str
    year_of_study: int
    is_active: bool


@dataclass
class TestSurveyResponse:
    """
    模拟 survey_responses 表的数据结构：
    id, student_id, module_id, week_number, stress_level, hours_slept, mood_comment, is_active
    """
    id: int
    student_id: int
    module_id: int
    week_number: int
    stress_level: int
    hours_slept: float
    mood_comment: Optional[str]
    is_active: bool


# ====== 测试 to_serializable 对单个 dataclass 的处理 ======

def test_to_serializable_single_student():
    student = TestStudent(
        id=1,
        student_number="S0001",
        full_name="Alice Smith",
        email="alice@example.com",
        course_name="MSc AI",
        year_of_study=1,
        is_active=True,
    )

    result = JsonHelper.to_serializable(student)

    # 应该是一个 dict
    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["student_number"] == "S0001"
    assert result["full_name"] == "Alice Smith"
    assert result["email"] == "alice@example.com"
    assert result["course_name"] == "MSc AI"
    assert result["year_of_study"] == 1
    assert result["is_active"] is True


# ====== 测试 to_serializable 对对象列表的处理 ======

def test_to_serializable_survey_list():
    surveys = [
        TestSurveyResponse(
            id=1,
            student_id=1,
            module_id=101,
            week_number=1,
            stress_level=3,
            hours_slept=7.5,
            mood_comment="Feeling ok",
            is_active=True,
        ),
        TestSurveyResponse(
            id=2,
            student_id=1,
            module_id=101,
            week_number=2,
            stress_level=5,
            hours_slept=4.0,
            mood_comment="Very stressed",
            is_active=True,
        ),
    ]

    result = JsonHelper.to_serializable(surveys)

    assert isinstance(result, list)
    assert len(result) == 2

    first = result[0]
    assert first["id"] == 1
    assert first["student_id"] == 1
    assert first["module_id"] == 101
    assert first["week_number"] == 1
    assert first["stress_level"] == 3
    assert first["hours_slept"] == 7.5
    assert first["mood_comment"] == "Feeling ok"
    assert first["is_active"] is True


# ====== 测试 success_dict ======

def test_success_dict_with_student():
    student = TestStudent(
        id=2,
        student_number="S0002",
        full_name="Bob Lee",
        email="bob@example.com",
        course_name="MSc Data Science",
        year_of_study=2,
        is_active=False,
    )

    resp = JsonHelper.success_dict(student, message="get student ok")

    assert resp["success"] is True
    assert resp["message"] == "get student ok"

    data = resp["data"]
    assert isinstance(data, dict)
    assert data["id"] == 2
    assert data["student_number"] == "S0002"
    assert data["full_name"] == "Bob Lee"
    assert data["email"] == "bob@example.com"
    assert data["course_name"] == "MSc Data Science"
    assert data["year_of_study"] == 2
    assert data["is_active"] is False


# ====== 测试 error_dict ======

def test_error_dict_with_details():
    details = {
        "field_errors": {
            "student_number": "student_number is required",
            "email": "invalid email format",
        }
    }

    resp = JsonHelper.error_dict(
        message="Validation failed",
        details=details,
    )

    assert resp["success"] is False
    assert resp["message"] == "Validation failed"
    assert "details" in resp
    assert resp["details"]["field_errors"]["student_number"] == "student_number is required"
    assert resp["details"]["field_errors"]["email"] == "invalid email format"


# ====== 测试 success_json / error_json 生成的 JSON 字符串 ======

def test_success_json_and_error_json():
    student = TestStudent(
        id=3,
        student_number="S0003",
        full_name="Charlie",
        email="charlie@example.com",
        course_name="MSc CS",
        year_of_study=1,
        is_active=True,
    )

    # 生成 JSON 字符串
    success_json_str = JsonHelper.success_json(student, message="ok", ensure_ascii=False)
    error_json_str = JsonHelper.error_json(
        message="not ok",
        details={"code": "E001"},
        ensure_ascii=False,
    )

    # 通过 json.loads 解析回 Python 对象验证结构
    success_obj = json.loads(success_json_str)
    error_obj = json.loads(error_json_str)

    # success_json
    assert success_obj["success"] is True
    assert success_obj["message"] == "ok"
    assert success_obj["data"]["id"] == 3
    assert success_obj["data"]["student_number"] == "S0003"

    # error_json
    assert error_obj["success"] is False
    assert error_obj["message"] == "not ok"
    assert error_obj["details"]["code"] == "E001"