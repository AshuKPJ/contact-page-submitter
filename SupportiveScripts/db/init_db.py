# app/db/init_db.py
"""
Database initialization script to create test users
Run this file to populate your database with test users
"""

from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def init_test_users(db: Session):
    """Create test users if they don't exist"""

    test_users = [
        {
            "email": "admin@example.com",
            "password": "Admin@SecurePass123",
            "first_name": "Jane",
            "last_name": "Admin",
            "role": UserRole.ADMIN,
        },
        {
            "email": "user@example.com",
            "password": "User@SecurePass123",
            "first_name": "John",
            "last_name": "User",
            "role": UserRole.USER,
        },
        {
            "email": "owner@example.com",
            "password": "Owner@SecurePass123",
            "first_name": "Mike",
            "last_name": "Owner",
            "role": UserRole.OWNER,
        },
        {
            "email": "demo@example.com",
            "password": "Demo@Pass123",
            "first_name": "Demo",
            "last_name": "User",
            "role": UserRole.USER,
        },
        {
            "email": "testuser@example.com",
            "password": "Test@Pass123",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.USER,
        },
    ]

    for user_data in test_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()

        if not existing_user:
            # Create new user
            new_user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                hashed_password=hash_password(
                    user_data["password"]
                ),  # USING hashed_password
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=(
                    user_data["role"].value
                    if hasattr(user_data["role"], "value")
                    else str(user_data["role"])
                ),
                is_active=True,
                created_at=datetime.utcnow(),
                subscription_status="free",
            )

            db.add(new_user)
            print(
                f"✓ Created user: {user_data['email']} with password: {user_data['password']}"
            )
        else:
            print(f"→ User already exists: {user_data['email']}")

    db.commit()
    print("\n✓ Test users initialization complete!")
    print("\nYou can login with these credentials:")
    print("-" * 40)
    for user_data in test_users:
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data['password']}")
        print(f"Role: {user_data['role'].value}")
        print("-" * 40)


def main():
    """Main function to initialize the database"""
    print("Initializing database with test users...")

    # Create a database session
    db = SessionLocal()

    try:
        init_test_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
