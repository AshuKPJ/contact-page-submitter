# app/api/auth.py
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# --- Project imports ---
from app.core.database import get_db
from app.models import User  # package import
from app.core.security import verify_password, hash_password, create_access_token
from app.core.dependencies import get_current_user

# --- Enhanced logging system ---
from app.logging import get_logger
from app.logging.core import user_id_var, request_id_var
from app.services.log_service import LogService

# NOTE: router has NO '/api' here; main.py attaches prefix '/api/auth'
router = APIRouter(tags=["auth"], redirect_slashes=False)

logger = get_logger("app.api.auth")

ALLOW_UNVERIFIED_LOGIN = os.getenv("AUTH_ALLOW_UNVERIFIED", "false").lower() == "true"
ALLOW_INACTIVE_LOGIN = os.getenv("AUTH_ALLOW_INACTIVE", "false").lower() == "true"


# =========================
# Schemas
# =========================


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(
        min_length=8, description="New password must be at least 8 characters"
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    model_config = {"from_attributes": True}


# =========================
# Helpers
# =========================


def _norm_email(e: Optional[str]) -> str:
    return (e or "").strip().lower()


def _get_client_ip(request: Request) -> Optional[str]:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real = request.headers.get("x-real-ip")
    if real:
        return real.strip()
    return request.client.host if request.client else None


def _get_safe_logger(db: Optional[Session]) -> LogService:
    try:
        return LogService(db)
    except Exception:

        class NoOp:
            def __getattr__(self, _):
                def noop(*a, **k):
                    return None

                return noop

        return NoOp()


def _user_to_public_dict(u: User) -> dict:
    return {
        "id": str(u.id),
        "email": u.email,
        "first_name": getattr(u, "first_name", None),
        "last_name": getattr(u, "last_name", None),
        "role": (
            getattr(u, "role", None)
            if not hasattr(u, "role") or isinstance(getattr(u, "role"), str)
            else str(getattr(u, "role"))
        ),
        "is_active": getattr(u, "is_active", True),
        "is_verified": getattr(u, "is_verified", False),
    }


def _log_auth_attempt(
    *,
    email: str,
    action: str,
    success: bool,
    ip_address: Optional[str] = None,
    failure_reason: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Optional[Session] = None,
):
    # structured logger
    logger.auth_event(
        action=action,
        email=email,
        success=success,
        ip_address=ip_address,
        failure_reason=failure_reason,
        user_id=user_id,
    )
    # legacy service
    try:
        svc = _get_safe_logger(db)
        svc.track_authentication(
            action=action,
            email=email,
            success=success,
            failure_reason=failure_reason,
            ip_address=ip_address,
        )
    except Exception:
        pass


# =========================
# Routes
# =========================


@router.get("/test")
def test_auth_router():
    logger.info("Auth test endpoint accessed")
    return {
        "status": "success",
        "message": "Auth router is working!",
        "timestamp": datetime.utcnow(),
        "request_id": request_id_var.get(),
    }


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    email = _norm_email(payload.email)
    ip = _get_client_ip(request)
    logger.info(
        f"Registration attempt for email: {email}",
        context={"email": email, "ip_address": ip, "event_type": "registration_start"},
    )

    # Duplicate?
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        _log_auth_attempt(
            email=email,
            action="register",
            success=False,
            ip_address=ip,
            failure_reason="email_already_exists",
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    now = datetime.utcnow()
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(
            "User created successfully",
            context={
                "user_id": str(user.id),
                "email": email,
                "event_type": "user_created",
            },
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "Integrity error during registration",
            context={"email": email, "error": str(e)},
        )
        _log_auth_attempt(
            email=email,
            action="register",
            success=False,
            ip_address=ip,
            failure_reason="database_integrity_error",
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    except Exception as exc:
        db.rollback()
        logger.exception(
            exc, context={"email": email, "event_type": "registration_error"}
        )
        _log_auth_attempt(
            email=email,
            action="register",
            success=False,
            ip_address=ip,
            failure_reason="database_error",
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    # Issue token (standard pattern)
    t0 = time.perf_counter()
    token = None
    try:
        token = create_access_token(data={"sub": email})
    except TypeError:
        # fallback forms if your helper expects a single positional or different key
        try:
            token = create_access_token({"sub": email})
        except TypeError:
            token = create_access_token(email)  # last resort
    jwt_ms = (time.perf_counter() - t0) * 1000.0

    _log_auth_attempt(
        email=email,
        action="register",
        success=True,
        ip_address=ip,
        user_id=str(user.id),
        db=db,
    )
    logger.performance_metric("jwt_generation_time", jwt_ms, unit="ms")
    user_id_var.set(str(user.id))

    return TokenResponse(access_token=token, user=_user_to_public_dict(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    email = _norm_email(payload.email)
    ip = _get_client_ip(request)

    logger.info(
        "Login attempt for email: %s" % email,
        context={"email": email, "ip_address": ip, "event_type": "login_start"},
    )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        _log_auth_attempt(
            email=email,
            action="login",
            success=False,
            ip_address=ip,
            failure_reason="user_not_found",
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not ALLOW_INACTIVE_LOGIN and not getattr(user, "is_active", True):
        _log_auth_attempt(
            email=email,
            action="login",
            success=False,
            ip_address=ip,
            failure_reason="inactive_user",
            user_id=str(user.id),
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    if not ALLOW_UNVERIFIED_LOGIN and not getattr(user, "is_verified", False):
        _log_auth_attempt(
            email=email,
            action="login",
            success=False,
            ip_address=ip,
            failure_reason="unverified_user",
            user_id=str(user.id),
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email to login",
        )

    # Verify password (guard bcrypt/passlib mismatch)
    t_verify = time.perf_counter()
    try:
        ok = verify_password(payload.password, user.hashed_password)
    except AttributeError as e:
        # Typical when passlib<->bcrypt are incompatible; surface a clear error
        logger.error(
            "bcrypt/passlib compatibility error during verify_password",
            context={"email": email, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password verification module error. Please pin packages: "
            "pip install -U 'passlib>=1.7.4' 'bcrypt>=4.0.1' (or bcrypt==3.2.2).",
        )
    verify_ms = (time.perf_counter() - t_verify) * 1000.0
    logger.performance_metric("password_verification_time", verify_ms, unit="ms")

    if not ok:
        _log_auth_attempt(
            email=email,
            action="login",
            success=False,
            ip_address=ip,
            failure_reason="invalid_password",
            user_id=str(user.id),
            db=db,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Issue token (standard pattern)
    t0 = time.perf_counter()
    token = None
    try:
        token = create_access_token(data={"sub": email})
    except TypeError:
        try:
            token = create_access_token({"sub": email})
        except TypeError:
            token = create_access_token(email)
    jwt_ms = (time.perf_counter() - t0) * 1000.0

    _log_auth_attempt(
        email=email,
        action="login",
        success=True,
        ip_address=ip,
        user_id=str(user.id),
        db=db,
    )
    logger.performance_metric("jwt_generation_time", jwt_ms, unit="ms")

    try:
        svc = _get_safe_logger(db)
        svc.track_business_event(
            event_name="user_logged_in",
            properties={"user_id": str(user.id), "email": user.email},
        )
    except Exception:
        pass

    user_id_var.set(str(user.id))
    return TokenResponse(access_token=token, user=_user_to_public_dict(user))


@router.get("/me", response_model=UserOut)
def me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        "User profile request",
        context={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "event_type": "profile_access",
        },
    )
    try:
        svc = _get_safe_logger(db)
        svc.track_user_action(
            action="profile_access",
            target="auth",
            properties={"user_id": str(current_user.id), "email": current_user.email},
        )
    except Exception:
        pass
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        "Password change attempt",
        context={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "event_type": "password_change_start",
        },
    )

    # Verify old password
    try:
        if not verify_password(payload.old_password, current_user.hashed_password):
            logger.warning(
                "Password change failed - invalid old password",
                context={
                    "user_id": str(current_user.id),
                    "event_type": "password_change_failed",
                    "reason": "invalid_old_password",
                },
            )
            try:
                svc = _get_safe_logger(db)
                svc.track_user_action(
                    action="change_password_failed",
                    target="auth",
                    properties={
                        "user_id": str(current_user.id),
                        "reason": "invalid_old_password",
                    },
                )
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect",
            )
    except AttributeError as e:
        logger.error(
            "bcrypt/passlib compatibility error during change_password",
            context={"user_id": str(current_user.id), "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password verification module error. Please pin packages: "
            "pip install -U 'passlib>=1.7.4' 'bcrypt>=4.0.1' (or bcrypt==3.2.2).",
        )

    # Update
    current_user.hashed_password = hash_password(payload.new_password)
    current_user.updated_at = datetime.utcnow()
    try:
        db.add(current_user)
        db.commit()
        logger.info(
            "Password changed successfully",
            context={"user_id": str(current_user.id), "event_type": "password_changed"},
        )
        try:
            svc = _get_safe_logger(db)
            svc.track_user_action(
                action="password_changed",
                target="auth",
                properties={"user_id": str(current_user.id)},
            )
        except Exception:
            pass
    except Exception as exc:
        db.rollback()
        logger.exception(
            exc,
            context={
                "user_id": str(current_user.id),
                "event_type": "password_change_error",
            },
        )
        try:
            svc = _get_safe_logger(db)
            svc.track_exception(
                exc=exc,
                handled=False,
                properties={
                    "user_id": str(current_user.id),
                    "email": current_user.email,
                },
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )

    return None


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip = _get_client_ip(request)
    logger.info(
        "User logout",
        context={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "ip_address": ip,
            "event_type": "logout",
        },
    )
    try:
        svc = _get_safe_logger(db)
        svc.track_authentication(
            action="logout", email=current_user.email, success=True, ip_address=ip
        )
        svc.track_business_event(
            event_name="user_logged_out",
            properties={"user_id": str(current_user.id), "email": current_user.email},
        )
    except Exception:
        pass
    return {"success": True, "message": "Logged out successfully"}