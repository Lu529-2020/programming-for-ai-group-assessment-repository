from . import analysis_bp
from .services import *


@analysis_bp.route("/analysis-test")
def analysis_test_route():
    analysis_service_repository = AnalysisServiceRepository()
    msg = analysis_service_repository.test()
    print(msg)
    return {
        "msg": msg,
    }

