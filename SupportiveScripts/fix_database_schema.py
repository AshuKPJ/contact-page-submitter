# backend/fix_database_schema.py
"""
Script to add missing columns to the database tables.
Run this to fix the schema mismatch issues.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_subscription_plans_table():
    """Add missing description column to subscription_plans table if it doesn't exist."""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()

        try:
            # Check if description column exists
            result = conn.execute(
                text(
                    """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'subscription_plans' 
                AND column_name = 'description'
            """
                )
            )

            if not result.fetchone():
                logger.info(
                    "Adding 'description' column to subscription_plans table..."
                )
                conn.execute(
                    text(
                        """
                    ALTER TABLE subscription_plans 
                    ADD COLUMN IF NOT EXISTS description VARCHAR(500)
                """
                    )
                )
                logger.info("✅ Added 'description' column successfully")
            else:
                logger.info("✅ 'description' column already exists")

            # Commit the transaction
            trans.commit()

        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Failed to add column: {e}")
            raise


def add_default_subscription_plan():
    """Add a default free plan if no plans exist."""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # Check if any plans exist
            result = conn.execute(text("SELECT COUNT(*) FROM subscription_plans"))
            count = result.scalar()

            if count == 0:
                logger.info("Adding default 'Free' subscription plan...")
                conn.execute(
                    text(
                        """
                    INSERT INTO subscription_plans (
                        id, name, description, max_websites, max_submissions_per_day,
                        max_campaigns, price, currency, is_active, created_at
                    ) VALUES (
                        '00000000-0000-0000-0000-000000000000'::uuid,
                        'Free', 
                        'Basic free plan',
                        10,
                        50,
                        3,
                        0.00,
                        'USD',
                        true,
                        NOW()
                    )
                """
                    )
                )
                logger.info("✅ Added default Free plan")
            else:
                logger.info(f"✅ Found {count} existing subscription plans")

            trans.commit()

        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Failed to add default plan: {e}")


def main():
    logger.info("=" * 60)
    logger.info("DATABASE SCHEMA FIX SCRIPT")
    logger.info("=" * 60)

    try:
        # Test connection
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")

        # Fix subscription_plans table
        fix_subscription_plans_table()

        # Add default plan
        add_default_subscription_plan()

        logger.info("=" * 60)
        logger.info("✅ DATABASE SCHEMA FIXED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Failed to fix database schema: {e}")
        raise


if __name__ == "__main__":
    main()
# backend/update_passwords.py