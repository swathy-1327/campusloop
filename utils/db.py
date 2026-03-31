from datetime import datetime, timezone

from pymongo import MongoClient


def init_db(app):
    client = MongoClient(app.config["MONGO_URI"])
    db = client[app.config["MONGO_DB_NAME"]]
    app.extensions["mongo_client"] = client
    app.extensions["mongo_db"] = db
    app.extensions["now"] = lambda: datetime.now(timezone.utc)

    db.users.create_index("email", unique=True)
    db.products.create_index([("title", "text"), ("description", "text")])


def get_db():
    from flask import current_app

    return current_app.extensions["mongo_db"]
