import os

class Config:
    SECRET_KEY = "qurio_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
