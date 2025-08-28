from typing import Dict, List, Optional, Any
from playwright.async_api import Page, ElementHandle

from app.utils.constants import FORM_FIELD_PATTERNS, CONTACT_FORM_INDICATORS


class FormService:
    """Handles form detection and interaction"""

    async def find_contact_forms(self, page: Page) -> List[ElementHandle]:
        """Find potential contact forms on page"""
        forms = await page.query_selector_all("form")
        contact_forms = []

        for form in forms:
            if await self._is_contact_form(form):
                contact_forms.append(form)

        return contact_forms

    async def identify_fields(self, form: ElementHandle) -> Dict[str, str]:
        """Map form fields to their types"""
        fields = {}

        for field_type, patterns in FORM_FIELD_PATTERNS.items():
            for pattern in patterns:
                element = await form.query_selector(pattern)
                if element and await element.is_visible():
                    selector = await self._get_element_selector(element)
                    if selector:
                        fields[field_type] = selector
                        break

        return fields

    async def fill_form(
        self, page: Page, fields: Dict[str, str], data: Dict[str, Any]
    ) -> bool:
        """Fill form fields with provided data"""
        try:
            for field_type, selector in fields.items():
                if field_type in data and data[field_type]:
                    await page.fill(selector, str(data[field_type]))

            return True
        except Exception:
            return False

    async def submit_form(self, form: ElementHandle) -> bool:
        """Submit the form"""
        submit_button = await form.query_selector(
            'button[type="submit"], input[type="submit"], '
            'button:has-text("send"), button:has-text("submit")'
        )

        if submit_button:
            await submit_button.click()
            return True

        return False

    async def _is_contact_form(self, form: ElementHandle) -> bool:
        """Check if form is likely a contact form"""
        form_html = await form.inner_html()
        form_text = form_html.lower()

        return any(indicator in form_text for indicator in CONTACT_FORM_INDICATORS)

    async def _get_element_selector(self, element: ElementHandle) -> Optional[str]:
        """Generate a reliable selector for an element"""
        # Try name attribute first
        name = await element.get_attribute("name")
        if name:
            return f'[name="{name}"]'

        # Then ID
        element_id = await element.get_attribute("id")
        if element_id:
            return f"#{element_id}"

        # Then class
        class_attr = await element.get_attribute("class")
        if class_attr:
            classes = class_attr.split()
            if classes:
                return f".{classes[0]}"

        return None
