import os

import click
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

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

    @app.get("/health")
    def health():
        app.extensions["mongo_db"].command("ping")
        return jsonify(status="ok"), 200

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.option("--name", prompt=True)
    @click.option("--phone", prompt=True)
    def create_admin(email, name, phone):
        """Create an administrator or promote an existing account."""
        from models.user_model import create_user, find_user_by_email

        email = email.strip().lower()
        user = find_user_by_email(email)
        if user:
            app.extensions["mongo_db"].users.update_one(
                {"_id": user["_id"]}, {"$set": {"role": "admin", "account_status": "active"}}
            )
            click.echo(f"Administrator access enabled for {email}.")
            return

        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        user = create_user(name=name.strip(), email=email, phone=phone.strip(), password=password)
        app.extensions["mongo_db"].users.update_one(
            {"_id": user["_id"]}, {"$set": {"role": "admin"}}
        )
        click.echo(f"Administrator account created for {email}.")

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
