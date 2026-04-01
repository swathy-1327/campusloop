import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.main import main_bp
    from app.routes.marketplace import marketplace_bp
    from app.routes.requests import requests_bp
    from app.routes.verification import verification_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(marketplace_bp, url_prefix="/marketplace")
    app.register_blueprint(requests_bp, url_prefix="/requests")
    app.register_blueprint(verification_bp, url_prefix="/verification")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()

    return app
