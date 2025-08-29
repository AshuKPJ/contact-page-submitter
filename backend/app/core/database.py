from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import sys

from app.core.config import settings

# Better error handling for database connection
try:
    # Create engine with connection test
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Test connections before using
        pool_size=5,
        max_overflow=10,
    )

    # Test the connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print(f"[DATABASE] Successfully connected to database")

except Exception as e:
    print(f"[DATABASE ERROR] Failed to connect to database: {e}")
    print(f"[DATABASE] Attempted URL: {settings.DATABASE_URL}")

    # Fallback to SQLite for development
    if settings.ENVIRONMENT == "development":
        print("[DATABASE] Falling back to SQLite for development")
        fallback_url = "sqlite:///./contact_submitter.db"
        engine = create_engine(fallback_url)
        print("[DATABASE] Using SQLite database")
    else:
        print(
            "[DATABASE] Cannot fallback in production. Please fix database connection."
        )
        sys.exit(1)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("[DATABASE] Database tables initialized successfully")
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to initialize tables: {e}")
        raise
