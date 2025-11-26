from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.BaseModel import BaseModel


# =========================================================
# 5. Module（继承 BaseModel）
# =========================================================
@dataclass
class Module(BaseModel):
    module_code: str = ""
    module_title: str = ""
    credit: Optional[int] = None
    academic_year: Optional[str] = None

