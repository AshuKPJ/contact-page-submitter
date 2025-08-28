# app/workers/processor.py

import asyncio
from datetime import datetime
from playwright.sync_api import (
    sync_playwright,
)  # Use sync version for Windows compatibility
from sqlalchemy.orm import Session
import re
import threading

# Import database and models
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.core.database import SessionLocal
from app.models.submission import Submission
from app.models.website import Website
from app.models.user_profile import UserContactProfile


def process_campaign_sync(campaign_id: str):
    """Process campaign submissions synchronously (Windows compatible)"""
    db = SessionLocal()

    try:
        # Start browser in headless mode for background processing
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False,  # Set to False to see what's happening during development
                args=["--disable-blink-features=AutomationControlled"],
            )

            print(f"Processing campaign: {campaign_id}")

            # Get submissions
            submissions = (
                db.query(Submission)
                .filter(
                    Submission.campaign_id == campaign_id,
                    Submission.status == "pending",
                )
                .all()
            )

            print(f"Found {len(submissions)} submissions to process")

            for submission in submissions:
                website = (
                    db.query(Website)
                    .filter(Website.id == submission.website_id)
                    .first()
                )

                if not website:
                    continue

                # Update status
                submission.status = "processing"
                db.commit()

                page = browser.new_page()

                try:
                    print(f"Processing: {website.contact_url}")

                    # Navigate to site
                    page.goto(website.contact_url, timeout=30000)
                    page.wait_for_timeout(2000)

                    # Try to find form
                    form = page.query_selector("form")
                    if form:
                        # Try to fill email field at minimum
                        email_field = page.query_selector('input[type="email"]')
                        if email_field:
                            email_field.fill("contact@example.com")

                        # Try name field
                        name_field = page.query_selector('input[name*="name"]')
                        if name_field:
                            name_field.fill("Test User")

                        # Try message field
                        message_field = page.query_selector("textarea")
                        if message_field:
                            message_field.fill("I am interested in your services.")

                        # Try to submit
                        submit = page.query_selector('button[type="submit"]')
                        if submit:
                            submit.click()
                            page.wait_for_timeout(2000)

                        submission.status = "submitted"
                        submission.success = True
                        print(f"✓ Form submitted for {website.domain}")
                    else:
                        # Try to find email
                        mailto = page.query_selector('a[href^="mailto:"]')
                        if mailto:
                            href = mailto.get_attribute("href")
                            email = href.replace("mailto:", "").split("?")[0]
                            submission.email_extracted = email
                            submission.status = "email_found"
                            print(f"✓ Email found for {website.domain}: {email}")
                        else:
                            submission.status = "no_contact"
                            print(f"✗ No contact method found for {website.domain}")

                except Exception as e:
                    submission.status = "failed"
                    submission.error_message = str(e)[:500]
                    print(f"✗ Error processing {website.domain}: {str(e)}")

                finally:
                    page.close()
                    submission.processed_at = datetime.utcnow()
                    db.commit()

                # Small delay between sites
                import time

                time.sleep(2)

            browser.close()
            print(f"Campaign {campaign_id} processing completed")

    except Exception as e:
        print(f"Campaign processing error: {e}")
    finally:
        db.close()


def process_campaign(campaign_id: str):
    """
    Wrapper function that runs the sync processor in a thread
    This avoids Windows asyncio subprocess issues
    """
    # Run in a separate thread to avoid blocking
    thread = threading.Thread(target=process_campaign_sync, args=(campaign_id,))
    thread.daemon = True  # Allow main program to exit even if thread is running
    thread.start()
    print(f"Started processing thread for campaign: {campaign_id}")


# For backwards compatibility with async calls
async def process_campaign_async(campaign_id: str):
    """Async wrapper that calls the sync version in a thread"""
    process_campaign(campaign_id)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # For testing, run synchronously
        process_campaign_sync(sys.argv[1])
