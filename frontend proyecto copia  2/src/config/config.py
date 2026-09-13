import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "billeterapp-frontend-development-secret-change-me",
    )
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api/v1").rstrip("/")
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"


class DevelopmentConfig(Config):
    DEBUG = os.getenv("DEBUG", "1").lower() in {"1", "true", "yes", "on"}


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}