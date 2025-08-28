import asyncio
import aiohttp
import base64
import json
from typing import Optional, Dict, Any
from playwright.async_api import Page

from app.core.config import settings


class CaptchaService:
    """Handles CAPTCHA detection and solving"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.api_url = settings.CAPTCHA_DBC_API_URL  # Updated to uppercase field name

    async def detect_captcha_type(self, page: Page) -> Optional[str]:
        """Detect CAPTCHA type on page"""
        captcha_types = {
            "recaptcha": ".g-recaptcha",
            "hcaptcha": ".h-captcha",
            "turnstile": ".cf-turnstile",
            "image": 'img[src*="captcha"]',
        }

        for captcha_type, selector in captcha_types.items():
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                return captcha_type

        return None

    async def solve(self, page: Page, captcha_type: str) -> bool:
        """Solve CAPTCHA based on type"""
        solvers = {
            "recaptcha": self._solve_recaptcha,
            "hcaptcha": self._solve_hcaptcha,
            "image": self._solve_image_captcha,
        }

        solver = solvers.get(captcha_type)
        if solver:
            return await solver(page)

        return False

    async def _solve_recaptcha(self, page: Page) -> bool:
        """Solve Google reCAPTCHA"""
        # Get site key
        site_key = await page.get_attribute(".g-recaptcha", "data-sitekey")
        if not site_key:
            return False

        # Get solution from API
        solution = await self._call_dbc_api(
            "recaptcha", {"googlekey": site_key, "pageurl": page.url}
        )

        if solution:
            # Inject solution
            await page.evaluate(
                f"""
                document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                if (window.grecaptcha && window.grecaptcha.getResponse) {{
                    window.grecaptcha.getResponse = () => '{solution}';
                }}
            """
            )
            return True

        return False

    async def _solve_image_captcha(self, page: Page) -> bool:
        """Solve image CAPTCHA"""
        # Get CAPTCHA image
        captcha_img = await page.query_selector('img[src*="captcha"]')
        if not captcha_img:
            return False

        # Screenshot CAPTCHA
        image_data = await captcha_img.screenshot()

        # Get solution
        solution = await self._call_dbc_api("image", {"image": image_data})

        if solution:
            # Find input and enter solution
            captcha_input = await page.query_selector(
                'input[name*="captcha"], input[placeholder*="captcha"]'
            )
            if captcha_input:
                await captcha_input.fill(solution)
                return True

        return False

    async def _call_dbc_api(
        self, captcha_type: str, params: Dict[str, Any]
    ) -> Optional[str]:
        """Call DeathByCaptcha API"""
        payload = {"username": self.username, "password": self.password}

        if captcha_type == "image":
            image_b64 = base64.b64encode(params["image"]).decode()
            payload["captchafile"] = f"base64:{image_b64}"
        elif captcha_type == "recaptcha":
            payload["type"] = 4
            payload["token_params"] = json.dumps(params)

        async with aiohttp.ClientSession() as session:
            # Submit CAPTCHA
            async with session.post(
                f"{self.api_url}/captcha", data=payload
            ) as response:
                if response.status != 200:
                    return None

                result = await response.json()
                captcha_id = result.get("captcha")

                if not captcha_id:
                    return None

                # Poll for solution
                for _ in range(
                    settings.CAPTCHA_SOLVE_TIMEOUT // 5
                ):  # Updated to uppercase field name
                    await asyncio.sleep(5)

                    async with session.get(
                        f"{self.api_url}/captcha/{captcha_id}"
                    ) as poll_response:
                        if poll_response.status == 200:
                            poll_result = await poll_response.json()
                            if poll_result.get("text"):
                                return poll_result["text"]

        return None

    async def _solve_hcaptcha(self, page: Page) -> bool:
        """Solve hCaptcha (placeholder for implementation)"""
        # Similar to reCAPTCHA but with hCaptcha specific logic
        return False
