# test_subprocess_fix.py - Test if the subprocess fix works
import threading
import asyncio
import sys
import os


def test_subprocess_browser():
    """Test if subprocess can launch visible browser like the fix"""

    async def run_browser_test():
        """Run browser in subprocess-like environment"""
        from playwright.async_api import async_playwright

        print(f"Thread environment check:")
        print(f"  DEV_AUTOMATION_HEADFUL = {os.getenv('DEV_AUTOMATION_HEADFUL')}")
        print(f"  BROWSER_HEADLESS = {os.getenv('BROWSER_HEADLESS')}")

        playwright = None
        browser = None

        try:
            playwright = await async_playwright().start()
            print("Playwright started in thread")

            # Force visible browser like the fix
            browser = await playwright.chromium.launch(
                headless=False,  # FORCED visible
                slow_mo=1000,  # FORCED slow motion
                args=["--start-maximized", "--no-sandbox", "--disable-dev-shm-usage"],
            )
            print("Browser launched in thread - should be VISIBLE!")

            page = await browser.new_page()
            await page.goto("https://example.com")
            print("Page loaded - browser should be visible now!")

            await asyncio.sleep(10)
            print("Test completed")

        except Exception as e:
            print(f"Error in thread: {e}")

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

    def thread_target():
        """Thread that mimics your subprocess"""
        # Force environment variables in thread (like the fix)
        os.environ["DEV_AUTOMATION_HEADFUL"] = "true"
        os.environ["DEV_AUTOMATION_SLOWMO_MS"] = "1000"
        os.environ["BROWSER_HEADLESS"] = "false"

        print(f"Set environment variables in thread")

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(run_browser_test())
        finally:
            loop.close()

    print("=" * 60)
    print("TESTING SUBPROCESS BROWSER FIX")
    print("=" * 60)
    print("Starting browser test in thread...")

    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()

    print("Thread test completed")


if __name__ == "__main__":
    test_subprocess_browser()
