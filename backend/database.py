"""
TRUVEX Database Connection Module.
Owner: Rounit
Status: Phase 1 Placeholder
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./truvex.db")

# SQLite connection args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to retrieve database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
