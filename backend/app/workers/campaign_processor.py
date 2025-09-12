# app/workers/campaign_processor.py
"""Campaign processing worker with user-specific CAPTCHA support."""

import asyncio
import logging
import uuid
import os
from datetime import datetime
from typing import Dict, Optional

from app.core.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.submission import Submission, SubmissionStatus
from app.services.log_service import LogService
from app.workers.browser_automation import BrowserAutomation
from app.workers.database_handler import (
    mark_submission_processing,
    mark_submission_result,
    pending_for_campaign,
    update_campaign_status,
)

logger = logging.getLogger(__name__)


class CampaignProcessor:
    """Process campaign submissions with user-specific configurations."""

    def __init__(self, campaign_id: str, user_id: Optional[str] = None):
        """
        Initialize campaign processor with FORCED visible browser.
        """
        self.campaign_id = str(uuid.UUID(campaign_id))
        self.user_id = user_id
        self.db = SessionLocal()
        self.browser_automation = None
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None,
        }

        # Log subprocess environment for debugging
        self._log(
            "INFO",
            f"Subprocess environment: HEADFUL={os.getenv('DEV_AUTOMATION_HEADFUL')}, HEADLESS={os.getenv('BROWSER_HEADLESS')}",
        )

    def _log(self, level: str, msg: str):
        """Log message using LogService."""
        LogService.append(
            level,  # First arg is level
            msg,  # Second arg is message
            campaign_id=self.campaign_id,  # Use keyword argument
            user_id=self.user_id,  # Include user_id if available
        )

        # Also log to Python logger
        getattr(logger, level.lower(), logger.info)(
            f"[Campaign {self.campaign_id[:8]}] [User {self.user_id[:8] if self.user_id else 'N/A'}] {msg}"
        )

    async def run(self):
        """Run campaign processing with VISIBLE browser."""
        self.stats["start_time"] = datetime.utcnow()

        try:
            self._log("INFO", "Starting campaign processing with VISIBLE browser")

            # Get campaign
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == uuid.UUID(self.campaign_id))
                .first()
            )

            if not campaign:
                raise ValueError(f"Campaign {self.campaign_id} not found")

            # Get or verify user_id
            if not self.user_id:
                self.user_id = str(campaign.user_id)
                self._log(
                    "INFO", f"Retrieved user_id from campaign: {self.user_id[:8]}"
                )
            elif str(campaign.user_id) != self.user_id:
                self._log(
                    "WARNING",
                    f"Campaign user_id mismatch: expected {campaign.user_id}, got {self.user_id}",
                )
                self.user_id = str(campaign.user_id)

            # FORCE VISIBLE BROWSER - Override any configuration
            self._log("INFO", "FORCING browser to VISIBLE mode")
            self.browser_automation = BrowserAutomation(
                headless=False,  # FORCE visible
                slow_mo=1000,  # FORCE slow motion for visibility
                user_id=self.user_id,
                campaign_id=self.campaign_id,
            )

            # Double-check the settings were applied
            if hasattr(self.browser_automation, "headless"):
                self._log(
                    "INFO",
                    f"Browser automation headless setting: {self.browser_automation.headless}",
                )
                if self.browser_automation.headless:
                    self._log(
                        "WARNING",
                        "Browser is still headless despite forcing visible mode!",
                    )
                    # Force it again
                    self.browser_automation.headless = False
                    self._log("INFO", "Forced headless=False again")

            # Update status
            update_campaign_status(
                self.db,
                uuid.UUID(self.campaign_id),
                CampaignStatus.ACTIVE,
                started_at=datetime.utcnow(),
            )

            # Get user data including DBC credentials
            from app.services.submission_service import SubmissionService

            service = SubmissionService(self.db)
            user_data = service.get_user_profile_data(campaign.user_id)

            # Log CAPTCHA status
            has_dbc = bool(
                user_data.get("dbc_username") and user_data.get("dbc_password")
            )
            self._log(
                "INFO",
                f"CAPTCHA solving {'enabled' if has_dbc else 'disabled'} for this campaign",
            )

            # Get pending submissions
            submissions = pending_for_campaign(self.db, uuid.UUID(self.campaign_id))
            self.stats["total"] = len(submissions)

            if not submissions:
                self._log("INFO", "No pending submissions found")
                update_campaign_status(
                    self.db,
                    uuid.UUID(self.campaign_id),
                    CampaignStatus.COMPLETED,
                    completed_at=datetime.utcnow(),
                )
                return

            self._log("INFO", f"Found {len(submissions)} pending submissions")

            # Initialize browser - should be VISIBLE now
            self._log("INFO", "Starting VISIBLE browser...")
            await self.browser_automation.start()
            self._log(
                "INFO", f"Browser started - should be VISIBLE with DBC: {has_dbc}"
            )

            # Process submissions
            for i, submission in enumerate(submissions, 1):
                await self._process_submission(
                    submission, user_data, i, self.stats["total"]
                )
                await asyncio.sleep(2)

            # Complete campaign
            self.stats["end_time"] = datetime.utcnow()
            update_campaign_status(
                self.db,
                uuid.UUID(self.campaign_id),
                CampaignStatus.COMPLETED,
                completed_at=self.stats["end_time"],
                total_urls=self.stats["total"],
                submitted_count=self.stats["successful"],
                failed_count=self.stats["failed"],
            )

            self._log("INFO", "Campaign completed successfully")
            self._log_summary()

        except Exception as e:
            self.stats["end_time"] = datetime.utcnow()
            self._log("ERROR", f"Campaign processing failed: {e}")
            update_campaign_status(
                self.db,
                uuid.UUID(self.campaign_id),
                CampaignStatus.FAILED,
                completed_at=self.stats["end_time"],
            )
            raise

        finally:
            try:
                if self.browser_automation:
                    await self.browser_automation.stop()
            except:
                pass
            self.db.close()

    async def _process_submission(
        self, submission: Submission, user_data: Dict, index: int, total: int
    ):
        """Process a single submission."""
        try:
            self._log("INFO", f"Processing {index}/{total}: {submission.url}")
            mark_submission_processing(self.db, submission.id)

            # Process website with user-specific data and CAPTCHA credentials
            result = await self.browser_automation.process(submission.url, user_data)

            # Update submission
            success = result.get("success", False)
            method = result.get("method", "none")
            error_msg = result.get("error")
            details = result.get("details", {})

            # Log CAPTCHA usage if it was solved
            if details.get("captcha_solved"):
                self._log(
                    "INFO",
                    f"CAPTCHA solved for {submission.url} (type: {details.get('captcha_type')})",
                )

            mark_submission_result(
                self.db,
                submission.id,
                success=success,
                method=method,
                error_message=error_msg,
                email_extracted=details.get("primary_email"),
            )

            # Update stats
            self.stats["processed"] += 1
            if success:
                self.stats["successful"] += 1
                self._log("INFO", f"Success via {method}: {submission.url}")
            else:
                self.stats["failed"] += 1
                self._log("ERROR", f"Failed: {submission.url} - {error_msg}")

        except Exception as e:
            self.stats["failed"] += 1
            self._log("ERROR", f"Processing error for {submission.url}: {e}")
            mark_submission_result(
                self.db, submission.id, success=False, error_message=str(e)[:500]
            )

    def _log_summary(self):
        """Log campaign summary."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        success_rate = (
            (self.stats["successful"] / self.stats["total"] * 100)
            if self.stats["total"] > 0
            else 0
        )

        summary = f"""
Campaign Summary:
- User: {self.user_id[:8] if self.user_id else 'N/A'}
- Total: {self.stats['total']}
- Successful: {self.stats['successful']}
- Failed: {self.stats['failed']}
- Success Rate: {success_rate:.1f}%
- Duration: {duration:.2f} seconds
- Processing Speed: {self.stats['total'] / (duration / 3600):.1f} URLs/hour
"""
        self._log("INFO", summary)
