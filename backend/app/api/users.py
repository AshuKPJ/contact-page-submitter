# app/api/users.py - Updated ProfileUpdateRequest with DBC fields
from __future__ import annotations

import time
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.log_service import ApplicationInsightsLogger

router = APIRouter(prefix="/api/users", tags=["users"], redirect_slashes=False)


class ProfileUpdateRequest(BaseModel):
    # Basic Information
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)

    # Company Information
    company_name: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)
    website_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)

    # Location Information
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=100)

    # Contact Preferences
    preferred_language: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=50)
    preferred_contact: Optional[str] = Field(None, max_length=100)
    best_time_to_contact: Optional[str] = Field(None, max_length=100)

    # Message Defaults
    subject: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = Field(None)

    # Business Information
    product_interest: Optional[str] = Field(None, max_length=255)
    budget_range: Optional[str] = Field(None, max_length=100)
    referral_source: Optional[str] = Field(None, max_length=255)
    contact_source: Optional[str] = Field(None, max_length=255)
    is_existing_customer: Optional[bool] = Field(None)

    # Additional Fields
    notes: Optional[str] = Field(None)
    form_custom_field_1: Optional[str] = Field(None, max_length=500)
    form_custom_field_2: Optional[str] = Field(None, max_length=500)
    form_custom_field_3: Optional[str] = Field(None, max_length=500)

    # Death By Captcha Credentials
    dbc_username: Optional[str] = Field(None, max_length=255)
    dbc_password: Optional[str] = Field(None, max_length=255)


class UserProfileResponse(BaseModel):
    user: Dict[str, Any]
    profile: Dict[str, Any]


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request and request.client:
        return request.client.host
    return "unknown"


def _get_role_string(user: User) -> str:
    """Helper function to extract role as string"""
    role = getattr(user, "role", "user")
    if hasattr(role, "value"):
        return str(role.value)
    return str(role)


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user profile combining base user data and extended profile information"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Track profile view
    logger.track_user_action(
        action="view_profile",
        target="user_profile",
        properties={"user_id": str(current_user.id), "ip": get_client_ip(request)},
    )

    try:
        # Build base user data
        base = {
            "id": str(current_user.id),
            "email": current_user.email,
            "first_name": getattr(current_user, "first_name", None),
            "last_name": getattr(current_user, "last_name", None),
            "role": _get_role_string(current_user),
            "is_active": getattr(current_user, "is_active", True),
            "is_verified": getattr(current_user, "is_verified", True),
            "profile_image_url": getattr(current_user, "profile_image_url", None),
            "created_at": (
                current_user.created_at.isoformat()
                if hasattr(current_user, "created_at") and current_user.created_at
                else None
            ),
            "updated_at": (
                current_user.updated_at.isoformat()
                if hasattr(current_user, "updated_at") and current_user.updated_at
                else None
            ),
        }

        # Get extended profile information including DBC credentials
        profile_start = time.time()
        profile_query = text(
            """
            SELECT
                up.first_name, up.last_name, up.phone_number, up.company_name, 
                up.job_title, up.website_url, up.linkedin_url, up.industry, 
                up.city, up.state, up.zip_code, up.country, up.region, 
                up.timezone, up.subject, up.message, up.product_interest,
                up.budget_range, up.referral_source, up.preferred_contact, 
                up.best_time_to_contact, up.contact_source, up.is_existing_customer, 
                up.language, up.preferred_language, up.notes, 
                up.form_custom_field_1, up.form_custom_field_2, up.form_custom_field_3,
                up.dbc_username, 
                CASE 
                    WHEN up.dbc_password IS NOT NULL AND up.dbc_password != '' 
                    THEN '********' 
                    ELSE NULL 
                END as dbc_password_masked,
                CASE 
                    WHEN up.dbc_username IS NOT NULL AND up.dbc_password IS NOT NULL 
                    THEN true 
                    ELSE false 
                END as has_dbc_credentials,
                up.created_at, up.updated_at
            FROM user_profiles up
            WHERE up.user_id = :uid
            LIMIT 1
        """
        )

        profile_result = (
            db.execute(profile_query, {"uid": str(current_user.id)}).mappings().first()
        )
        profile_time = (time.time() - profile_start) * 1000

        logger.track_database_operation(
            operation="SELECT",
            table="user_profiles",
            query_time_ms=profile_time,
            success=True,
        )

        profile = dict(profile_result) if profile_result else {}

        # Convert datetime objects to ISO strings in profile
        for key, value in profile.items():
            if hasattr(value, "isoformat"):
                profile[key] = value.isoformat()

        # Add CAPTCHA status if DBC credentials exist
        if profile.get("has_dbc_credentials"):
            profile["captcha_enabled"] = True
            logger.track_metric(
                name="user_has_captcha",
                value=1.0,
                properties={"user_id": str(current_user.id)},
            )

        payload = {"user": base, "profile": profile}

        # Track metrics
        logger.track_metric(
            name="profile_completeness",
            value=(
                len([v for v in profile.values() if v]) / len(profile) * 100
                if profile
                else 0
            ),
            properties={"user_id": str(current_user.id)},
        )

        # Track business event
        logger.track_business_event(
            event_name="profile_retrieved",
            properties={
                "user_id": str(current_user.id),
                "has_extended_profile": bool(profile),
                "has_dbc_credentials": profile.get("has_dbc_credentials", False),
                "profile_fields_populated": len([v for v in profile.values() if v]),
            },
            metrics={"query_time_ms": profile_time},
        )

        return payload

    except SQLAlchemyError as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        )


