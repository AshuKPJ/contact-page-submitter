from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import sys

from app.core.config import settings

# Create engine without fallback
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args=(
            {"sslmode": "require", "connect_timeout": 10}
            if "postgresql" in settings.DATABASE_URL
            else {}
        ),
    )

    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    print(f"[DATABASE] Connected to PostgreSQL successfully")

except Exception as e:
    print(f"[DATABASE ERROR] Cannot connect to database: {e}")
    print(f"[DATABASE] Connection string: {settings.DATABASE_URL[:50]}...")
    sys.exit(1)  # Exit instead of falling back

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
    Base.metadata.create_all(bind=engine)
    print("[DATABASE] Tables initialized")
