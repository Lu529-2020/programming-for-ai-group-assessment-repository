from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 9. SurveyResponse（继承 BaseModel）
# =========================================================
@dataclass
class SurveyResponse(BaseModel):
    student_id: int = 0
    module_id: Optional[int] = None
    week_number: int = 0
    stress_level: int = 0
    hours_slept: Optional[float] = None
    mood_comment: Optional[str] = None

