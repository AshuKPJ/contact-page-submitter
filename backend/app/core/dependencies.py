# app/core/dependencies.py
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user (required)."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[getattr(settings, "ALGORITHM", "HS256")],
        )
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return user if token is present/valid; else None."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[getattr(settings, "ALGORITHM", "HS256")],
        )
        email: str = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()
    except JWTError:
        return None


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Legacy admin checker: True admin if boolean is_superuser is set."""
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Accepts both role-based and boolean admin flags.
    Allowed roles: admin, owner (case-insensitive); OR is_superuser True.
    """
    role = (getattr(current_user, "role", "") or "").lower()
    if role in {"admin", "owner"} or getattr(current_user, "is_superuser", False):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    )


# ============================================
# WebSocket Authentication Functions
# ============================================


async def get_current_user_ws(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    WebSocket authentication using token from query parameter.
    Returns None if no token or invalid token (doesn't raise exception).
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[getattr(settings, "ALGORITHM", "HS256")],
        )
        email: str = payload.get("sub")
        if not email:
            return None

        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError:
        return None


async def get_current_user_ws_required(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> User:
    """
    WebSocket authentication that requires a valid user.
    Raises HTTPException if no valid token/user.
    """
    user = await get_current_user_ws(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WebSocket authentication failed",
        )
    return user


# ============================================
# Additional Helper Functions
# ============================================


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload.
    Returns None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[getattr(settings, "ALGORITHM", "HS256")],
        )
        return payload
    except JWTError:
        return None


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    Get a user from a JWT token.
    Returns None if token is invalid or user not found.
    """
    payload = verify_token(token)
    if not payload:
        return None

    email = payload.get("sub")
    if not email:
        return None

    return db.query(User).filter(User.email == email).first()


# ============================================
# Role-based permission checkers
# ============================================


def require_role(required_roles: list[str]):
    """
    Decorator/dependency to require specific roles.
    Usage: @router.get("/", dependencies=[Depends(require_role(["admin", "moderator"]))])
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = (getattr(current_user, "role", "") or "").lower()
        if user_role not in [r.lower() for r in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of these roles: {', '.join(required_roles)}",
            )
        return current_user

    return role_checker


def has_permission(user: User, permission: str) -> bool:
    """
    Check if a user has a specific permission.
    This can be extended to check permissions from a database table.
    """
    # For now, simple role-based check
    role = (getattr(user, "role", "") or "").lower()

    # Admin and owner have all permissions
    if role in {"admin", "owner"}:
        return True

    # Define permission mappings
    permission_map = {
        "view_users": ["admin", "owner", "moderator"],
        "edit_users": ["admin", "owner"],
        "delete_users": ["owner"],
        "view_campaigns": ["admin", "owner", "user"],
        "edit_campaigns": ["admin", "owner", "user"],  # Users can edit their own
        "delete_campaigns": ["admin", "owner"],
        "view_logs": ["admin", "owner"],
        "manage_system": ["owner"],
    }

    allowed_roles = permission_map.get(permission, [])
    return role in allowed_roles
