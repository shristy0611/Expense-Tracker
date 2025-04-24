import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

class DevConfig(BaseConfig):
    """
    Development configuration.
    - Enables debug mode.
    - Enables Flask-Profiler for local performance analysis.
    """
    DEBUG = True
    FLASK_DEBUG = 1
    # Performance profiling configuration for development
    FLASK_PROFILER = {
        "enabled": True,
        "storage": {
            "engine": "sqlite",
            "db_path": "flask_profiler.sqlite"
        },
        "endpointRoot": "profiler",
        "basicAuth": {"enabled": False}
    }

class TestConfig(BaseConfig):
    """
    Testing configuration.
    - Enables testing mode.
    - Disables debug mode.
    """
    TESTING = True
    DEBUG = False

class ProdConfig(BaseConfig):
    """
    Production configuration.
    - Disables debug and testing modes.
    """
    DEBUG = False
    TESTING = False
