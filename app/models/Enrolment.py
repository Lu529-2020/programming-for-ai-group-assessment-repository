from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 6. Enrolment（继承 BaseModel）
# =========================================================
@dataclass
class Enrolment(BaseModel):
    student_id: int = 0
    module_id: int = 0
    enrol_date: Optional[str] = None


