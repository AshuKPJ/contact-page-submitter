import asyncio
from app.services.browser_automation_service import BrowserAutomationService


async def test_single_website():
    service = BrowserAutomationService()
    await service.initialize()

    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "555-1234",
        "company_name": "Test Company",
        "message": "This is a test message.",
    }

    result = await service.process_website("https://example.com/contact", test_data)

    print(f"Result: {result}")

    await service.cleanup()


if __name__ == "__main__":
    asyncio.run(test_single_website())
