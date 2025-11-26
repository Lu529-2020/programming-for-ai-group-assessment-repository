from dataclasses import dataclass
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# StressEvent（单次高压力事件）
# =========================================================
@dataclass
class StressEvent(BaseModel):
    """
    对应表：stress_events
    字段：
        id, student_id, module_id, survey_response_id, week_number,
        stress_level, cause_category, description, source,
        created_at, is_active
    """
    student_id: int = 0
    module_id: Optional[int] = None
    survey_response_id: Optional[int] = None
    week_number: Optional[int] = None
    stress_level: int = 0                 # 1~5
    cause_category: str = ""              # "academic"/"personal"/"health"/"financial"/"other"
    description: Optional[str] = None
    source: str = "system"                # "system"/"student"/"staff"
