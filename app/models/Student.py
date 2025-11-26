from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC

from app.models.Person import Person


# =========================================================
# 4. Student（继承 Person）
# =========================================================
@dataclass
class Student(Person):
    """
    对应 students 表
    """
    student_number: str = ""
    course_name: Optional[str] = None
    year_of_study: Optional[int] = None

