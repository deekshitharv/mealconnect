from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.session import get_db

router = APIRouter(tags=["General"])
logger = get_logger("general")


@router.get("/")
def root():
    """Simple API information."""
    return {
        "name": settings.app_name,
        "subtitle": settings.app_subtitle,
        "version": settings.app_version,
        "docs": "/docs",
    }


@router.get("/health")
def health_check():
    """Used to check that the server is running."""
    return {"status": "healthy"}


@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """Checks that the API can talk to PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Database health check failed")
        return {"status": "unhealthy", "database": "unreachable"}