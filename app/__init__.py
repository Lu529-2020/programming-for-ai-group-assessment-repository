from flask import Flask
from .auth import auth_bp
from .analysis import analysis_bp
from .alert import alert_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    app.register_blueprint(alert_bp, url_prefix="/alert")

    return app