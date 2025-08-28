class FormHandler:
    FIELDS = {
        'input[type="email"]': "email",
        'input[name*="name"]': "name",
        "textarea": "message",
        'input[type="tel"]': "phone",
    }

    BUTTONS = [
        'button[type="submit"]',
        'button:has-text("Send")',
        'button:has-text("Submit")',
    ]

    async def fill(self, page, data):
        filled = 0
        for selector, field in self.FIELDS.items():
            if field in data and data[field]:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.fill(data[field])
                        filled += 1
                except:
                    pass
        return filled

    async def submit(self, page):
        for selector in self.BUTTONS:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    await page.wait_for_timeout(3000)
                    return True
            except:
                pass
        return False
