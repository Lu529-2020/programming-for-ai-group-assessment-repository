from . import alert_bp
from .services import *


@alert_bp.route("/alert-test")
def alert_test_route():
    alert_service_repository = AlertServiceRepository()
    msg = alert_service_repository.test()
    print(msg)
    return {
        "msg": msg,
    }

