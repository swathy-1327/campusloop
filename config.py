import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    MONGO_URI = os.environ["MONGO_URI"]
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "campusloop")
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", str(Path(__file__).parent / "static" / "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
