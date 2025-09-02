# app/services/auth_service.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid
import traceback

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, AuthResponse, UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, request: UserRegister) -> AuthResponse:
        """Register a new user with proper error handling"""
        try:
            print(f"[AUTH SERVICE] Starting registration for: {request.email}")

            # Check if user already exists
            existing_user = (
                self.db.query(User).filter(User.email == request.email).first()
            )

            if existing_user:
                print(f"[AUTH SERVICE] User already exists: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Create new user
            hashed_pwd = hash_password(request.password)

            new_user = User(
                id=uuid.uuid4(),
                email=request.email,
                hashed_password=hashed_pwd,
                first_name=request.first_name,
                last_name=request.last_name,
                role=(
                    request.role
                    if hasattr(request, "role") and request.role
                    else "user"
                ),
                is_active=True,
                created_at=datetime.utcnow(),
                subscription_status="free",
            )

            # Add to database
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            print(f"[AUTH SERVICE] User created successfully: {new_user.email}")

            # Create access token
            access_token = create_access_token(
                data={"user_id": str(new_user.id), "email": new_user.email}
            )

            # Create response
            user_response = UserResponse(
                id=str(new_user.id),
                email=new_user.email,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                role=new_user.role,
                is_active=new_user.is_active,
                created_at=new_user.created_at,
                subscription_status=new_user.subscription_status,
            )

            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response,
                message="Registration successful",
            )

        except IntegrityError as e:
            self.db.rollback()
            print(f"[AUTH SERVICE ERROR] Database integrity error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists or database constraint violated",
            )
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            print(
                f"[AUTH SERVICE ERROR] Unexpected error during registration: {str(e)}"
            )
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}",
            )

    async def login_user(self, request: UserLogin) -> AuthResponse:
        """Authenticate user and return token"""
        try:
            print(f"[AUTH SERVICE] Login attempt for: {request.email}")

            # Find user by email
            user = self.db.query(User).filter(User.email == request.email).first()

            if not user:
                print(f"[AUTH SERVICE] User not found: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # Verify password
            if not verify_password(request.password, user.hashed_password):
                print(f"[AUTH SERVICE] Invalid password for: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # Check if user is active
            if not user.is_active:
                print(f"[AUTH SERVICE] Inactive user attempted login: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive. Please contact support.",
                )

            print(f"[AUTH SERVICE] Login successful for: {request.email}")

            # Create access token
            access_token = create_access_token(
                data={"user_id": str(user.id), "email": user.email}
            )

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

            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response,
                message="Login successful",
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"[AUTH SERVICE ERROR] Unexpected error during login: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}",
            )
