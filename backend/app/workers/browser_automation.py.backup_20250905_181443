"""
Browser automation handler using Playwright
Consolidates all browser-related operations from the old modules
"""

from playwright.async_api import async_playwright, Page
import re
from typing import Dict, List, Optional
from app.core.config import settings


class BrowserAutomation:
    """Handles browser automation for form filling and submission"""

    def __init__(self, headless: bool = None, slow_mo: int = None):
        """Initialize browser automation with config settings"""
        self.headless = headless if headless is not None else settings.browser.headless
        self.slow_mo = slow_mo if slow_mo is not None else settings.browser.slow_mo
        self.playwright = None
        self.browser = None
        self.context = None

    async def start(self):
        """Start browser instance"""
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-extensions",
                "--no-first-run",
                "--disable-default-apps",
            ],
        )

        self.context = await self.browser.new_context(
            viewport={
                "width": settings.browser.viewport_width,
                "height": settings.browser.viewport_height,
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        )

    async def stop(self):
        """Stop browser and clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def create_page(self) -> Page:
        """Create new browser page/tab"""
        if not self.context:
            await self.start()
        return await self.context.new_page()

    async def navigate(self, page: Page, url: str) -> bool:
        """Navigate to URL with retries for different variants"""
        variants = self._get_url_variants(url)

        for variant in variants:
            try:
                response = await page.goto(
                    variant, wait_until="domcontentloaded", timeout=30000
                )
                await page.wait_for_timeout(2000)  # Let page settle

                # Check if navigation was successful
                if response and response.status < 400:
                    return True

            except Exception:
                continue

        return False

    async def process_form(self, page: Page, user_data: Dict) -> Dict:
        """Find, fill and submit a form on the page"""
        result = {"success": False, "details": []}

        try:
            # Find forms on the page
            forms = await page.query_selector_all("form")
            if not forms:
                result["details"].append("No forms found on page")
                return result

            # Find the best form (likely contact form)
            best_form = await self._find_contact_form(forms)
            if not best_form:
                best_form = forms[0]  # Fallback to first form

            # Fill the form
            fields_filled = await self._fill_form(page, best_form, user_data)
            if fields_filled == 0:
                result["details"].append("Could not fill any form fields")
                return result

            result["details"].append(f"Filled {fields_filled} fields")

            # Submit the form
            if not await self._submit_form(page, best_form):
                result["details"].append("Could not find submit button")
                return result

            # Wait for submission to process
            await page.wait_for_timeout(3000)

            # Check for success indicators
            if await self._check_success(page):
                result["success"] = True
                result["details"].append("Form submitted successfully")
            else:
                result["success"] = True  # Still consider it success
                result["details"].append("Form submitted (no confirmation found)")

        except Exception as e:
            result["details"].append(f"Form processing error: {str(e)[:100]}")

        return result

    async def extract_emails(self, page: Page) -> List[str]:
        """Extract email addresses from the page"""
        emails = []

        try:
            # Check mailto links first (most reliable)
            mailto_links = await page.query_selector_all('a[href^="mailto:"]')
            for link in mailto_links:
                href = await link.get_attribute("href")
                if href:
                    email = href.replace("mailto:", "").split("?")[0].strip()
                    if email and "@" in email:
                        emails.append(email)

            # Search page content for email patterns
            content = await page.content()
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            found = re.findall(pattern, content)

            # Filter out common non-contact emails
            exclude = ["noreply", "no-reply", "donotreply", "admin@", "webmaster@"]
            for email in found:
                email_lower = email.lower()
                if not any(x in email_lower for x in exclude):
                    emails.append(email)

        except Exception:
            pass

        # Return unique emails (max 5)
        unique_emails = list(dict.fromkeys(emails))
        return unique_emails[:5]

    async def _find_contact_form(self, forms) -> Optional:
        """Identify the most likely contact form"""
        keywords = ["contact", "message", "inquiry", "get in touch", "reach", "email"]

        for form in forms:
            try:
                html = await form.inner_html()
                html_lower = html.lower()

                # Check if form contains contact-related keywords
                if any(keyword in html_lower for keyword in keywords):
                    return form

                # Check for email field (good indicator of contact form)
                email_field = await form.query_selector('input[type="email"]')
                if email_field:
                    return form

            except Exception:
                continue

        return None

    async def _fill_form(self, page: Page, form, user_data: Dict) -> int:
        """Fill form fields with user data"""
        filled_count = 0

        # Field mappings (selector -> data key)
        field_mappings = [
            ('input[type="email"]', user_data.get("email")),
            ('input[name*="email" i]', user_data.get("email")),
            (
                'input[name*="name"]:not([name*="first"]):not([name*="last"])',
                f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            ),
            ('input[name*="first" i]', user_data.get("first_name")),
            ('input[name*="last" i]', user_data.get("last_name")),
            ('input[type="tel"]', user_data.get("phone_number")),
            ('input[name*="phone" i]', user_data.get("phone_number")),
            ('input[name*="company" i]', user_data.get("company_name")),
            ('input[name*="organization" i]', user_data.get("company_name")),
            ("textarea", user_data.get("message")),
            ('input[name*="message" i]', user_data.get("message")),
            ('input[name*="subject" i]', "Business Inquiry"),
        ]

        for selector, value in field_mappings:
            if not value:
                continue

            try:
                elements = await form.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible() and not await element.is_disabled():
                        await element.fill("")  # Clear first
                        await element.fill(str(value))
                        filled_count += 1
                        break  # Only fill first matching element
            except Exception:
                continue

        return filled_count

    async def _submit_form(self, page: Page, form) -> bool:
        """Submit the form"""
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Send")',
            'button:has-text("Submit")',
            'button:has-text("Contact")',
            'button:has-text("Get in touch")',
            'button:has-text("Send message")',
        ]

        # Try to find submit button within form first
        for selector in submit_selectors:
            try:
                buttons = await form.query_selector_all(selector)
                for button in buttons:
                    if await button.is_visible() and not await button.is_disabled():
                        await button.click()
                        return True
            except Exception:
                continue

        # If no button in form, try page-wide search
        for selector in submit_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    return True
            except Exception:
                continue

        return False

    async def _check_success(self, page: Page) -> bool:
        """Check if form submission was successful"""
        try:
            # Wait a bit for any redirects or updates
            await page.wait_for_timeout(1000)

            content = await page.content()
            content_lower = content.lower()

            success_keywords = [
                "thank you",
                "thanks for",
                "successfully",
                "success",
                "submitted",
                "received your",
                "we'll get back",
                "confirmation",
                "message sent",
                "form submitted",
            ]

            return any(keyword in content_lower for keyword in success_keywords)

        except Exception:
            return False

    def _get_url_variants(self, url: str) -> List[str]:
        """Generate URL variants to try"""
        # Clean URL
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Extract domain
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split("/")[0]

        # Remove www if present for base domain
        base_domain = domain.replace("www.", "")

        # Generate variants
        variants = []

        # Original URL first
        if url not in variants:
            variants.append(url)

        # Common patterns
        protocols = ["https://", "http://"]
        subdomains = ["", "www."]
        paths = ["", "/contact", "/contact-us", "/get-in-touch"]

        for protocol in protocols:
            for subdomain in subdomains:
                for path in paths:
                    variant = f"{protocol}{subdomain}{base_domain}{path}"
                    if variant not in variants:
                        variants.append(variant)

        # Return first 6 unique variants
        return variants[:6]
