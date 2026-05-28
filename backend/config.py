import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret keys
    SECRET_KEY = "ppa-secret-key-23f2001035"
    JWT_SECRET_KEY = "ppa-jwt-secret-23f2001035"

    # Database - SQLite file will be created at backend/instance/placement.db
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis & Celery
    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    # Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # Mail (we'll fill this later for Celery jobs)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""