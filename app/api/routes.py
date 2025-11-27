import os
import sqlite3
from flask import jsonify, request, abort, current_app

from app.api import api_bp
from app.repositories.StudentRepository import StudentRepository
from app.repositories.AttendanceRecordRepository import AttendanceRecordRepository
from app.repositories.SubmissionRecordRepository import SubmissionRecordRepository
from app.repositories.SurveyResponseRepository import SurveyResponseRepository
from app.repositories.AlertRepository import AlertRepository
from app.models.Student import Student
from app.models.AttendanceRecord import AttendanceRecord
from app.models.SubmissionRecord import SubmissionRecord
from app.models.SurveyResponse import SurveyResponse
from app.models.Alert import Alert


def _get_db_path() -> str:
    """
    Resolve the sqlite database path from the DATABASE env or default config.
    Supports values like sqlite:////absolute/path/to/db.sqlite3.
    """
    db_url = os.environ.get("DATABASE") or current_app.config.get("DATABASE", "")

    # sqlite:///absolute/path -> absolute/path
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    if db_url:
        return db_url

    # Fallbacks: prefer dev DB if present, otherwise data.db in repo root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dev_db = os.path.join(repo_root, "db_dev.sqlite3")
    if os.path.exists(dev_db):
        return dev_db
    return os.path.join(repo_root, "data.db")


@api_bp.get("/students")
def list_students():
    """Return all active students as JSON."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = StudentRepository(conn)
        students = repo.list_all()
        return jsonify([_serialize_student(s) for s in students])
    finally:
        conn.close()


@api_bp.get("/students/<int:student_id>")
def get_student(student_id: int):
    """Return a single student by id."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = StudentRepository(conn)
        student = repo.get_by_id(student_id)
        if student is None or not student.is_active:
            abort(404, description="Student not found")
        return jsonify(_serialize_student(student))
    finally:
        conn.close()


@api_bp.post("/students")
def create_student():
    """Create a new student record."""
    payload = request.get_json(silent=True) or {}
    student = _parse_student_payload(payload)

    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = StudentRepository(conn)
        created = repo.add(student)
        return jsonify(_serialize_student(created)), 201
    finally:
        conn.close()


@api_bp.put("/students/<int:student_id>")
def update_student(student_id: int):
    """Update an existing student record."""
    payload = request.get_json(silent=True) or {}
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = StudentRepository(conn)
        existing = repo.get_by_id(student_id)
        if existing is None or not existing.is_active:
            abort(404, description="Student not found")

        updated_student = _parse_student_payload(payload, existing_student=existing)
        updated_student.id = student_id
        repo.update(updated_student)
        refreshed = repo.get_by_id(student_id)
        return jsonify(_serialize_student(refreshed))
    finally:
        conn.close()


@api_bp.delete("/students/<int:student_id>")
def delete_student(student_id: int):
    """Hard-delete a student record (remove row from DB)."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = StudentRepository(conn)
        existing = repo.get_by_id(student_id)
        if existing is None or not existing.is_active:
            abort(404, description="Student not found")
        # Use hard delete so the row disappears from the DB file (not just is_active=0).
        repo.hard_delete(student_id)
        return "", 204
    finally:
        conn.close()


@api_bp.get("/attendance")
def list_attendance():
    """Return all attendance records."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AttendanceRecordRepository(conn)
        records = repo.list_all()
        return jsonify([_serialize_attendance(r) for r in records])
    finally:
        conn.close()


@api_bp.post("/attendance")
def create_attendance():
    payload = request.get_json(silent=True) or {}
    record = _parse_attendance_payload(payload)
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AttendanceRecordRepository(conn)
        created = repo.add(record)
        return jsonify(_serialize_attendance(created)), 201
    finally:
        conn.close()


@api_bp.put("/attendance/<int:record_id>")
def update_attendance(record_id: int):
    payload = request.get_json(silent=True) or {}
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AttendanceRecordRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Attendance record not found")
        updated = _parse_attendance_payload(payload, existing_record=existing)
        updated.id = record_id
        repo.update(updated)
        refreshed = repo.get_by_id(record_id)
        return jsonify(_serialize_attendance(refreshed))
    finally:
        conn.close()


@api_bp.delete("/attendance/<int:record_id>")
def delete_attendance(record_id: int):
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AttendanceRecordRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Attendance record not found")
        repo.soft_delete(record_id)
        return "", 204
    finally:
        conn.close()


@api_bp.get("/submissions")
def list_submissions():
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SubmissionRecordRepository(conn)
        records = repo.list_all()
        return jsonify([_serialize_submission(r) for r in records])
    finally:
        conn.close()


@api_bp.post("/submissions")
def create_submission():
    payload = request.get_json(silent=True) or {}
    record = _parse_submission_payload(payload)
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SubmissionRecordRepository(conn)
        created = repo.add(record)
        return jsonify(_serialize_submission(created)), 201
    finally:
        conn.close()


