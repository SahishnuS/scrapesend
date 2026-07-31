"""
Base Playwright Crawler Framework.
Provides headless browser initialization, stealth configuration, and basic page fetching.
"""

from playwright.async_api import async_playwright, Browser, Page
import structlog
import asyncio

log = structlog.get_logger(__name__)

class BaseCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Browser = None

    async def start(self):
        """Initialise the Playwright browser with stealth-like arguments."""
        self._playwright = await async_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]
        
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=args
        )
        log.info("Browser started successfully.")

    async def stop(self):
        """Close browser resources."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        log.info("Browser stopped.")

    async def get_page(self) -> Page:
        """Create a new page context masquerading as a normal user."""
        context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            has_touch=False,
            is_mobile=False,
        )
        
        # Override navigator.webdriver to bypass basic bot checks
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        return page

    async def fetch_html(self, url: str) -> str:
        """Navigate to a URL and return the rendered HTML."""
        page = await self.get_page()
        try:
            log.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait a short random time to allow lazy-loaded elements
            await asyncio.sleep(2) 
            
            html = await page.content()
            return html
        except Exception as e:
            log.error(f"Failed to fetch {url}", error=str(e))
            return ""
        finally:
            await page.close()
