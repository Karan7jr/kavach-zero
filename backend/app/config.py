
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class Config:

    APP_NAME = "KAVACH ZERO 2.0"

    APP_VERSION = "0.1.0"

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    PRIVATE_STORAGE = str(
        BASE_DIR / "backend" / "private_storage"
    )

    FILE_ENCRYPTION_KEY = os.getenv(
        "FILE_ENCRYPTION_KEY"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        os.getenv(
            "SESSION_COOKIE_SECURE", "true"
        ).lower() == "true"
    )

    DEBUG = False
