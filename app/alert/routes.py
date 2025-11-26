from . import alert_bp
from .services import *


@alert_bp.route("/alert-test")
def alert_test_route():
    msg = test()
    print(msg)
    return {
        "msg": msg,
    }

