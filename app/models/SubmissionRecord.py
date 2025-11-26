from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 8. SubmissionRecord（继承 BaseModel）
# =========================================================
@dataclass
class SubmissionRecord(BaseModel):
    student_id: int = 0
    module_id: int = 0
    assessment_name: str = ""
    due_date: Optional[str] = None
    submitted_date: Optional[str] = None
    is_submitted: bool = False
    is_late: bool = False

