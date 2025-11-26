from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 7. AttendanceRecord（继承 BaseModel）
# =========================================================
@dataclass
class AttendanceRecord(BaseModel):
    student_id: int = 0
    module_id: int = 0
    week_number: int = 0
    attended_sessions: Optional[int] = None
    total_sessions: Optional[int] = None
    attendance_rate: Optional[float] = None
