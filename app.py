import os

from flask import Flask

from config import Config
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.product_routes import product_bp
from routes.request_routes import request_bp
from utils.auth import current_user
from utils.db import init_db
from utils.helpers import format_currency, format_datetime, trust_badge_class


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db(app)

    app.jinja_env.filters["currency"] = format_currency
    app.jinja_env.filters["datetime"] = format_datetime
    app.jinja_env.filters["trust_badge_class"] = trust_badge_class

    @app.context_processor
    def inject_current_user():
        return {"current_user": current_user()}

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
