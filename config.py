import os
from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    # Application settings
    SECRET_KEY = os.environ.get("SESSION_SECRET", "default-dev-secret")

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Upload settings
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "static/uploads")

    # AI settings
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    # Rotate through all available Gemini API keys
    GEMINI_API_KEYS = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 11)]
    # Model to use
    GEMINI_MODEL_NAME = os.environ.get("GEMINI_PRO_MODEL", "gemini-2.0-flash-lite")
    # RAG settings
    RAG_MODEL_NAME = os.environ.get("RAG_MODEL_NAME", "all-MiniLM-L6-v2")
    RAG_INDEX_PATH = os.environ.get("RAG_INDEX_PATH", "rag.index")
    RAG_TEXTS_PATH = os.environ.get("RAG_TEXTS_PATH", "rag_texts.npy")
    RAG_K = int(os.environ.get("RAG_K", "5"))

class DevConfig(Config):
    DEBUG = True
    # Dev fallback to local SQLite if DATABASE_URL unset
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///expense_tracker.db")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

class ProdConfig(Config):
    DEBUG = False
