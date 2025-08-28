import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from fastapi import HTTPException
from urllib.parse import urlparse

from app.models.website import Website
from app.models.campaign import Campaign
from app.schemas.website import WebsiteCreate, WebsiteUpdate, WebsiteResponse


class WebsiteService:
    """Service for managing websites and form detection"""

    def __init__(self, db: Session):
        self.db = db

    def create_website(
        self, user_id: uuid.UUID, website_data: WebsiteCreate
    ) -> Website:
        """Create a new website entry"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(
                and_(
                    Campaign.id == website_data.campaign_id, Campaign.user_id == user_id
                )
            )
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Extract domain from contact URL if not provided
        domain = website_data.domain
        if not domain and website_data.contact_url:
            parsed = urlparse(website_data.contact_url)
            domain = parsed.netloc

        website = Website(
            campaign_id=website_data.campaign_id,
            user_id=user_id,
            domain=domain,
            contact_url=website_data.contact_url,
            status="pending",
        )

        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        return website

    def get_website(
        self, website_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Website]:
        """Get a website by ID"""
        return (
            self.db.query(Website)
            .filter(and_(Website.id == website_id, Website.user_id == user_id))
            .first()
        )

    def get_campaign_websites(
        self,
        campaign_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[Website], int]:
        """Get websites for a campaign"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        query = (
            self.db.query(Website)
            .filter(Website.campaign_id == campaign_id)
            .order_by(desc(Website.created_at))
        )

        total = query.count()
        websites = query.offset((page - 1) * per_page).limit(per_page).all()

        return websites, total

    def update_website(
        self, website_id: uuid.UUID, user_id: uuid.UUID, website_data: WebsiteUpdate
    ) -> Optional[Website]:
        """Update a website"""
        website = self.get_website(website_id, user_id)
        if not website:
            return None

        update_data = website_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(website, field, value)

        website.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(website)
        return website

    def mark_form_detected(
        self,
        website_id: uuid.UUID,
        form_type: str,
        form_labels: List[str] = None,
        field_count: int = 0,
        has_captcha: bool = False,
        captcha_type: str = None,
    ) -> Website:
        """Mark that a form was detected on a website"""
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        website.form_detected = True
        website.form_type = form_type
        website.form_labels = form_labels
        website.form_field_count = field_count
        website.has_captcha = has_captcha
        website.captcha_type = captcha_type
        website.status = "analyzed"
        website.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(website)
        return website

    def mark_website_failed(
        self, website_id: uuid.UUID, failure_reason: str
    ) -> Website:
        """Mark a website as failed with reason"""
        website = self.db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        website.status = "failed"
        website.failure_reason = failure_reason
        website.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(website)
        return website

    def get_websites_by_status(self, user_id: uuid.UUID, status: str) -> List[Website]:
        """Get websites by status"""
        return (
            self.db.query(Website)
            .filter(and_(Website.user_id == user_id, Website.status == status))
            .all()
        )

    def bulk_import_websites(
        self,
        user_id: uuid.UUID,
        campaign_id: uuid.UUID,
        website_data: List[Dict[str, Any]],
    ) -> List[Website]:
        """Bulk import websites from CSV or other source"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        websites = []
        for data in website_data:
            # Extract domain from URL if needed
            contact_url = data.get("contact_url") or data.get("url")
            domain = data.get("domain")

            if not domain and contact_url:
                parsed = urlparse(contact_url)
                domain = parsed.netloc

            website = Website(
                campaign_id=campaign_id,
                user_id=user_id,
                domain=domain,
                contact_url=contact_url,
                status="pending",
            )
            websites.append(website)

        self.db.add_all(websites)

        # Update campaign total URLs
        campaign.total_urls += len(websites)

        self.db.commit()

        for website in websites:
            self.db.refresh(website)

        return websites
