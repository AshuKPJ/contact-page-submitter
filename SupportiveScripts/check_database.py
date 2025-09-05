# check_database.py - Run this to verify your database structure
import psycopg2
from app.core.config import settings
from sqlalchemy import create_engine, inspect


def check_database_structure():
    """Check the actual database structure vs your models"""

    print("=" * 60)
    print("DATABASE STRUCTURE CHECK")
    print("=" * 60)

    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)

    # Check users table
    print("\n📋 USERS TABLE COLUMNS:")
    print("-" * 40)

    columns = inspector.get_columns("users")
    for col in columns:
        print(
            f"  • {col['name']:20} {col['type']} {'(nullable)' if col['nullable'] else '(required)'}"
        )

    # Check if problematic columns exist
    column_names = [col["name"] for col in columns]

    print("\n✅ STATUS CHECK:")
    print("-" * 40)

    # Check for expected columns
    expected_columns = {
        "id": "✅" if "id" in column_names else "❌",
        "email": "✅" if "email" in column_names else "❌",
        "hashed_password": "✅" if "hashed_password" in column_names else "❌",
        "first_name": "✅" if "first_name" in column_names else "❌",
        "last_name": "✅" if "last_name" in column_names else "❌",
        "role": "✅" if "role" in column_names else "❌",
        "is_active": "✅" if "is_active" in column_names else "❌",
        "created_at": "✅" if "created_at" in column_names else "❌",
        "updated_at": "✅" if "updated_at" in column_names else "❌",
        "plan_id": "✅" if "plan_id" in column_names else "❌",
    }

    for col, status in expected_columns.items():
        print(f"  {status} {col}")

    # Check for columns that shouldn't exist
    print("\n⚠️  COLUMNS TO CHECK:")
    print("-" * 40)

    if "hashed_password" in column_names:
        print("  ❌ 'hashed_password' exists (should be 'hashed_password')")
    else:
        print("  ✅ 'hashed_password' doesn't exist (correct)")

    if "is_verified" in column_names:
        print("  ⚠️  'is_verified' exists in DB but not in updated model")
    else:
        print("  ✅ 'is_verified' doesn't exist (correct)")

    # Check subscription_plans table if it exists
    if "subscription_plans" in inspector.get_table_names():
        print("\n📋 SUBSCRIPTION_PLANS TABLE:")
        print("-" * 40)
        sub_columns = inspector.get_columns("subscription_plans")
        for col in sub_columns[:5]:  # Show first 5 columns
            print(f"  • {col['name']:20} {col['type']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    check_database_structure()
