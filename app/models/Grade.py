from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 10. Grade（继承 BaseModel）
# =========================================================
@dataclass
class Grade(BaseModel):
    student_id: int = 0
    module_id: int = 0
    assessment_name: str = ""
    grade: Optional[float] = None
