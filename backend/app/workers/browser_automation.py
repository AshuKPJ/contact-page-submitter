# app/workers/browser_automation.py
"""Enhanced browser automation with Windows compatibility and user profile integration."""

import re
import logging
import os
import asyncio
import base64
import sys
import subprocess
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
from sqlalchemy.orm import Session

# CRITICAL: Set Windows event loop policy for Playwright subprocess support
if sys.platform == "win32":
    # Ensure we're using ProactorEventLoop for subprocess support
    try:
        from asyncio import WindowsProactorEventLoopPolicy

        asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())
    except ImportError:
        pass

from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    Playwright,
)

from app.services.log_service import LogService
from app.services.captcha_service import CaptchaService
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """Enhanced browser automation with user profile integration."""

    # Update just the __init__ method in app/workers/browser_automation.py

    def __init__(
        self,
        headless: Optional[bool] = None,
        slow_mo: Optional[int] = None,
        user_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ):
        """Initialize browser automation with centralized config"""
        # Get settings
        from app.core.config import get_settings

        settings = get_settings()

        # Use settings.browser for configuration
        # Allow overrides if explicitly provided
        self.headless = headless if headless is not None else settings.browser.headless
        self.slow_mo = slow_mo if slow_mo is not None else settings.browser.slow_mo

        # Store browser settings for later use
        self.browser_settings = settings.browser

        # User context for profile-based features
        self.user_id = user_id
        self.campaign_id = campaign_id

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # Database session for user profile access
        self.db: Optional[Session] = None

        # Initialize CAPTCHA service with user context
        self.captcha_service: Optional[CaptchaService] = None

        # Log configuration with clear visibility status
        self._log_info(
            f"Browser Configuration: "
            f"{'VISIBLE' if not self.headless else 'HEADLESS'} mode, "
            f"slow_mo={self.slow_mo}ms, "
            f"user_id={user_id[:8] if user_id else 'None'}",
            browser_config=self.browser_settings.log_settings(),
        )

    def _log_info(self, message: str, **context):
        """Log info message with campaign context."""
        LogService.info(
            message, user_id=self.user_id, campaign_id=self.campaign_id, context=context
        )
        logger.info(
            f"[Campaign {self.campaign_id[:8] if self.campaign_id else 'N/A'}] {message}"
        )

    def _log_error(self, message: str, **context):
        """Log error message with campaign context."""
        LogService.error(
            message, user_id=self.user_id, campaign_id=self.campaign_id, context=context
        )
        logger.error(
            f"[Campaign {self.campaign_id[:8] if self.campaign_id else 'N/A'}] {message}"
        )

    def _log_warning(self, message: str, **context):
        """Log warning message with campaign context."""
        LogService.warning(
            message, user_id=self.user_id, campaign_id=self.campaign_id, context=context
        )
        logger.warning(
            f"[Campaign {self.campaign_id[:8] if self.campaign_id else 'N/A'}] {message}"
        )

    async def start(self):
        """Start browser with Windows compatibility and user context."""
        try:
            self._log_info("Starting Playwright browser automation")

            # Ensure ProactorEventLoop on Windows for subprocess support
            if sys.platform == "win32":
                loop = asyncio.get_event_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    self._log_warning(
                        "Not using ProactorEventLoop, attempting to switch..."
                    )
                    # Create new ProactorEventLoop
                    new_loop = asyncio.ProactorEventLoop()
                    asyncio.set_event_loop(new_loop)
                    loop = new_loop
                    self._log_info(
                        "Switched to ProactorEventLoop for Windows subprocess support"
                    )

            # Initialize database session for user profile access
            if self.user_id:
                self.db = SessionLocal()
                self.captcha_service = CaptchaService(
                    db=self.db, user_id=self.user_id, campaign_id=self.campaign_id
                )
                self._log_info(
                    f"Initialized CAPTCHA service for user {self.user_id[:8]}"
                )

            # Start playwright with explicit timeout
            self._log_info("Launching Playwright...")
            try:
                self.playwright = await async_playwright().start()
            except Exception as e:
                # Fallback: Try with manual subprocess if automatic fails
                self._log_warning(
                    f"Standard Playwright start failed: {e}, trying alternative method"
                )

                # Alternative approach for Windows
                if sys.platform == "win32":
                    # Install browser if needed
                    try:
                        subprocess.run(
                            ["playwright", "install", "chromium"], check=True
                        )
                    except:
                        pass

                    # Retry with fresh event loop
                    self.playwright = await async_playwright().start()
                else:
                    raise

            # Windows-specific browser args for better compatibility
            browser_args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ]

            # Additional Windows-specific args
            if sys.platform == "win32":
                browser_args.extend(
                    [
                        "--disable-gpu-sandbox",
                        "--disable-software-rasterizer",
                        "--disable-features=RendererCodeIntegrity",
                    ]
                )

            self._log_info(
                f"Launching browser with args: {browser_args[:5]}..."
            )  # Log first 5 args

            # Launch browser with timeout
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=browser_args,
                timeout=30000,  # 30 second timeout
            )

            # Create context with stealth settings
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                },
            )

            # Add stealth scripts
            await self.context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            """
            )

            self._log_info("Browser started successfully")

        except Exception as e:
            self._log_error(f"Failed to start browser: {e}")
            await self.cleanup()
            raise RuntimeError(f"Browser initialization failed: {e}")

    async def stop(self):
        """Stop browser and cleanup."""
        await self.cleanup()

    async def cleanup(self):
        """Clean up browser resources and database connection."""
        try:
            if self.context:
                try:
                    await self.context.close()
                    self._log_info("Browser context closed")
                except Exception as e:
                    self._log_warning(f"Error closing context: {e}")
                finally:
                    self.context = None

            if self.browser:
                try:
                    await self.browser.close()
                    self._log_info("Browser closed")
                except Exception as e:
                    self._log_warning(f"Error closing browser: {e}")
                finally:
                    self.browser = None

            if self.playwright:
                try:
                    await self.playwright.stop()
                    self._log_info("Playwright stopped")
                except Exception as e:
                    self._log_warning(f"Error stopping playwright: {e}")
                finally:
                    self.playwright = None

            # Close database connection
            if self.db:
                try:
                    self.db.close()
                except:
                    pass
                finally:
                    self.db = None

        except Exception as e:
            self._log_warning(f"Error during cleanup: {e}")

    async def process(self, url: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process website with user profile-based CAPTCHA solving and form filling."""
        if not self.context:
            await self.start()

        page = None
        result = {
            "success": False,
            "method": "none",
            "error": None,
            "details": {
                "primary_email": None,
                "emails_found": [],
                "submitted_via": None,
                "success_hint": None,
                "pages_checked": [],
                "captcha_solved": False,
                "captcha_type": None,
                "form_fields_filled": 0,
                "user_has_dbc_credentials": (
                    bool(self.captcha_service and self.captcha_service.dbc.enabled)
                    if self.captcha_service
                    else False
                ),
            },
        }

        try:
            self._log_info(f"Starting to process website: {url}")

            # Create and configure page
            page = await self.context.new_page()
            page.set_default_timeout(30000)

            # Clean and normalize URL
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Navigate to main page
            nav_success, final_url, nav_error = await self._safe_navigate(page, url)
            if not nav_success:
                result["error"] = f"Navigation failed: {nav_error}"
                self._log_error(f"Navigation failed for {url}: {nav_error}")
                return result

            result["details"]["pages_checked"].append(final_url)
            self._log_info(f"Successfully navigated to: {final_url}")

            # Wait for page to load and dynamic content
            await asyncio.sleep(2)
            await self._wait_for_dynamic_content(page)

            # Strategy 1: Try forms on current page
            forms_found = await self._detect_forms(page)
            if forms_found:
                self._log_info(f"Found {len(forms_found)} form(s) on main page")

                form_result = await self._process_forms(
                    page, forms_found, user_data, result
                )
                if form_result["success"]:
                    return form_result

            # Strategy 2: Look for contact page
            contact_url = await self._find_contact_page(page)
            if contact_url and contact_url != final_url:
                contact_result = await self._process_contact_page(
                    page, contact_url, user_data, result
                )
                if contact_result["success"]:
                    return contact_result

            # Strategy 3: Email extraction fallback
            emails = await self._extract_emails_comprehensive(page)
            if emails:
                result["success"] = True
                result["method"] = "email"
                result["details"]["primary_email"] = emails[0]
                result["details"]["emails_found"] = emails[:5]
                self._log_info(f"Email extraction successful: {emails[0]}")
                return result

            # No success
            result["error"] = (
                f"No forms or emails found on {len(result['details']['pages_checked'])} page(s)"
            )
            self._log_warning(result["error"])

        except Exception as e:
            result["error"] = f"Processing error: {str(e)[:200]}"
            self._log_error(f"Processing error for {url}: {e}")

        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    self._log_warning(f"Error closing page: {e}")

        return result

    async def _get_user_profile_data(self) -> Dict[str, Any]:
        """Get user profile data for form filling from database."""
        if not self.db or not self.user_id:
            return {}

        try:
            from app.models.user_profile import UserProfile
            from app.models.user import User

            # Get user basic info
            user = self.db.query(User).filter(User.id == self.user_id).first()

            # Get extended profile
            profile = (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == self.user_id)
                .first()
            )

            user_data = {}

            # Basic user data
            if user:
                user_data.update(
                    {
                        "email": user.email,
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                    }
                )

            # Extended profile data including DBC credentials
            if profile:
                user_data.update(
                    {
                        "phone_number": profile.phone_number or "",
                        "company_name": profile.company_name or "",
                        "job_title": profile.job_title or "",
                        "website_url": profile.website_url or "",
                        "subject": profile.subject or "Business Inquiry",
                        "message": profile.message
                        or "I am interested in your services and would like to discuss potential business opportunities.",
                        "city": profile.city or "",
                        "state": profile.state or "",
                        "country": profile.country or "",
                        "industry": profile.industry or "",
                        # DBC credentials for CAPTCHA solving
                        "dbc_username": profile.dbc_username or "",
                        "dbc_password": profile.dbc_password or "",
                    }
                )

            # Set defaults if no profile data
            if not user_data.get("first_name"):
                user_data["first_name"] = "John"
            if not user_data.get("last_name"):
                user_data["last_name"] = "Doe"
            if not user_data.get("email"):
                user_data["email"] = "contact@example.com"
            if not user_data.get("message"):
                user_data["message"] = "I am interested in your services."

            return user_data

        except Exception as e:
            self._log_error(f"Error getting user profile data: {e}")
            return {
                "first_name": "John",
                "last_name": "Doe",
                "email": "contact@example.com",
                "message": "I am interested in your services.",
            }

    # ... (rest of the methods remain the same)
    async def _safe_navigate(self, page: Page, url: str):
        """Safely navigate to URL with multiple attempts."""
        candidates = [url]
        if not url.startswith("http"):
            candidates = [f"https://{url}", f"http://{url}"]

        last_error = None
        for candidate in candidates:
            try:
                self._log_info(f"Attempting navigation to: {candidate}")
                response = await page.goto(
                    candidate, wait_until="domcontentloaded", timeout=20000
                )

                if response and response.status >= 400:
                    last_error = f"HTTP {response.status}"
                    continue

                return True, page.url, None

            except Exception as e:
                last_error = str(e)
                continue

        return False, url, last_error

    async def _wait_for_dynamic_content(self, page: Page):
        """Wait for dynamic forms and content to load."""
        try:
            # Wait for common form elements
            await page.wait_for_selector("form, input, textarea", timeout=5000)
        except:
            # Try waiting for common contact form selectors
            selectors = [
                'input[type="email"]',
                'input[name*="email" i]',
                'textarea[name*="message" i]',
                'input[name*="name" i]',
            ]

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    break
                except:
                    continue

    async def _detect_forms(self, page: Page) -> List[Any]:
        """Detect all forms on the page."""
        forms = await page.query_selector_all("form")

        # Filter for likely contact forms
        contact_forms = []
        for form in forms:
            try:
                form_html = await form.inner_html()
                form_text = form_html.lower()

                # Check for contact indicators
                contact_indicators = [
                    "contact",
                    "message",
                    "inquiry",
                    "email",
                    "send",
                    "submit",
                    "get in touch",
                    "reach out",
                    "talk to us",
                ]

                if any(indicator in form_text for indicator in contact_indicators):
                    contact_forms.append(form)
            except:
                continue

        return contact_forms if contact_forms else forms

    async def _process_forms(
        self, page: Page, forms: List[Any], user_data: Dict, result: Dict
    ) -> Dict:
        """Process detected forms with user profile data and CAPTCHA solving."""
        # Use profile data if user_data is not comprehensive
        if self.user_id and len(user_data) < 3:  # Minimal data provided
            profile_data = await self._get_user_profile_data()
            user_data = {
                **profile_data,
                **user_data,
            }  # Merge, with user_data taking precedence

        for i, form in enumerate(forms, 1):
            self._log_info(f"Processing form {i}/{len(forms)}")

            # Detect and solve CAPTCHA if present
            captcha_solved = False
            captcha_type = None

            if self.captcha_service:
                captcha_solved = await self.captcha_service.solve_if_present(page)
                if captcha_solved:
                    result["details"]["captcha_solved"] = True
                    self._log_info("CAPTCHA solved successfully")

                    # Detect which type was solved for logging
                    detected_types = await self.captcha_service.detect_captcha_types(
                        page
                    )
                    for ctype, detected in detected_types.items():
                        if detected:
                            captcha_type = ctype
                            break
                    result["details"]["captcha_type"] = captcha_type

            # Fill form
            filled_count = await self._fill_form_comprehensive(page, form, user_data)
            result["details"]["form_fields_filled"] = filled_count

            if filled_count > 0:
                self._log_info(f"Filled {filled_count} form fields")

                # Submit form
                submitted, submit_method = await self._submit_form(page, form)
                if submitted:
                    self._log_info(f"Form submitted via {submit_method}")

                    # Wait and check for success
                    await asyncio.sleep(3)
                    success_hint = await self._detect_success_indicators(page)

                    result["success"] = True
                    result["method"] = "form"
                    result["details"]["submitted_via"] = submit_method
                    result["details"]["success_hint"] = success_hint

                    self._log_info(
                        f"Form submission successful: {success_hint or 'No specific success message'}"
                    )
                    return result

        return result

    async def _fill_form_comprehensive(
        self, page: Page, form: Any, user_data: Dict
    ) -> int:
        """Comprehensively fill form with user profile data."""
        filled_count = 0

        # Field mapping with multiple selectors for each field type
        field_mappings = {
            "email": {
                "selectors": [
                    'input[type="email"]',
                    'input[name*="email" i]',
                    'input[id*="email" i]',
                    'input[placeholder*="email" i]',
                ],
                "value": user_data.get("email", ""),
            },
            "first_name": {
                "selectors": [
                    'input[name*="first" i]',
                    'input[id*="first" i]',
                    'input[placeholder*="first" i]',
                ],
                "value": user_data.get("first_name", ""),
            },
            "last_name": {
                "selectors": [
                    'input[name*="last" i]',
                    'input[id*="last" i]',
                    'input[placeholder*="last" i]',
                ],
                "value": user_data.get("last_name", ""),
            },
            "full_name": {
                "selectors": [
                    'input[name*="name" i]:not([name*="first" i]):not([name*="last" i])',
                    'input[id*="name" i]:not([id*="first" i]):not([id*="last" i])',
                    'input[placeholder*="name" i]:not([placeholder*="first" i]):not([placeholder*="last" i])',
                ],
                "value": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            },
            "phone": {
                "selectors": [
                    'input[type="tel"]',
                    'input[name*="phone" i]',
                    'input[id*="phone" i]',
                    'input[placeholder*="phone" i]',
                ],
                "value": user_data.get("phone_number", ""),
            },
            "company": {
                "selectors": [
                    'input[name*="company" i]',
                    'input[id*="company" i]',
                    'input[placeholder*="company" i]',
                    'input[name*="organization" i]',
                ],
                "value": user_data.get("company_name", ""),
            },
            "job_title": {
                "selectors": [
                    'input[name*="title" i]',
                    'input[id*="title" i]',
                    'input[placeholder*="title" i]',
                    'input[name*="position" i]',
                ],
                "value": user_data.get("job_title", ""),
            },
            "subject": {
                "selectors": [
                    'input[name*="subject" i]',
                    'input[id*="subject" i]',
                    'input[placeholder*="subject" i]',
                ],
                "value": user_data.get("subject", "Business Inquiry"),
            },
            "message": {
                "selectors": [
                    'textarea[name*="message" i]',
                    'textarea[id*="message" i]',
                    'textarea[placeholder*="message" i]',
                    'textarea[name*="comment" i]',
                    "textarea",
                ],
                "value": user_data.get(
                    "message",
                    "I am interested in your services and would like to discuss business opportunities.",
                ),
            },
            "website": {
                "selectors": [
                    'input[type="url"]',
                    'input[name*="website" i]',
                    'input[id*="website" i]',
                    'input[placeholder*="website" i]',
                ],
                "value": user_data.get("website_url", ""),
            },
        }

        # Fill each field type
        for field_name, field_info in field_mappings.items():
            if not field_info["value"]:
                continue

            for selector in field_info["selectors"]:
                try:
                    element = await form.query_selector(selector)
                    if element and await element.is_visible():
                        await element.fill(field_info["value"])
                        filled_count += 1
                        self._log_info(
                            f"Filled {field_name} field with: {field_info['value'][:50]}"
                        )
                        break
                except Exception as e:
                    continue

        return filled_count

    async def _submit_form(self, page: Page, form: Any) -> tuple[bool, str]:
        """Submit form using multiple strategies."""
        try:
            # Strategy 1: Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Send")',
                'button:has-text("Submit")',
                'button:has-text("Contact")',
                'button:has-text("Send Message")',
                'button:has-text("Get in Touch")',
            ]

            for selector in submit_selectors:
                try:
                    button = await form.query_selector(selector)
                    if button and await button.is_visible():
                        await button.click()

                        # Wait for navigation or response
                        try:
                            await page.wait_for_load_state("networkidle", timeout=10000)
                        except:
                            pass

                        await asyncio.sleep(2)
                        return True, f"button:{selector}"

                except Exception:
                    continue

            # Strategy 2: Try Enter key on last input
            try:
                inputs = await form.query_selector_all("input, textarea")
                if inputs:
                    last_input = inputs[-1]
                    await last_input.press("Enter")

                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        pass

                    await asyncio.sleep(2)
                    return True, "enter_key"

            except Exception:
                pass

            return False, "no_submit_method"

        except Exception as e:
            self._log_error(f"Form submission error: {e}")
            return False, f"error:{str(e)[:50]}"

    async def _detect_success_indicators(self, page: Page) -> Optional[str]:
        """Detect success indicators after form submission."""
        try:
            # Wait a moment for success messages to appear
            await asyncio.sleep(2)

            # Get page content
            content = await page.content()
            content_lower = content.lower()

            # Success patterns
            success_patterns = [
                "thank you",
                "thanks",
                "success",
                "successfully",
                "submitted",
                "received",
                "message sent",
                "we'll get back",
                "we will get back",
                "we'll be in touch",
                "we will be in touch",
                "your message has been sent",
                "form submitted",
                "submission received",
            ]

            for pattern in success_patterns:
                if pattern in content_lower:
                    self._log_info(f"Success indicator found: {pattern}")
                    return pattern

            # Check for success-indicating elements
            success_selectors = [
                ".success",
                ".alert-success",
                ".message-success",
                '[class*="success"]',
                '[id*="success"]',
            ]

            for selector in success_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        text = await element.inner_text()
                        if text and len(text.strip()) > 0:
                            return f"success_element:{text[:50]}"
                except:
                    continue

            return None

        except Exception as e:
            self._log_error(f"Success detection error: {e}")
            return None

    async def _process_contact_page(
        self, page: Page, contact_url: str, user_data: Dict, result: Dict
    ) -> Dict:
        """Process contact page if found."""
        try:
            self._log_info(f"Navigating to contact page: {contact_url}")
            await page.goto(contact_url, wait_until="domcontentloaded")
            result["details"]["pages_checked"].append(contact_url)

            await asyncio.sleep(2)
            await self._wait_for_dynamic_content(page)

            # Process forms on contact page
            contact_forms = await self._detect_forms(page)
            if contact_forms:
                self._log_info(f"Found {len(contact_forms)} form(s) on contact page")
                return await self._process_forms(page, contact_forms, user_data, result)

        except Exception as e:
            self._log_warning(f"Error processing contact page: {e}")

        return result

    async def _find_contact_page(self, page: Page) -> Optional[str]:
        """Find contact page link."""
        try:
            contact_selectors = [
                'a[href*="contact" i]',
                'a[href*="get-in-touch" i]',
                'a[href*="reach-out" i]',
                'a:has-text("Contact")',
                'a:has-text("Contact Us")',
                'a:has-text("Get in Touch")',
                'a:has-text("Reach Out")',
            ]

            for selector in contact_selectors:
                try:
                    link = await page.query_selector(selector)
                    if link:
                        href = await link.get_attribute("href")
                        if href:
                            return urljoin(page.url, href)
                except:
                    continue

            return None

        except Exception as e:
            self._log_warning(f"Error finding contact page: {e}")
            return None

    async def _extract_emails_comprehensive(self, page: Page) -> List[str]:
        """Comprehensive email extraction."""
        emails = set()

        try:
            # Strategy 1: mailto links
            mailto_links = await page.query_selector_all('a[href^="mailto:"]')
            for link in mailto_links[:5]:
                try:
                    href = await link.get_attribute("href")
                    if href:
                        email = href.replace("mailto:", "").split("?")[0].strip()
                        if self._is_valid_email(email):
                            emails.add(email)
                except:
                    continue

            # Strategy 2: text content scanning
            try:
                body_text = await page.inner_text("body")
                email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                found_emails = re.findall(email_pattern, body_text)

                for email in found_emails[:10]:
                    if self._is_valid_email(email):
                        emails.add(email)

            except Exception as e:
                self._log_warning(f"Text email extraction error: {e}")

            # Strategy 3: specific sections
            email_sections = [
                "footer",
                ".footer",
                "#footer",
                ".contact",
                ".contact-info",
            ]
            for section in email_sections:
                try:
                    element = await page.query_selector(section)
                    if element:
                        section_text = await element.inner_text()
                        section_emails = re.findall(
                            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                            section_text,
                        )
                        for email in section_emails[:3]:
                            if self._is_valid_email(email):
                                emails.add(email)
                except:
                    continue

            # Filter and return
            filtered_emails = [
                email
                for email in emails
                if not any(
                    exclude in email.lower()
                    for exclude in ["noreply", "no-reply", "example.com", "test@"]
                )
            ]

            if filtered_emails:
                self._log_info(
                    f"Extracted {len(filtered_emails)} emails: {filtered_emails[:3]}"
                )

            return list(filtered_emails)[:5]

        except Exception as e:
            self._log_error(f"Email extraction error: {e}")
            return []

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or len(email) > 254:
            return False

        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
        return bool(re.match(email_pattern, email))
