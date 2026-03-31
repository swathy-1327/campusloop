import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://swathy2006malu_db_user:zyLwmybpsYhi6dyY@cluster0.xs0banz.mongodb.net/?appName=Cluster0",
    )
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "campusloop")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join("static", "uploads"))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
