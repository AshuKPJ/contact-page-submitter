# app/workers/subprocess_runner.py
"""Subprocess runner with Windows ProactorEventLoop support and forced visible browser."""

import asyncio
import sys
import logging
from typing import Callable, Any
import threading
import os
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SubprocessRunner:
    """Runner that ensures proper event loop for subprocess operations on Windows."""

    @staticmethod
    def run_with_proactor_loop(coro):
        """Run a coroutine with ProactorEventLoop on Windows."""
        if sys.platform == "win32":
            # Create a new ProactorEventLoop
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            logger.info("Created ProactorEventLoop for subprocess operations")
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(coro)
        finally:
            try:
                # Clean up pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()

                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )

                loop.close()
            except Exception as e:
                logger.warning(f"Error closing event loop: {e}")


def run_campaign_in_subprocess(campaign_id: str, user_id: str = None):
    """Run campaign in a separate thread with proper event loop and VISIBLE browser."""
    from .campaign_processor import CampaignProcessor

    async def _run_campaign():
        """Inner async function to run the campaign with forced visible browser."""
        # Force environment variables here as well (belt and suspenders approach)
        os.environ["DEV_AUTOMATION_HEADFUL"] = "true"
        os.environ["DEV_AUTOMATION_SLOWMO_MS"] = "1000"
        os.environ["BROWSER_HEADLESS"] = "false"

        logger.info(
            f"Campaign async function - Environment: HEADFUL={os.getenv('DEV_AUTOMATION_HEADFUL')}"
        )

        processor = CampaignProcessor(campaign_id, user_id=user_id)
        await processor.run()

    def thread_target():
        """Thread target that sets up ProactorEventLoop and runs the campaign with visible browser."""
        # CRITICAL: Set environment variables directly in the thread
        os.environ["DEV_AUTOMATION_HEADFUL"] = "true"
        os.environ["DEV_AUTOMATION_SLOWMO_MS"] = "1000"
        os.environ["BROWSER_HEADLESS"] = "false"

        logger.info(
            f"Thread environment set: HEADFUL={os.getenv('DEV_AUTOMATION_HEADFUL')}, SLOWMO={os.getenv('DEV_AUTOMATION_SLOWMO_MS')}"
        )

        if sys.platform == "win32":
            # Set ProactorEventLoop policy for this thread
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            logger.info("Set ProactorEventLoop policy in thread")

        # Create and run the event loop
        SubprocessRunner.run_with_proactor_loop(_run_campaign())

    # Create and start the thread
    thread = threading.Thread(target=thread_target, name=f"Campaign-{campaign_id[:8]}")
    thread.start()

    # Don't wait for the thread to complete (fire and forget)
    logger.info(
        f"Started VISIBLE browser campaign {campaign_id[:8]} in background thread: {thread.name}"
    )

    return thread
