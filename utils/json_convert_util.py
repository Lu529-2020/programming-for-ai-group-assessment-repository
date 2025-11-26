# app/utils/json_helper.py
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Union
import json


"""
使用方法：

将需要传递的对象实例或对象集合以键值对的形式封装到字典中：
payload = {
    "user": user_obj,                  # dataclass User
    "attendances": attendance_list,    # list[Attendance]
}
然后使用result获取结果：
result = JsonHelper.success_json(payload, ensure_ascii=False)

前端将会得到的结构类似于：
{
  "success": true,
  "message": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    },
    "attendances": [
      {
        "id": 1,
        "student_id": 1,
        "module_id": 101,
        "week_number": 1,
        "status": "present"
      },
      {
        "id": 2,
        "student_id": 1,
        "module_id": 101,
        "week_number": 2,
        "status": "absent"
      }
    ]
  }
}

"""


class JsonHelper:
    """
    通用 JSON 工具类：
    - 负责把对象 / 对象集合 转换为可 JSON 序列化的 Python 结构（dict / list / 基本类型）
    - 提供 success_dict / error_dict（返回 Python dict）
    - 提供 success_json / error_json（返回 JSON 字符串）
    - 不依赖 Flask
    """

    @staticmethod
    def to_serializable(obj: Any) -> Any:
        """
        将任意对象递归转换为可被 json.dumps 处理的结构：
        - dataclass -> dict
        - list -> 列表中每个元素递归处理
        - dict -> 每个 value 递归处理
        - None / 基本类型 -> 直接返回
        """
        # None 直接返回
        if obj is None:
            return None

        # 列表：递归处理每个元素
        if isinstance(obj, list):
            return [JsonHelper.to_serializable(item) for item in obj]

        # dataclass 对象：转为字典
        if is_dataclass(obj):
            return asdict(obj)

        # 字典：递归处理 value
        if isinstance(obj, dict):
            return {k: JsonHelper.to_serializable(v) for k, v in obj.items()}

        # 其他基础类型（int、str、float、bool等）直接返回
        return obj

    # ======================
    #   success / error（返回 dict）
    # ======================
    @staticmethod
    def success_dict(data: Any = None, message: str = "success") -> Dict[str, Any]:
        """
        构造一个表示“成功”的响应字典结构：
        {
            "success": True,
            "message": "...",
            "data": <序列化后的数据>
        }
        """
        return {
            "success": True,
            "message": message,
            "data": JsonHelper.to_serializable(data),
        }

    @staticmethod
    def error_dict(message: str = "error", details: Any = None) -> Dict[str, Any]:
        """
        构造一个表示“失败”的响应字典结构：
        {
            "success": False,
            "message": "...",
            "details": <序列化后的详情>
        }
        """
        return {
            "success": False,
            "message": message,
            "details": JsonHelper.to_serializable(details),
        }

    # ======================
    #   success / error（返回 JSON 字符串）
    # ======================
    @staticmethod
    def success_json(data: Any = None, message: str = "success", **json_kwargs) -> str:
        """
        构造“成功”响应的 JSON 字符串。
        json_kwargs 会传给 json.dumps，例如 ensure_ascii=False 等。
        """
        return json.dumps(
            JsonHelper.success_dict(data=data, message=message),
            **json_kwargs,
        )

    @staticmethod
    def error_json(message: str = "error", details: Any = None, **json_kwargs) -> str:
        """
        构造“失败”响应的 JSON 字符串。
        """
        return json.dumps(
            JsonHelper.error_dict(message=message, details=details),
            **json_kwargs,
        )