@api_bp.put("/submissions/<int:record_id>")
def update_submission(record_id: int):
    payload = request.get_json(silent=True) or {}
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SubmissionRecordRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Submission record not found")
        updated = _parse_submission_payload(payload, existing_record=existing)
        updated.id = record_id
        repo.update(updated)
        refreshed = repo.get_by_id(record_id)
        return jsonify(_serialize_submission(refreshed))
    finally:
        conn.close()


@api_bp.delete("/submissions/<int:record_id>")
def delete_submission(record_id: int):
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SubmissionRecordRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Submission record not found")
        repo.soft_delete(record_id)
        return "", 204
    finally:
        conn.close()


@api_bp.get("/surveys")
def list_surveys():
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SurveyResponseRepository(conn)
        records = repo.list_all()
        return jsonify([_serialize_survey(r) for r in records])
    finally:
        conn.close()


@api_bp.post("/surveys")
def create_survey():
    payload = request.get_json(silent=True) or {}
    record = _parse_survey_payload(payload)
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SurveyResponseRepository(conn)
        created = repo.add(record)
        return jsonify(_serialize_survey(created)), 201
    finally:
        conn.close()


@api_bp.put("/surveys/<int:record_id>")
def update_survey(record_id: int):
    payload = request.get_json(silent=True) or {}
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SurveyResponseRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Survey response not found")
        updated = _parse_survey_payload(payload, existing_record=existing)
        updated.id = record_id
        repo.update(updated)
        refreshed = repo.get_by_id(record_id)
        return jsonify(_serialize_survey(refreshed))
    finally:
        conn.close()


@api_bp.delete("/surveys/<int:record_id>")
def delete_survey(record_id: int):
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = SurveyResponseRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Survey response not found")
        repo.soft_delete(record_id)
        return "", 204
    finally:
        conn.close()


@api_bp.get("/alerts")
def list_alerts():
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AlertRepository(conn)
        records = repo.list_all()
        return jsonify([_serialize_alert(r) for r in records])
    finally:
        conn.close()


@api_bp.post("/alerts")
def create_alert():
    payload = request.get_json(silent=True) or {}
    record = _parse_alert_payload(payload)
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AlertRepository(conn)
        created = repo.add(record)
        return jsonify(_serialize_alert(created)), 201
    finally:
        conn.close()


@api_bp.put("/alerts/<int:record_id>")
def update_alert(record_id: int):
    payload = request.get_json(silent=True) or {}
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AlertRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Alert not found")
        updated = _parse_alert_payload(payload, existing_alert=existing)
        updated.id = record_id
        repo.update(updated)
        refreshed = repo.get_by_id(record_id)
        return jsonify(_serialize_alert(refreshed))
    finally:
        conn.close()


@api_bp.delete("/alerts/<int:record_id>")
def delete_alert(record_id: int):
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        repo = AlertRepository(conn)
        existing = repo.get_by_id(record_id)
        if existing is None or not existing.is_active:
            abort(404, description="Alert not found")
        repo.soft_delete(record_id)
        return "", 204
    finally:
        conn.close()


def _serialize_student(student: Student) -> dict:
    """Convert a Student entity to JSON-ready dict."""
    return {
        "id": student.id,
        "studentNumber": student.student_number,
        "fullName": student.full_name,
        "courseName": student.course_name,
        "yearOfStudy": student.year_of_study,
        "email": student.email,
        # risk is not yet calculated in DB; default to low for UI
        "riskLevel": "low",
    }


def _parse_student_payload(payload: dict, existing_student: Student | None = None) -> Student:
    """
    Validate and map incoming JSON to Student.
    If existing_student provided, missing fields keep existing values.
    """
    required_fields = ["studentNumber", "fullName"]
    if existing_student is None:
        missing = [f for f in required_fields if not payload.get(f)]
        if missing:
            abort(400, description=f"Missing required fields: {', '.join(missing)}")

    def _get(key, default=None):
        return payload.get(key, default)

    student = existing_student or Student()
    student.student_number = _get("studentNumber", student.student_number)
    student.full_name = _get("fullName", student.full_name)
    student.email = _get("email", student.email)
    student.course_name = _get("courseName", student.course_name)

    year_value = payload.get("yearOfStudy")
    if year_value is not None:
        try:
            student.year_of_study = int(year_value)
        except (TypeError, ValueError):
            abort(400, description="yearOfStudy must be an integer")

    return student


def _serialize_attendance(record: AttendanceRecord) -> dict:
    return {
        "id": record.id,
        "studentId": record.student_id,
        "moduleId": record.module_id,
        "weekNumber": record.week_number,
        "attendedSessions": record.attended_sessions,
        "totalSessions": record.total_sessions,
        "attendanceRate": record.attendance_rate,
    }


