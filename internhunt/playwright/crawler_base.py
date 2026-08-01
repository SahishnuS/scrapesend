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

    # Button text patterns that trigger loading more job results
    _LOAD_MORE_TEXTS = [
        "load more", "show more", "see more", "more jobs", "more results",
        "view more", "load more jobs", "show more jobs", "next page",
        "more openings", "show all", "load all",
    ]

    # Maximum number of "load more" clicks per page to avoid infinite loops
    _MAX_PAGINATION_CLICKS = 5

    async def fetch_html(self, url: str) -> str:
        """
        Navigate to a URL, expand paginated/infinite-scroll content, and
        return the fully rendered HTML.

        Strategy:
          1. Wait for the page to reach network idle (JS fully executed).
          2. Scroll to the bottom to trigger any infinite-scroll loaders.
          3. Look for common "Load More" / "Show More" buttons and click them.
          4. Repeat steps 2-3 up to _MAX_PAGINATION_CLICKS times.
          5. Return the expanded HTML for the ATS handler to parse.
        """
        page = await self.get_page()
        try:
            log.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=45000)
            await asyncio.sleep(3)

            for click_num in range(self._MAX_PAGINATION_CLICKS):
                # ── Step 1: Scroll to bottom to trigger infinite scroll ────────
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

                # ── Step 2: Look for a "Load More" style button ───────────────
                clicked = False
                for text in self._LOAD_MORE_TEXTS:
                    # Try exact case-insensitive text match first
                    btn = page.get_by_role("button", name=text, exact=False)
                    try:
                        if await btn.first.is_visible(timeout=1500):
                            await btn.first.scroll_into_view_if_needed()
                            await btn.first.click()
                            log.info(
                                "Clicked pagination button",
                                url=url,
                                button_text=text,
                                click_num=click_num + 1,
                            )
                            # Wait for new content to load
                            await page.wait_for_load_state("networkidle", timeout=15000)
                            await asyncio.sleep(2)
                            clicked = True
                            break
                    except Exception:
                        continue

                # If no button was found and clicked, the page is fully loaded
                if not clicked:
                    log.info(
                        "No more pagination buttons found, page fully loaded",
                        url=url,
                        pages_loaded=click_num + 1,
                    )
                    break

            html = await page.content()
            return html
        except Exception as e:
            log.error(f"Failed to fetch {url}", error=str(e))
            return ""
        finally:
            await page.close()

