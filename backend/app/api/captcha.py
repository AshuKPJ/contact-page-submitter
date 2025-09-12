# app/api/captcha.py
"""CAPTCHA API endpoints for Death By Captcha integration."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.captcha_service import DeathByCaptchaAPI

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/captcha", tags=["captcha"])


class DBCCredentials(BaseModel):
    """Death By Captcha credentials request model."""

    username: str
    password: str


class DBCBalanceResponse(BaseModel):
    """Death By Captcha balance response model."""

    success: bool
    balance: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None


@router.post("/check-balance", response_model=DBCBalanceResponse)
async def check_dbc_balance(
    credentials: DBCCredentials,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check Death By Captcha account balance.

    This endpoint allows users to test their DBC credentials and check their balance
    before saving them to their profile.
    """
    try:
        # Create DBC client with provided credentials
        dbc_client = DeathByCaptchaAPI(
            username=credentials.username, password=credentials.password
        )

        # Check if credentials are valid
        if not dbc_client.enabled:
            return DBCBalanceResponse(
                success=False,
                error="Invalid credentials format",
                message="Please provide both username and password",
            )

        # Get balance
        balance = await dbc_client.get_balance()

        # If balance is 0, it might mean invalid credentials
        if balance == 0.0:
            # Try to verify if it's actually 0 or invalid credentials
            # This is handled in the DeathByCaptchaAPI class
            return DBCBalanceResponse(
                success=True,
                balance=balance,
                message="Balance is $0.00 or credentials may be invalid",
            )

        return DBCBalanceResponse(
            success=True,
            balance=balance,
            message=f"Successfully connected. Balance: ${balance:.2f}",
        )

    except Exception as e:
        logger.error(f"Error checking DBC balance for user {current_user.id}: {e}")
        return DBCBalanceResponse(
            success=False, error=str(e), message="Failed to connect to Death By Captcha"
        )


@router.get("/status", response_model=dict)
async def get_captcha_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get CAPTCHA solving status for the current user.

    Returns whether the user has configured DBC credentials and their current balance.
    """
    try:
        # Get user profile
        profile = (
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        )

        if not profile or not profile.dbc_username or not profile.dbc_password:
            return {
                "enabled": False,
                "configured": False,
                "balance": None,
                "message": "Death By Captcha not configured",
            }

        # Create DBC client with user's credentials
        dbc_client = DeathByCaptchaAPI(
            username=profile.dbc_username, password=profile.dbc_password
        )

        # Get current balance
        balance = await dbc_client.get_balance()

        return {
            "enabled": True,
            "configured": True,
            "balance": balance,
            "username": profile.dbc_username,
            "message": f"Death By Captcha configured. Balance: ${balance:.2f}",
        }

    except Exception as e:
        logger.error(f"Error getting CAPTCHA status for user {current_user.id}: {e}")
        return {
            "enabled": False,
            "configured": False,
            "balance": None,
            "error": str(e),
            "message": "Error checking CAPTCHA service status",
        }


@router.post("/test-solve", response_model=dict)
async def test_captcha_solving(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Test CAPTCHA solving with a sample image.

    This endpoint tests the user's DBC credentials by solving a test CAPTCHA.
    """
    try:
        # Get user profile
        profile = (
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        )

        if not profile or not profile.dbc_username or not profile.dbc_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Death By Captcha credentials not configured",
            )

        # Create DBC client
        dbc_client = DeathByCaptchaAPI(
            username=profile.dbc_username, password=profile.dbc_password
        )

        # Check balance first
        balance = await dbc_client.get_balance()
        if balance < 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient DBC balance: ${balance:.2f}",
            )

        # For testing, we would use a sample CAPTCHA image
        # In production, you might want to generate a test CAPTCHA
        import base64

        # This is a placeholder - in production, use an actual test CAPTCHA image
        test_captcha_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_captcha_bytes = base64.b64decode(test_captcha_base64)

        # Solve the test CAPTCHA
        solution = await dbc_client.solve_image_captcha(test_captcha_bytes)

        if solution:
            return {
                "success": True,
                "message": "CAPTCHA solving test successful",
                "solution": solution,
                "balance_before": balance,
                "estimated_cost": 0.0029,  # DBC typically charges $2.89 per 1000 CAPTCHAs
            }
        else:
            return {
                "success": False,
                "message": "Failed to solve test CAPTCHA",
                "balance": balance,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing CAPTCHA solving for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test CAPTCHA solving",
        )