def _parse_attendance_payload(payload: dict, existing_record: AttendanceRecord | None = None) -> AttendanceRecord:
    required_fields = ["studentId", "moduleId", "weekNumber"]
    if existing_record is None:
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            abort(400, description=f"Missing required fields: {', '.join(missing)}")

    record = existing_record or AttendanceRecord()
    record.student_id = _require_int(payload.get("studentId"), "studentId", record.student_id)
    record.module_id = _require_int(payload.get("moduleId"), "moduleId", record.module_id)
    record.week_number = _require_int(payload.get("weekNumber"), "weekNumber", record.week_number)
    record.attended_sessions = _optional_int(payload.get("attendedSessions"), record.attended_sessions)
    record.total_sessions = _optional_int(payload.get("totalSessions"), record.total_sessions)

    # auto-calc attendance_rate if sessions are present
    if record.attended_sessions is not None and record.total_sessions:
        record.attendance_rate = round((record.attended_sessions / record.total_sessions) * 100, 2)
    else:
        record.attendance_rate = _optional_float(payload.get("attendanceRate"), record.attendance_rate)
    return record


def _serialize_submission(record: SubmissionRecord) -> dict:
    return {
        "id": record.id,
        "studentId": record.student_id,
        "moduleId": record.module_id,
        "assessmentName": record.assessment_name,
        "dueDate": record.due_date,
        "submittedDate": record.submitted_date,
        "isSubmitted": record.is_submitted,
        "isLate": record.is_late,
    }


def _parse_submission_payload(
    payload: dict, existing_record: SubmissionRecord | None = None
) -> SubmissionRecord:
    required_fields = ["studentId", "moduleId", "assessmentName"]
    if existing_record is None:
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            abort(400, description=f"Missing required fields: {', '.join(missing)}")

    record = existing_record or SubmissionRecord()
    record.student_id = _require_int(payload.get("studentId"), "studentId", record.student_id)
    record.module_id = _require_int(payload.get("moduleId"), "moduleId", record.module_id)
    record.assessment_name = payload.get("assessmentName", record.assessment_name)
    record.due_date = payload.get("dueDate", record.due_date)
    record.submitted_date = payload.get("submittedDate", record.submitted_date)
    record.is_submitted = bool(payload.get("isSubmitted", record.is_submitted))
    record.is_late = bool(payload.get("isLate", record.is_late))
    return record


def _serialize_survey(record: SurveyResponse) -> dict:
    return {
        "id": record.id,
        "studentId": record.student_id,
        "moduleId": record.module_id,
        "weekNumber": record.week_number,
        "stressLevel": record.stress_level,
        "hoursSlept": record.hours_slept,
        "moodComment": record.mood_comment,
        "createdAt": record.created_at,
    }


def _parse_survey_payload(payload: dict, existing_record: SurveyResponse | None = None) -> SurveyResponse:
    required_fields = ["studentId", "weekNumber", "stressLevel"]
    if existing_record is None:
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            abort(400, description=f"Missing required fields: {', '.join(missing)}")

    record = existing_record or SurveyResponse()
    record.student_id = _require_int(payload.get("studentId"), "studentId", record.student_id)
    record.module_id = _optional_int(payload.get("moduleId"), record.module_id)
    record.week_number = _require_int(payload.get("weekNumber"), "weekNumber", record.week_number)
    record.stress_level = _require_int(payload.get("stressLevel"), "stressLevel", record.stress_level)
    record.hours_slept = _optional_float(payload.get("hoursSlept"), record.hours_slept)
    record.mood_comment = payload.get("moodComment", record.mood_comment)
    record.created_at = payload.get("createdAt", record.created_at)
    return record


def _serialize_alert(record: Alert) -> dict:
    return {
        "id": record.id,
        "studentId": record.student_id,
        "moduleId": record.module_id,
        "weekNumber": record.week_number,
        "reason": record.reason,
        "createdAt": record.created_at,
        "resolved": record.resolved,
        "severity": record.severity or "medium",
    }


def _parse_alert_payload(payload: dict, existing_alert: Alert | None = None) -> Alert:
    required_fields = ["studentId", "reason"]
    if existing_alert is None:
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            abort(400, description=f"Missing required fields: {', '.join(missing)}")

    record = existing_alert or Alert()
    record.student_id = _require_int(payload.get("studentId"), "studentId", record.student_id)
    record.module_id = _optional_int(payload.get("moduleId"), record.module_id)
    record.week_number = _optional_int(payload.get("weekNumber"), record.week_number)
    record.reason = payload.get("reason", record.reason)
    record.created_at = payload.get("createdAt", record.created_at)
    record.resolved = bool(payload.get("resolved", record.resolved))
    record.severity = payload.get("severity", record.severity or "medium")
    return record


def _require_int(value, field_name: str, fallback=None) -> int:
    if value is None and fallback is not None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        abort(400, description=f"{field_name} must be an integer")


def _optional_int(value, fallback=None):
    if value is None or value == "":
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        abort(400, description="Expected integer value")


def _optional_float(value, fallback=None):
    if value is None or value == "":
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        abort(400, description="Expected numeric value")
