import asyncio
import logging
import subprocess
import requests
from playwright.async_api import (
    Browser as PlaywrightBrowser,
    Playwright,
)
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig
from .custom_context import CustomBrowserContext

logger = logging.getLogger(__name__)

class CustomBrowser(Browser):

    async def new_context(
        self,
        config: BrowserContextConfig = BrowserContextConfig()
    ) -> CustomBrowserContext:
        return CustomBrowserContext(config=config, browser=self)

    async def _setup_browser_with_instance(self, playwright: Playwright) -> PlaywrightBrowser:
        """Sets up and returns a Playwright Browser instance."""

        CHROME_PATH = self.config.chrome_instance_path
        CDP_ENDPOINT = 'http://127.0.0.1:9222'
        USER_DATA_DIR = '/tmp/chrome-debug'

        def chrome_is_running():
            try:
                r = requests.get(f"{CDP_ENDPOINT}/json/version", timeout=2)
                return r.status_code == 200
            except requests.RequestException:
                return False

        # Step 1: Check if Chrome is already running
        if not chrome_is_running():
            logger.info("🔁 Starting Chrome with debug mode...")

            # Build Chrome command, override --user-data-dir if needed
            chrome_cmd = [
                CHROME_PATH,
                "--remote-debugging-port=9222",
                f"--user-data-dir={USER_DATA_DIR}",
                "--no-first-run",
                "--no-default-browser-check",
                "--window-size=1280,1100"
            ]

            subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait until Chrome is up
            for i in range(10):
                if chrome_is_running():
                    logger.info("✅ Chrome is ready.")
                    break
                await asyncio.sleep(1)
            else:
                raise RuntimeError("❌ Timeout waiting for Chrome to become ready.")

        # Step 2: Connect to Chrome via CDP
        browser = await playwright.chromium.connect_over_cdp(
            endpoint_url=CDP_ENDPOINT,
            timeout=20000
        )
        return browser
