from . import analysis_bp
from .services import *


@analysis_bp.route("/analysis-test")
def analysis_test_route():
    msg = test()
    print(msg)
    return {
        "msg": msg,
    }

