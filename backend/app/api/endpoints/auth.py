# app/api/endpoints/auth.py - FIXED JWT TOKEN CREATION

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, AuthResponse, UserResponse

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = (
            db.query(User).filter(User.email == request.email.lower()).first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=request.email.lower(),
            hashed_password=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role=request.role if hasattr(request, "role") else "user",
            is_active=True,
            created_at=datetime.utcnow(),
            subscription_status="free",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # FIXED: Create access token with "sub" field for JWT standard compliance
        access_token = create_access_token(
            data={
                "sub": user.email,  # JWT standard: "sub" (subject) field
                "user_id": str(user.id),  # Additional user info
                "email": user.email,  # Additional user info
            }
        )

        print(f"[AUTH SUCCESS] User registered: {user.email}")

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                subscription_status=user.subscription_status,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[AUTH ERROR] Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        print(f"[AUTH] Login attempt for: {request.email}")

        # Find user
        user = db.query(User).filter(User.email == request.email.lower()).first()

        if not user or not verify_password(request.password, user.hashed_password):
            print(f"[AUTH] Invalid credentials for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            print(f"[AUTH] Inactive account: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
            )

        # FIXED: Create access token with "sub" field for JWT standard compliance
        access_token = create_access_token(
            data={
                "sub": user.email,  # JWT standard: "sub" (subject) field
                "user_id": str(user.id),  # Additional user info
                "email": user.email,  # Additional user info
            }
        )

        print(f"[AUTH SUCCESS] User logged in: {user.email}")
        print(f"[AUTH] Token created with sub: {user.email}")

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                subscription_status=user.subscription_status,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH ERROR] Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again.",
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user_optional)):
    """Logout user"""
    if current_user:
        print(f"[AUTH] User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_optional),
):
    """Get current user info"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    print(f"[AUTH] Current user info requested: {current_user.email}")

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        subscription_status=current_user.subscription_status,
    )
