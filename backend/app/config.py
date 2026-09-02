import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/gestion_almacen_dev",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "solo-desarrollo-cambiar")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    JSON_SORT_KEYS = False

