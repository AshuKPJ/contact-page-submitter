# app/services/auth_service.py

from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import traceback

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, AuthResponse, UserResponse


class AuthService:
    """Enhanced authentication service with comprehensive logging"""

    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> AuthResponse:
        """Register a new user with detailed logging"""

        # Log registration attempt
        print(f"[AUTH SERVICE] 📝 Registration attempt started")
        print(f"[AUTH SERVICE] Email: {user_data.email}")
        print(f"[AUTH SERVICE] First Name: {user_data.first_name}")
        print(f"[AUTH SERVICE] Last Name: {user_data.last_name}")

        try:
            # Check if user already exists
            print(f"[AUTH SERVICE] 🔍 Checking if user already exists...")
            existing_user = (
                self.db.query(User)
                .filter(User.email == user_data.email.lower())
                .first()
            )

            if existing_user:
                print(f"[AUTH SERVICE] ❌ User already exists: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            print(f"[AUTH SERVICE] ✅ Email available for registration")

            # Hash password
            print(f"[AUTH SERVICE] 🔐 Hashing password...")
            hashed_password = hash_password(user_data.password)
            print(f"[AUTH SERVICE] ✅ Password hashed successfully")

            # Create user
            print(f"[AUTH SERVICE] 👤 Creating user record...")
            db_user = User(
                email=user_data.email.lower(),
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role="user",
                is_active=True,
                created_at=datetime.utcnow(),
                subscription_status="free",
            )

            self.db.add(db_user)
            self.db.flush()  # Get the ID
            print(f"[AUTH SERVICE] ✅ User created with ID: {db_user.id}")

            # Create access token
            print(f"[AUTH SERVICE] 🎫 Creating access token...")
            access_token = create_access_token(
                data={"user_id": str(db_user.id)}, expires_delta=timedelta(hours=24)
            )
            print(f"[AUTH SERVICE] ✅ Access token created")

            self.db.commit()
            print(f"[AUTH SERVICE] 💾 User registration committed to database")

            # Create response
            user_response = UserResponse(
                id=str(db_user.id),
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                role=db_user.role,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                subscription_status=db_user.subscription_status,
            )

            result = AuthResponse(
                access_token=access_token, token_type="bearer", user=user_response
            )

            print(
                f"[AUTH SERVICE] 🎉 Registration completed successfully for: {user_data.email}"
            )
            return result

        except HTTPException as e:
            print(f"[AUTH SERVICE] ⚠️ Registration failed (expected): {e.detail}")
            self.db.rollback()
            raise
        except Exception as e:
            print(f"[AUTH SERVICE] ❌ Registration failed (unexpected): {str(e)}")
            print(f"[AUTH SERVICE] 📍 Traceback:")
            traceback.print_exc()
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed due to internal error",
            )

    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Authenticate user with detailed logging"""

        print(f"[AUTH SERVICE] 🔑 Login attempt started")
        print(f"[AUTH SERVICE] Email: {login_data.email}")

        try:
            # Find user
            print(f"[AUTH SERVICE] 🔍 Looking up user in database...")
            user = (
                self.db.query(User)
                .filter(User.email == login_data.email.lower())
                .first()
            )

            if not user:
                print(f"[AUTH SERVICE] ❌ User not found: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            print(f"[AUTH SERVICE] ✅ User found - ID: {user.id}")

            # Check if user is active
            if not user.is_active:
                print(f"[AUTH SERVICE] ❌ User account is inactive: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
                )

            print(f"[AUTH SERVICE] ✅ User account is active")

            # Verify password
            print(f"[AUTH SERVICE] 🔐 Verifying password...")
            if not verify_password(login_data.password, user.hashed_password):
                print(
                    f"[AUTH SERVICE] ❌ Password verification failed for: {login_data.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            print(f"[AUTH SERVICE] ✅ Password verified successfully")

            # Create access token
            print(f"[AUTH SERVICE] 🎫 Creating access token...")
            access_token = create_access_token(
                data={"user_id": str(user.id)}, expires_delta=timedelta(hours=24)
            )
            print(f"[AUTH SERVICE] ✅ Access token created")

            # Create response
            user_response = UserResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                subscription_status=user.subscription_status,
            )

            result = AuthResponse(
                access_token=access_token, token_type="bearer", user=user_response
            )

            print(
                f"[AUTH SERVICE] 🎉 Login completed successfully for: {login_data.email}"
            )
            print(
                f"[AUTH SERVICE] 📊 User role: {user.role}, Status: {user.subscription_status}"
            )

            return result

        except HTTPException as e:
            print(f"[AUTH SERVICE] ⚠️ Login failed (expected): {e.detail}")
            raise
        except Exception as e:
            print(f"[AUTH SERVICE] ❌ Login failed (unexpected): {str(e)}")
            print(f"[AUTH SERVICE] 📍 Traceback:")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed due to internal error",
            )

    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID with logging"""
        print(f"[AUTH SERVICE] 🔍 Looking up user by ID: {user_id[:8]}...")

        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                print(f"[AUTH SERVICE] ✅ User found: {user.email}")
            else:
                print(f"[AUTH SERVICE] ❌ User not found for ID: {user_id[:8]}...")
            return user
        except Exception as e:
            print(f"[AUTH SERVICE] ❌ Database error looking up user: {str(e)}")
            return None
