import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True

class TestConfig(BaseConfig):
    FLASK_ENV = 'testing'
    TESTING = True

class ProdConfig(BaseConfig):
    FLASK_ENV = 'production'
    DEBUG = False
