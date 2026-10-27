from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# The engine manages the connection to PostgreSQL.
# pool_pre_ping checks a connection is alive before using it.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Each request gets its own "session" (a temporary workspace for talking to the DB).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All our database models (Phase 4) will inherit from this."""
    pass


def get_db():
    """FastAPI dependency: open a session for one request, always close it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()