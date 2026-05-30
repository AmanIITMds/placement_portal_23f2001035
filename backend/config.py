import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "ppa-secret-key-23f2001035"
    JWT_SECRET_KEY = "ppa-jwt-secret-23f2001035"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_DEFAULT_TIMEOUT = 300

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""