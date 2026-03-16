from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.database import init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    JWTManager(app)

    # Initialize database
    init_db(config_class.DATABASE_URL)

    # Register blueprints
    from app.routes.wechat import wechat_bp
    from app.routes.auth import auth_bp
    from app.routes.cases import cases_bp

    app.register_blueprint(wechat_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cases_bp)

    return app
