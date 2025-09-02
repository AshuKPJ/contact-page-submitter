"""
Workers module entry point
"""

import asyncio
import sys
import traceback
from datetime import datetime

from .campaign_processor import CampaignProcessor

# Windows compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def process_campaign(campaign_id: str, headless: bool = None):
    """
    Process a campaign with browser automation

    Args:
        campaign_id: The campaign ID to process
        headless: Whether to run browser in headless mode (None = use config default)
    """
    if headless is None:
        from app.core.config import settings

        headless = settings.browser.headless

    # Simple logging without the middleware
    print(f"[WORKER] Starting campaign processing: {campaign_id}")

    processor = CampaignProcessor(campaign_id, headless)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(processor.run())
        print(f"[WORKER] Campaign {campaign_id} completed successfully")

    except Exception as e:
        print(f"[WORKER ERROR] Campaign {campaign_id} failed: {str(e)}")

        # Update campaign status to failed
        from app.core.database import SessionLocal
        from app.models.campaign import Campaign

        db = SessionLocal()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = "failed"
                campaign.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

        raise

    finally:
        loop.close()


async def async_process_campaign(campaign_id: str, headless: bool = None):
    """Async version for when already in async context"""
    if headless is None:
        from app.core.config import settings

        headless = settings.browser.headless

    processor = CampaignProcessor(campaign_id, headless)
    await processor.run()


__all__ = ["process_campaign", "async_process_campaign"]
