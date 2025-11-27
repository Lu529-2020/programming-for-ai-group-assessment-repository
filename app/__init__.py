from flask import Flask
from flask_cors import CORS

from .auth import auth_bp
from .analysis import analysis_bp
from .alert import alert_bp
from .api import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    app.register_blueprint(alert_bp, url_prefix="/alert")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
