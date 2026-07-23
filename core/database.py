"""
Database setup: SQLAlchemy engine, session factory, and declarative base.

Why SQLAlchemy instead of raw sqlite3:
FAISS will store vectors and integer IDs only — it has no concept of which
document or chunk a vector belongs to. That metadata (document name, upload
date, raw chunk text, FAISS-id mapping) needs a proper relational table.
SQLAlchemy's ORM lets future modules define that as plain Python classes
instead of hand-written SQL scattered across the codebase.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings

# The engine manages the actual connection pool to the SQLite file.
# `check_same_thread=False` is required for SQLite specifically, because
# FastAPI may handle a single request's DB session across async context —
# SQLite otherwise restricts a connection to the thread that created it.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# SessionLocal is a factory: calling SessionLocal() gives a new DB session.
# We don't create a global session, because sessions are not thread-safe
# and each request should get its own.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Base class that all future ORM models (Document, Chunk, ChatLog, etc.)
    will inherit from. SQLAlchemy uses this to track table metadata.
    """

    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session for a single request
    and guarantees it's closed afterward, even if an exception occurs.

    Usage in a future route:
        @router.get("/documents")
        def list_documents(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Creates all tables registered against `Base` at application startup.

    Note: this is fine for an internship prototype. A production system
    would use a migration tool (e.g. Alembic) instead of create_all, since
    create_all can't handle schema changes to existing tables.
    """
    Base.metadata.create_all(bind=engine)
