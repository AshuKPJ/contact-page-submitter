import re


class FormExtractor:
    SELECTORS = [
        'form[id*="contact"]',
        'form:has(input[type="email"])',
        "form:has(textarea)",
    ]

    async def find(self, page):
        for selector in self.SELECTORS:
            try:
                form = await page.query_selector(selector)
                if form and await form.is_visible():
                    return form
            except:
                continue
        return None

    async def navigate_to_contact(self, page):
        try:
            link = await page.get_by_text(re.compile("contact", re.IGNORECASE)).first
            if link:
                await link.click()
                await page.wait_for_timeout(2000)
                return await self.find(page)
        except:
            return None
