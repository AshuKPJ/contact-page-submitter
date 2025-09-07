# backend/create_tables.py
"""
Script to create missing database tables.
Run this script to ensure all required tables exist in your database.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text
from app.core.database import engine, Base
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_and_create_tables():
    """Check existing tables and create missing ones."""

    # Import all models to ensure they're registered with Base
    from app.models import (
        User,
        UserProfile,
        UserProfile,
        Campaign,
        CampaignStatus,
        Website,
        Submission,
        SubmissionStatus,
        SubmissionLog,
        CaptchaLog,
        Settings,
        SystemLog,
        Log,
        SubscriptionPlan,
    )

    # Try to import optional models
    try:
        from app.models import Subscription

        logger.info("Subscription model imported successfully")
    except ImportError:
        logger.warning("Subscription model not found - skipping")

    # Get inspector to check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    logger.info(f"Existing tables in database: {existing_tables}")

    # Get all tables that should exist from our models
    all_tables = Base.metadata.tables.keys()
    logger.info(f"Tables defined in models: {list(all_tables)}")

    # Find missing tables
    missing_tables = set(all_tables) - set(existing_tables)

    if missing_tables:
        logger.info(f"Missing tables that will be created: {missing_tables}")

        # Create only the missing tables
        for table_name in missing_tables:
            table = Base.metadata.tables[table_name]
            table.create(engine, checkfirst=True)
            logger.info(f"Created table: {table_name}")
    else:
        logger.info("All required tables already exist")

    # Verify the creation
    inspector = inspect(engine)
    final_tables = inspector.get_table_names()
    logger.info(f"Final tables in database: {final_tables}")

    # Check if user_profiles table exists (the one that was missing)
    if "user_profiles" in final_tables:
        logger.info("✓ user_profiles table exists")
    else:
        logger.warning("✗ user_profiles table is still missing")

    return final_tables


def main():
    """Main function to run the table creation."""
    try:
        logger.info(
            f"Connecting to database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}"
        )

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Connected to PostgreSQL: {version}")

        # Check and create tables
        tables = check_and_create_tables()

        logger.info(f"\n✓ Database setup complete. Total tables: {len(tables)}")

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


if __name__ == "__main__":
    main()
