import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import command
from alembic.config import Config
from app.core.database import engine
from app.models import Base


def run_migrations():
    """Run database migrations"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database migrations completed")


if __name__ == "__main__":
    run_migrations()
