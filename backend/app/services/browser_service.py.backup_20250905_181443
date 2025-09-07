from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import random

from app.core.config import settings
from app.utils.constants import USER_AGENTS, BROWSER_ARGS


class BrowserService:
    """Manages browser instances and contexts"""

    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        """Initialize Playwright and browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.browser.headless, args=BROWSER_ARGS
        )

    async def stop(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def create_context(self, proxy: Optional[str] = None) -> BrowserContext:
        """Create a new browser context with stealth settings"""
        context_options = {
            "viewport": {
                "width": settings.browser.viewport_width,
                "height": settings.browser.viewport_height,
            },
            "user_agent": random.choice(USER_AGENTS),
            "extra_http_headers": self._get_default_headers(),
        }

        if proxy:
            context_options["proxy"] = {"server": proxy}

        context = await self.browser.new_context(**context_options)
        await self._add_stealth_scripts(context)

        return context

    async def create_page(self, context: BrowserContext) -> Page:
        """Create a new page with default settings"""
        page = await context.new_page()
        page.set_default_timeout(settings.browser.page_load_timeout)
        return page

    @staticmethod
    def _get_default_headers() -> Dict[str, str]:
        """Get default browser headers"""
        return {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
        }

    @staticmethod
    async def _add_stealth_scripts(context: BrowserContext):
        """Add stealth scripts to avoid detection"""
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """
        )
