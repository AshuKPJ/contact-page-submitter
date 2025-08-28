import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.core.database import SessionLocal
from app.models.submission import Submission
from app.models.website import Website


async def run(campaign_id):
    print(f"Starting browser for campaign: {campaign_id}")

    # Get submissions from database
    db = SessionLocal()
    submissions = (
        db.query(Submission).filter(Submission.campaign_id == campaign_id).all()
    )

    print(f"Found {len(submissions)} URLs to process")

    # Start browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False  # This makes browser visible
    )

    try:
        for submission in submissions:
            website = (
                db.query(Website).filter(Website.id == submission.website_id).first()
            )

            if website:
                print(f"Opening: {website.contact_url}")

                page = await browser.new_page()
                await page.goto(website.contact_url)
                await page.wait_for_timeout(5000)  # Wait 5 seconds
                await page.close()

    finally:
        await browser.close()
        await playwright.stop()
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(run(sys.argv[1]))
    else:
        print("Usage: python campaign_processor.py <campaign_id>")
