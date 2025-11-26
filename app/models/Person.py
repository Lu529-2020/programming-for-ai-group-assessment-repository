from abc import ABC
from dataclasses import dataclass
from typing import Optional

from app.models.BaseModel import BaseModel


@dataclass
class Person(BaseModel, ABC):
    """
    抽象类：表示具有姓名和邮件属性的所有“人”类。
    """
    full_name: str = ""
    email: Optional[str] = None
