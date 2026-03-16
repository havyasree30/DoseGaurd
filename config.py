import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-keep-safe'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///doseguard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
