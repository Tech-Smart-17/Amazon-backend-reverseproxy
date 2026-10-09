"""
Application Configuration settings loaded via Pydantic BaseSettings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Amazon Backend System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretjwtkeyforamazonbackendenterprise2026productionuseonly!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "sqlite+aiosqlite:///./amazon_backend.db"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "amazon_mongo_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CHROMADB_DIR: str = "./uploads/chromadb_store"
    UPLOAD_DIR: str = "./uploads"
    INVOICE_DIR: str = "./uploads/invoice"
    LOG_DIR: str = "./uploads/logs"

    # LangChain AI features initialize lazily and are optional for core API use.
    LANGCHAIN_CHAT_MODEL: str = "google_genai:gemini-3.7-flash"
    LANGCHAIN_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    GOOGLE_API_KEY: str = ""
    LANGCHAIN_CHUNK_SIZE: int = 800
    LANGCHAIN_CHUNK_OVERLAP: int = 120
    KNOWLEDGE_UPLOAD_MAX_BYTES: int = 20_000_000

    ASSEMBLYAI_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""
    CARTESIA_VOICE_ID: str = "a0e99841-438c-4a64-b679-ae501e7d6091"
    CARTESIA_MODEL_ID: str = "sonic-latest"
    CARTESIA_VERSION: str = "2026-08-14"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()


# Ensure required directories exist
for path in [settings.UPLOAD_DIR, settings.INVOICE_DIR, settings.LOG_DIR, settings.CHROMADB_DIR]:
    os.makedirs(path, exist_ok=True)
