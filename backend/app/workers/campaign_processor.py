"""
Main campaign processor - coordinates the entire automation workflow
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Use relative imports for modules in the same package
from .browser_automation import BrowserAutomation
from .database_handler import DatabaseHandler


class CampaignProcessor:
    """Processes campaigns by automating form submissions on websites"""

    def __init__(self, campaign_id: str, headless: bool = True):
        self.campaign_id = campaign_id
        self.db = DatabaseHandler()
        self.browser = BrowserAutomation(headless=headless)
        self.results = []

    async def run(self):
        """Main processing method"""
        print(f"\n{'='*60}")
        print(f"Starting campaign: {self.campaign_id}")
        print(f"{'='*60}\n")

        try:
            # Load campaign data
            campaign = self.db.get_campaign(self.campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {self.campaign_id} not found")

            print(f"Campaign: {campaign.name}")
            print(f"Status: {campaign.status}")

            # Load user profile for form data
            user_data = self.db.get_user_profile(campaign.user_id)
            print(f"User profile loaded for: {user_data['email']}")

            # Get pending submissions
            submissions = self.db.get_pending_submissions(self.campaign_id, limit=10)
            if not submissions:
                print("No pending submissions found")
                self.db.update_campaign_stats(self.campaign_id, 0, 0, "completed")
                return

            print(f"Found {len(submissions)} submissions to process\n")

            # Start browser
            await self.browser.start()
            print("Browser started successfully")

            if not self.browser.headless:
                print("Browser window should be visible - watch the automation!")

            # Process each submission
            for i, submission in enumerate(submissions, 1):
                print(f"\n{'-'*40}")
                print(f"Processing {i}/{len(submissions)}: {submission.url}")

                result = await self._process_submission(submission, user_data)
                self.results.append(result)

                # Update database
                self.db.update_submission(submission, result)

                status_icon = "✓" if result["success"] else "✗"
                print(f"{status_icon} Status: {result['status']}")

                # Small delay between submissions
                if i < len(submissions):
                    await asyncio.sleep(2)

            # Update campaign statistics
            self._finalize_campaign()

        except Exception as e:
            print(f"Campaign processing error: {str(e)}")
            self.db.update_campaign_stats(self.campaign_id, 0, 0, "failed")
            raise
        finally:
            await self.browser.stop()
            self.db.close()
            print("\nCleanup completed")

    async def _process_submission(self, submission, user_data: Dict) -> Dict:
        """Process a single submission"""
        result = {
            "submission_id": str(submission.id),
            "url": submission.url,
            "status": "pending",
            "success": False,
            "method": None,
            "error": None,
            "details": [],
        }

        page = None

        try:
            # Create browser page
            page = await self.browser.create_page()

            # Try to navigate to the URL
            if not await self.browser.navigate(page, submission.url):
                result["status"] = "navigation_failed"
                result["details"].append("Could not load website")
                return result

            # Try to find and fill a form
            form_result = await self.browser.process_form(page, user_data)

            if form_result["success"]:
                result["status"] = "form_submitted"
                result["success"] = True
                result["method"] = "form"
                result["details"] = form_result["details"]
            else:
                # If no form, try to extract emails
                emails = await self.browser.extract_emails(page)
                if emails:
                    result["status"] = "email_found"
                    result["success"] = True
                    result["method"] = "email"
                    result["email_extracted"] = emails[0]
                    result["details"].append(f"Found email: {emails[0]}")
                else:
                    result["status"] = "no_contact_method"
                    result["details"].append("No form or email found")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)[:500]
            result["details"].append(f"Error: {str(e)[:100]}")

        finally:
            if page:
                await page.close()

        return result

    def _finalize_campaign(self):
        """Update final campaign statistics"""
        successful = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - successful

        self.db.update_campaign_stats(self.campaign_id, successful, failed, "completed")

        print(f"\n{'='*60}")
        print(f"Campaign Results:")
        print(f"  Total processed: {len(self.results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {(successful/len(self.results)*100):.1f}%")
        print(f"{'='*60}")
