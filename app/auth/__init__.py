from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from . import routes   # 必须放在后面，避免循环引用