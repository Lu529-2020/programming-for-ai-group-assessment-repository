from dataclasses import dataclass
from typing import Optional, Literal

from app.models.Person import Person

# =========================================================
# 3. User（继承 Person）
# =========================================================

Role = Literal["admin", "course_director", "wellbeing_officer"]

@dataclass
class User(Person):
    """
    对应 users 表
    """
    username: str = ""
    password_hash: str = ""
    role: Role = "admin"