"""
Database configuration and session management for Restaurant AI Chatbot.

This module provides SQLAlchemy setup for storing conversation history
and session data using SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL - stores in data/ directory (mounted volume in Docker)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/conversations.db"

# Create engine with SQLite-specific options
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,  # Set to True for SQL query logging during development
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.post("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    This should be called once at application startup.
    It's safe to call multiple times - existing tables won't be recreated.
    """
    # Import models here to avoid circular imports
    from app.models import DBSession, DBMessage  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
