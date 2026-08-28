import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Multi-Vector Hybrid RAG Engine"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hybrid_rag"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_CELERY: bool = False

    # Gemini & AI
    GEMINI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = 768
    LLM_MODEL: str = "gemini-2.5-flash"

    # RAG Settings
    DEFAULT_CHUNK_SIZE: int = 512
    DEFAULT_CHUNK_OVERLAP: int = 50
    RRF_K: int = 60
    DEFAULT_TOP_K: int = 10
    DEFAULT_TOP_N: int = 5
    RERANK_THRESHOLD: float = 0.3

    # Storage directory for uploaded documents
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