@router.put("/profile")
def update_profile(
    request: Request,
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user profile information including DBC credentials"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Track what fields are being updated
    updated_fields = [
        k
        for k, v in profile_data.model_dump(exclude_unset=True).items()
        if v is not None
    ]

    # Check if DBC credentials are being updated
    updating_dbc = "dbc_username" in updated_fields or "dbc_password" in updated_fields

    logger.track_user_action(
        action="update_profile",
        target="user_profile",
        properties={
            "user_id": str(current_user.id),
            "fields_updated": updated_fields,
            "field_count": len(updated_fields),
            "updating_dbc": updating_dbc,
            "ip": get_client_ip(request),
        },
    )

    try:
        # Update base user fields if provided
        user_updated = False
        user_changes = {}

        if profile_data.first_name is not None:
            old_value = current_user.first_name
            current_user.first_name = profile_data.first_name.strip()
            user_updated = True
            user_changes["first_name"] = {
                "old": old_value,
                "new": current_user.first_name,
            }

        if profile_data.last_name is not None:
            old_value = current_user.last_name
            current_user.last_name = profile_data.last_name.strip()
            user_updated = True
            user_changes["last_name"] = {
                "old": old_value,
                "new": current_user.last_name,
            }

        if user_updated:
            update_start = time.time()
            current_user.updated_at = datetime.utcnow()
            db.add(current_user)
            update_time = (time.time() - update_start) * 1000

            logger.track_database_operation(
                operation="UPDATE",
                table="users",
                query_time_ms=update_time,
                affected_rows=1,
                success=True,
            )

        # Check if user profile exists
        profile_check_start = time.time()
        profile_exists_query = text(
            """
            SELECT COUNT(*) FROM user_profiles WHERE user_id = :uid
        """
        )
        profile_exists = (
            db.execute(profile_exists_query, {"uid": str(current_user.id)}).scalar() > 0
        )
        profile_check_time = (time.time() - profile_check_start) * 1000

        logger.track_database_operation(
            operation="SELECT",
            table="user_profiles",
            query_time_ms=profile_check_time,
            success=True,
        )

        # Prepare profile data
        profile_fields = {}
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            if value is not None and field not in ["first_name", "last_name"]:
                # Don't strip password fields
                if field == "dbc_password":
                    profile_fields[field] = value
                else:
                    profile_fields[field] = (
                        value.strip() if isinstance(value, str) else value
                    )

        if profile_fields:
            profile_update_start = time.time()

            if profile_exists:
                # Update existing profile
                update_parts = []
                params = {"uid": str(current_user.id)}

                for field, value in profile_fields.items():
                    update_parts.append(f"{field} = :{field}")
                    params[field] = value

                if update_parts:
                    params["updated_at"] = datetime.utcnow()
                    update_parts.append("updated_at = :updated_at")

                    update_query = text(
                        f"""
                        UPDATE user_profiles 
                        SET {', '.join(update_parts)}
                        WHERE user_id = :uid
                    """
                    )
                    db.execute(update_query, params)
            else:
                # Create new profile
                fields = list(profile_fields.keys()) + [
                    "user_id",
                    "created_at",
                    "updated_at",
                ]
                placeholders = [f":{field}" for field in fields]

                profile_fields.update(
                    {
                        "user_id": str(current_user.id),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                )

                insert_query = text(
                    f"""
                    INSERT INTO user_profiles ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                """
                )
                db.execute(insert_query, profile_fields)

            profile_update_time = (time.time() - profile_update_start) * 1000

            logger.track_database_operation(
                operation="UPDATE" if profile_exists else "INSERT",
                table="user_profiles",
                query_time_ms=profile_update_time,
                affected_rows=1,
                success=True,
            )

        db.commit()

        # Track business event
        logger.track_business_event(
            event_name="profile_updated",
            properties={
                "user_id": str(current_user.id),
                "fields_updated": updated_fields,
                "user_fields_changed": list(user_changes.keys()),
                "profile_fields_changed": list(profile_fields.keys()),
                "profile_created": not profile_exists and bool(profile_fields),
                "dbc_credentials_updated": updating_dbc,
            },
            metrics={
                "total_update_time_ms": (update_time if user_updated else 0)
                + (profile_update_time if profile_fields else 0),
                "fields_updated_count": len(updated_fields),
            },
        )

        # Log DBC update specifically
        if updating_dbc:
            logger.track_business_event(
                event_name="dbc_credentials_updated",
                properties={
                    "user_id": str(current_user.id),
                    "has_username": bool(profile_data.dbc_username),
                    "has_password": bool(profile_data.dbc_password),
                },
            )

        return {"success": True, "message": "Profile updated successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
