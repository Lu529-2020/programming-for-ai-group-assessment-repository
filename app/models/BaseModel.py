from abc import ABC
from dataclasses import dataclass
from typing import Optional


# =========================================================
# 1. 抽象父类：所有模型共享的基础字段
# =========================================================
@dataclass
class BaseModel(ABC):
    """
    所有模型类的父类。
    展示 OOP 的继承结构。
    """
    id: Optional[int] = None
    created_at: Optional[str] = None  # ISO8601 时间戳，可选
    is_active: bool = True  # 用来做逻辑删除



