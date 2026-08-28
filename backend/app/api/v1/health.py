from fastapi import APIRouter
from app.config import settings
from app.database import db, USE_POSTGRES

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def check_health():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database": "PostgreSQL + pgvector" if USE_POSTGRES else "SQLite + Vector Engine (Standalone Fallback)",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "documents_count": len(db.list_documents()),
        "total_indexed_chunks": len(db.get_all_chunks())
    }
