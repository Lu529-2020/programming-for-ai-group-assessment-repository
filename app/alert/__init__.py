from flask import Blueprint

alert_bp = Blueprint("alert", __name__)

from . import routes   # 必须放在后面，避免循环引用