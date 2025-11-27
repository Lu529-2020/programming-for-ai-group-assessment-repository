from flask import request, jsonify

from utils.json_convert_util import JsonHelper
from . import analysis_bp
from .services import AnalysisServiceRepository


def _to_bool(val: str) -> bool:
    """Lightweight parse for truthy query/body values."""
    return str(val).lower() in {"1", "true", "yes", "on"}


@analysis_bp.route("/analysis-test")
def analysis_test_route():
    service = AnalysisServiceRepository()
    msg = service.test()
    return jsonify(JsonHelper.success_dict({"msg": msg}))


# -----------------------------
# 功能：展示学生压力变化曲线
# -----------------------------
@analysis_bp.route("/analysis/stress-trend", methods=["GET"])
def analysis_stress_trend():
    """
    压力趋势：指定学生（可选课程）的按周压力列表。
    Query: student_id（必填）, module_id（可选）, include_inactive（可选: true/false）
    """
    student_id = request.args.get("student_id", type=int)
    if student_id is None:
        return jsonify(JsonHelper.error_dict("student_id is required")), 400

    module_id = request.args.get("module_id", type=int)
    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.get_student_stress_trend(
            student_id=student_id,
            module_id=module_id,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：统计学生平均出勤率
# -----------------------------
@analysis_bp.route("/analysis/attendance/averages", methods=["GET"])
def analysis_attendance_averages():
    """
    出勤率：返回所有学生的平均出勤率，可按课程过滤。
    Query: module_id (可选), include_inactive (可选: true/false)
    """
    module_id = request.args.get("module_id", type=int)
    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.get_students_average_attendance(
            module_id=module_id,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：对比压力与成绩关系
# -----------------------------
@analysis_bp.route("/analysis/stress-grade/by-module", methods=["GET"])
def analysis_stress_grade_by_module():
    """
    压力-成绩对比：按模块返回平均压力、平均成绩、样本量和相关系数。
    Query: module_id (可选, 逗号分隔), include_inactive (可选: true/false)
    """
    raw_modules = request.args.get("module_id")
    module_ids = None
    if raw_modules:
        try:
            module_ids = [int(mid.strip()) for mid in raw_modules.split(",") if mid.strip()]
        except ValueError:
            return jsonify(JsonHelper.error_dict("module_id must be int or comma-separated ints")), 400

    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.compare_stress_grade_by_module(
            module_ids=module_ids,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：成绩分布（饼图）
# -----------------------------
@analysis_bp.route("/analysis/grades/distribution", methods=["GET"])
def analysis_grade_distribution():
    """
    成绩分布：按分桶统计成绩数量。
    Query: module_id (可选), include_inactive (可选: true/false)
    """
    module_id = request.args.get("module_id", type=int)
    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.get_grade_distribution(
            module_id=module_id,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：压力-成绩散点数据
# -----------------------------
@analysis_bp.route("/analysis/stress-grade/pairs", methods=["GET"])
def analysis_stress_grade_pairs():
    """
    压力-成绩散点：返回原始点集（student/module/week 对应的压力与成绩）。
    Query: module_id (可选), include_inactive (可选: true/false)
    """
    module_id = request.args.get("module_id", type=int)
    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.get_stress_grade_pairs(
            module_id=module_id,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：检测连续两周高压
# -----------------------------
@analysis_bp.route("/analysis/stress/high", methods=["GET"])
def analysis_detect_high_stress():
    """
    连续高压检测：返回连续两周压力 >= 阈值的事件列表。
    Query: threshold (默认 4), module_id (可选), include_inactive (可选: true/false)
    """
    threshold = request.args.get("threshold", default=4, type=int)
    module_id = request.args.get("module_id", type=int)
    include_inactive = _to_bool(request.args.get("include_inactive", "false"))

    service = AnalysisServiceRepository()
    try:
        data = service.detect_consecutive_high_stress(
            threshold=threshold,
            module_id=module_id,
            include_inactive=include_inactive,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500


# -----------------------------
# 功能：自动创建预警记录
# -----------------------------
@analysis_bp.route("/analysis/alerts/generate", methods=["POST"])
def analysis_generate_alerts():
    """
    自动创建预警：基于连续高压结果写入 alerts。
    Query/Body: threshold (默认 4), module_id (可选), include_inactive (可选: true/false), clear_old (默认 true)
    """
    threshold = request.values.get("threshold", default=4, type=int)
    module_id = request.values.get("module_id", type=int)
    include_inactive = _to_bool(request.values.get("include_inactive", "false"))
    clear_old = _to_bool(request.values.get("clear_old", "true"))

    service = AnalysisServiceRepository()
    try:
        data = service.create_high_stress_alerts(
            threshold=threshold,
            module_id=module_id,
            include_inactive=include_inactive,
            clear_old=clear_old,
        )
        return jsonify(JsonHelper.success_dict(data))
    except Exception as e:
        return jsonify(JsonHelper.error_dict(f"failed: {e}")), 500

# ------------------------------------------------------------
# 可视化接口汇总（前端常用）：
# 1) 出勤率柱状图：
#    GET /analysis/attendance/averages
#    参数：module_id（可选），include_inactive（可选）
# 2) 成绩分布饼图：
#    GET /analysis/grades/distribution
#    参数：module_id（可选），include_inactive（可选）
# 3) 压力与成绩散点图：
#    GET /analysis/stress-grade/pairs
#    参数：module_id（可选），include_inactive（可选）
# ------------------------------------------------------------
