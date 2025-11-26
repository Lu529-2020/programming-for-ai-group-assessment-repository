from . import auth_bp
from .services import *


@auth_bp.route("/auth-test")
def test_route():
    msg = test()
    print(msg)
    return {
        "msg": msg,
    }


@auth_bp.route("/")
def index():
    return "index"

