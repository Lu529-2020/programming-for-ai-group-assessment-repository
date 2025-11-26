from flask import Blueprint

analysis_bp = Blueprint("analysis", __name__)

from . import routes   # 必须放在后面，避免循环引用