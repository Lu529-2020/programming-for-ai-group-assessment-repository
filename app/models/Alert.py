from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 11. Alert（继承 BaseModel）
# =========================================================
@dataclass
class Alert(BaseModel):
    student_id: int = 0
    module_id: Optional[int] = None
    week_number: Optional[int] = None
    reason: str = ""
    resolved: bool = False
    severity: str = "medium"  # not stored in DB yet; used for API/UI defaults
