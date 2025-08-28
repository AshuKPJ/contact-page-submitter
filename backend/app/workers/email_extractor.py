import re


class EmailExtractor:
    PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    async def extract(self, page):
        # Try mailto
        try:
            mailto = await page.query_selector('a[href^="mailto:"]')
            if mailto:
                href = await mailto.get_attribute("href")
                return href.replace("mailto:", "").split("?")[0]
        except:
            pass

        # Search text
        try:
            text = await page.inner_text("body")
            emails = re.findall(self.PATTERN, text)
            for email in emails:
                if "@example." not in email:
                    return email
        except:
            pass
        return None
