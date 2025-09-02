import asyncio
import re
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class BrowserAutomationService:
    """Enhanced browser automation service for form submission"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def initialize(self):
        """Initialize browser instance"""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=settings.browser.headless,
                slow_mo=settings.browser.slow_mo,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                    "--disable-features=BlockInsecurePrivateNetworkRequests",
                ],
            )

            # Create context with anti-detection measures
            self.context = await self.browser.new_context(
                viewport={
                    "width": settings.browser.viewport_width,
                    "height": settings.browser.viewport_height,
                },
                user_agent=settings.browser.user_agent,
                bypass_csp=True,
                ignore_https_errors=True,
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            )

            # Add stealth scripts
            await self.context.add_init_script(
                """
                // Override webdriver detection
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override chrome detection
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
            )

            logger.info("Browser automation service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def process_website(
        self, url: str, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single website"""
        result = {
            "url": url,
            "success": False,
            "method": None,
            "error": None,
            "details": {},
        }

        page = None

        try:
            # Create new page
            page = await self.context.new_page()

            # Set timeouts
            page.set_default_timeout(settings.browser.page_load_timeout)

            # Navigate to URL
            logger.info(f"Navigating to {url}")

            # Try different URL variations
            urls_to_try = self._generate_url_variants(url)

            response = None
            for variant_url in urls_to_try:
                try:
                    response = await page.goto(
                        variant_url, wait_until="domcontentloaded", timeout=30000
                    )

                    if response and response.status < 400:
                        logger.info(f"Successfully loaded {variant_url}")
                        break

                except Exception as e:
                    logger.debug(f"Failed to load {variant_url}: {str(e)}")
                    continue

            if not response or response.status >= 400:
                result["error"] = "Failed to load website"
                return result

            # Wait for page to stabilize
            await page.wait_for_timeout(2000)

            # Try to find and submit contact form
            form_result = await self._process_contact_form(page, user_data)

            if form_result["success"]:
                result["success"] = True
                result["method"] = "form"
                result["details"] = form_result
                logger.info(f"Successfully submitted form on {url}")
            else:
                # Try email fallback
                email_result = await self._extract_emails(page)

                if email_result["emails"]:
                    result["success"] = True
                    result["method"] = "email"
                    result["details"] = email_result
                    logger.info(
                        f"Found email addresses on {url}: {email_result['emails']}"
                    )
                else:
                    result["error"] = "No contact method found"
                    logger.warning(f"No contact method found on {url}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error processing {url}: {str(e)}")

        finally:
            if page:
                await page.close()

        return result

    async def _process_contact_form(
        self, page: Page, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find and submit contact form"""
        result = {"success": False, "form_found": False, "fields_filled": 0}

        try:
            # Find potential contact forms
            forms = await self._find_contact_forms(page)

            if not forms:
                logger.debug("No contact forms found")
                return result

            result["form_found"] = True

            # Process the most likely contact form
            for form in forms:
                filled = await self._fill_form(page, form, user_data)

                if filled > 0:
                    result["fields_filled"] = filled

                    # Submit form
                    submitted = await self._submit_form(page, form)

                    if submitted:
                        # Wait for submission to process
                        await page.wait_for_timeout(3000)

                        # Check for success indicators
                        success = await self._check_submission_success(page)

                        if success:
                            result["success"] = True
                            result["confirmation"] = success
                            break

        except Exception as e:
            logger.error(f"Error processing form: {str(e)}")
            result["error"] = str(e)

        return result

    async def _find_contact_forms(self, page: Page) -> List[Any]:
        """Find contact forms on the page"""
        contact_forms = []

        try:
            # Get all forms
            forms = await page.query_selector_all("form")

            for form in forms:
                # Check if it's likely a contact form
                form_html = await form.inner_html()
                form_text = form_html.lower()

                # Keywords indicating contact form
                contact_keywords = [
                    "contact",
                    "message",
                    "email",
                    "name",
                    "subject",
                    "inquiry",
                    "enquiry",
                    "get in touch",
                    "reach out",
                    "send",
                    "submit",
                    "phone",
                    "comment",
                ]

                if any(keyword in form_text for keyword in contact_keywords):
                    # Check for required fields
                    has_email = await form.query_selector(
                        'input[type="email"], input[name*="email"]'
                    )
                    has_text_area = await form.query_selector("textarea")

                    if has_email or has_text_area:
                        contact_forms.append(form)

            logger.info(f"Found {len(contact_forms)} potential contact forms")

        except Exception as e:
            logger.error(f"Error finding forms: {str(e)}")

        return contact_forms

    async def _fill_form(self, page: Page, form: Any, user_data: Dict[str, Any]) -> int:
        """Fill form fields with user data"""
        filled_count = 0

        try:
            # Field mappings
            field_mappings = {
                # Name fields
                'input[name*="name"]:not([name*="company"])': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
                'input[name*="first"]': user_data.get("first_name", ""),
                'input[name*="last"]': user_data.get("last_name", ""),
                'input[placeholder*="name" i]': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
                # Email fields
                'input[type="email"]': user_data.get("email", ""),
                'input[name*="email"]': user_data.get("email", ""),
                'input[placeholder*="email" i]': user_data.get("email", ""),
                # Phone fields
                'input[type="tel"]': user_data.get("phone_number", ""),
                'input[name*="phone"]': user_data.get("phone_number", ""),
                'input[name*="tel"]': user_data.get("phone_number", ""),
                # Company fields
                'input[name*="company"]': user_data.get("company_name", ""),
                'input[name*="organization"]': user_data.get("company_name", ""),
                # Subject fields
                'input[name*="subject"]': user_data.get("subject", "Business Inquiry"),
                # Message fields
                "textarea": user_data.get("message", ""),
                'textarea[name*="message"]': user_data.get("message", ""),
                'textarea[name*="comment"]': user_data.get("message", ""),
            }

            # Fill fields
            for selector, value in field_mappings.items():
                if not value:
                    continue

                try:
                    elements = await form.query_selector_all(selector)

                    for element in elements:
                        if await element.is_visible() and await element.is_enabled():
                            await element.fill(str(value))
                            filled_count += 1
                            await page.wait_for_timeout(
                                100
                            )  # Small delay between fields
                            break  # Only fill first matching element

                except Exception as e:
                    logger.debug(f"Could not fill {selector}: {str(e)}")

            logger.info(f"Filled {filled_count} form fields")

        except Exception as e:
            logger.error(f"Error filling form: {str(e)}")

        return filled_count

    async def _submit_form(self, page: Page, form: Any) -> bool:
        """Submit the form"""
        try:
            # Find submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Send")',
                'button:has-text("Submit")',
                'button:has-text("Contact")',
                'button:has-text("Get in touch")',
                '*:has-text("Send Message")',
            ]

            for selector in submit_selectors:
                try:
                    button = await form.query_selector(selector)

                    if (
                        button
                        and await button.is_visible()
                        and await button.is_enabled()
                    ):
                        await button.click()
                        logger.info("Form submitted")
                        return True

                except Exception:
                    continue

            # Try form submit as fallback
            await form.evaluate("form => form.submit()")
            logger.info("Form submitted via JavaScript")
            return True

        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False

    async def _check_submission_success(self, page: Page) -> Optional[str]:
        """Check if form submission was successful"""
        try:
            # Wait for any navigation or AJAX to complete
            await page.wait_for_load_state("networkidle", timeout=5000)

            # Check for success indicators
            success_keywords = [
                "thank you",
                "thanks",
                "successfully",
                "received",
                "submitted",
                "sent",
                "confirmation",
                "appreciate",
                "will get back",
                "will contact",
                "will be in touch",
            ]

            page_content = await page.content()
            page_text = page_content.lower()

            for keyword in success_keywords:
                if keyword in page_text:
                    # Try to extract the success message
                    success_elements = await page.query_selector_all(
                        'div:has-text("' + keyword + '"), p:has-text("' + keyword + '")'
                    )

                    if success_elements:
                        for element in success_elements[:1]:  # Get first match
                            text = await element.text_content()
                            if text and len(text) < 200:  # Reasonable message length
                                return text.strip()

                    return f"Success indicator found: {keyword}"

        except Exception as e:
            logger.debug(f"Error checking success: {str(e)}")

        return None

    async def _extract_emails(self, page: Page) -> Dict[str, Any]:
        """Extract email addresses from the page"""
        result = {"emails": [], "primary_email": None}

        try:
            # Get page content
            content = await page.content()

            # Find mailto links first (most reliable)
            mailto_links = await page.query_selector_all('a[href^="mailto:"]')

            for link in mailto_links:
                href = await link.get_attribute("href")
                if href:
                    email = href.replace("mailto:", "").split("?")[0].strip()
                    if self._is_valid_email(email) and email not in result["emails"]:
                        result["emails"].append(email)

            # Find emails in text using regex
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            found_emails = re.findall(email_pattern, content)

            for email in found_emails:
                if self._is_valid_email(email) and email not in result["emails"]:
                    # Filter out common non-contact emails
                    exclude = [
                        "noreply",
                        "no-reply",
                        "donotreply",
                        "admin@",
                        "webmaster@",
                        "info@info",
                    ]
                    if not any(x in email.lower() for x in exclude):
                        result["emails"].append(email)

            # Set primary email (prefer info@, contact@, or first found)
            if result["emails"]:
                for prefix in ["contact@", "info@", "hello@", "support@"]:
                    for email in result["emails"]:
                        if email.lower().startswith(prefix):
                            result["primary_email"] = email
                            break
                    if result["primary_email"]:
                        break

                if not result["primary_email"]:
                    result["primary_email"] = result["emails"][0]

        except Exception as e:
            logger.error(f"Error extracting emails: {str(e)}")

        return result

    def _generate_url_variants(self, url: str) -> List[str]:
        """Generate URL variants to try"""
        from urllib.parse import urlparse

        variants = []

        # Clean and parse URL
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split("/")[0]
        base_domain = domain.replace("www.", "")

        # Generate variants
        paths = ["", "/contact", "/contact-us", "/get-in-touch", "/about", "/contactus"]

        for protocol in ["https://", "http://"]:
            for subdomain in ["", "www."]:
                for path in paths:
                    variant = f"{protocol}{subdomain}{base_domain}{path}"
                    if variant not in variants:
                        variants.append(variant)

        return variants[:10]  # Limit to 10 variants

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            logger.info("Browser automation service cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
