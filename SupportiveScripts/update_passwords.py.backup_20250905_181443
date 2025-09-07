# update_passwords_simple.py
"""
Simple password update script that avoids loading relationships
Save this in your backend folder and run: python update_passwords_simple.py
"""

import psycopg2
from app.core.config import settings
from app.core.security import hash_password
from urllib.parse import urlparse


def update_passwords_directly():
    """Update passwords using direct SQL to avoid ORM relationship issues"""

    print("=" * 60)
    print("DIRECT PASSWORD UPDATE")
    print("=" * 60)

    # Parse database URL
    db_url = urlparse(settings.DATABASE_URL)

    # Connect directly to PostgreSQL
    conn = psycopg2.connect(
        host=db_url.hostname,
        port=db_url.port or 5432,
        database=db_url.path[1:],  # Remove leading /
        user=db_url.username,
        password=db_url.password,
        sslmode="require",
    )
    cursor = conn.cursor()

    # Users and their new passwords
    users_to_update = [
        ("user@example.com", "UserPassword123!"),
        ("admin@example.com", "AdminPassword456!"),
        ("owner@example.com", "OwnerPassword789!"),
        ("testuser@example.com", "TestPassword123!"),
        ("demo@example.com", "DemoPassword123!"),
    ]

    print("\nUpdating passwords...")
    print("-" * 40)

    for email, password in users_to_update:
        try:
            # Hash the password
            hashed = hash_password(password)

            # Update the user's password
            cursor.execute(
                "UPDATE users SET hashed_password = %s WHERE email = %s",
                (hashed, email),
            )

            if cursor.rowcount > 0:
                print(f"✅ Updated: {email}")
            else:
                print(f"❌ User not found: {email}")

        except Exception as e:
            print(f"❌ Error updating {email}: {str(e)}")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("PASSWORD UPDATE COMPLETE!")
    print("=" * 60)

    print("\n📋 LOGIN CREDENTIALS:")
    print("-" * 40)

    for email, password in users_to_update:
        print(f"\nEmail: {email}")
        print(f"Password: {password}")

    print("\n" + "=" * 60)
    print("You can now login with these credentials!")
    print("=" * 60)


if __name__ == "__main__":
    update_passwords_directly()
