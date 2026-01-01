"""Browser lifecycle management using Playwright."""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from loguru import logger


class BrowserDriver:
    """Manages browser lifecycle: launch, close, create contexts."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def launch(self) -> None:
        """Launch the browser."""
        logger.info(f"Launching browser (headless={self.headless})")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        await self._create_context()
        logger.info("Browser launched successfully")

    async def _create_context(self) -> None:
        """Create a new browser context with default settings."""
        if not self._browser:
            raise RuntimeError("Browser not launched")

        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        self._page = await self._context.new_page()
        logger.debug("Browser context created")

    @property
    def page(self) -> Page:
        """Get the current page."""
        if not self._page:
            raise RuntimeError("No page available - browser not launched")
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Get the current browser context."""
        if not self._context:
            raise RuntimeError("No context available - browser not launched")
        return self._context

    async def new_page(self) -> Page:
        """Create a new page in the current context."""
        if not self._context:
            raise RuntimeError("No context available - browser not launched")
        self._page = await self._context.new_page()
        return self._page

    async def close(self) -> None:
        """Close the browser and clean up resources."""
        logger.info("Closing browser")
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Browser closed")

    async def __aenter__(self) -> "BrowserDriver":
        """Async context manager entry."""
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
