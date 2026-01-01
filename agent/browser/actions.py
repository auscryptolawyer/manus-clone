"""Atomic browser actions: click, type, scroll, navigate."""

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
from loguru import logger

from api.schemas import ActionResult


class BrowserActions:
    """Executes atomic browser actions."""

    def __init__(self, page: Page, timeout: int = 5000):
        self.page = page
        self.timeout = timeout

    async def navigate(self, url: str) -> ActionResult:
        """Navigate to a URL."""
        logger.info(f"Navigating to: {url}")
        try:
            await self.page.goto(url, timeout=self.timeout * 2, wait_until="domcontentloaded")
            return ActionResult(success=True)
        except PlaywrightTimeout:
            logger.warning(f"Navigation timeout: {url}")
            return ActionResult(success=False, error=f"Timeout navigating to {url}")
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return ActionResult(success=False, error=str(e))

    async def click(self, selector: str) -> ActionResult:
        """Click an element by selector."""
        logger.info(f"Clicking: {selector}")
        try:
            await self.page.click(selector, timeout=self.timeout)
            return ActionResult(success=True)
        except PlaywrightTimeout:
            logger.warning(f"Click timeout: {selector}")
            return ActionResult(success=False, error=f"Element not found: {selector}")
        except Exception as e:
            logger.error(f"Click error: {e}")
            return ActionResult(success=False, error=str(e))

    async def click_element_id(self, element_id: int, elements: list[dict]) -> ActionResult:
        """Click an element by its numeric ID from the element list."""
        element = next((e for e in elements if e.get("id") == element_id), None)
        if not element:
            return ActionResult(success=False, error=f"Element ID {element_id} not found")
        return await self.click(element["selector"])

    async def type_text(
        self, text: str, selector: str | None = None, clear_first: bool = True
    ) -> ActionResult:
        """Type text into an element or the focused element."""
        logger.info(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
        try:
            if selector:
                if clear_first:
                    await self.page.fill(selector, text, timeout=self.timeout)
                else:
                    await self.page.type(selector, text, timeout=self.timeout)
            else:
                # Type into currently focused element
                await self.page.keyboard.type(text)
            return ActionResult(success=True)
        except PlaywrightTimeout:
            logger.warning(f"Type timeout: {selector}")
            return ActionResult(success=False, error=f"Element not found: {selector}")
        except Exception as e:
            logger.error(f"Type error: {e}")
            return ActionResult(success=False, error=str(e))

    async def type_element_id(
        self, element_id: int, text: str, elements: list[dict], clear_first: bool = True
    ) -> ActionResult:
        """Type text into an element by its numeric ID."""
        element = next((e for e in elements if e.get("id") == element_id), None)
        if not element:
            return ActionResult(success=False, error=f"Element ID {element_id} not found")
        return await self.type_text(text, element["selector"], clear_first)

    async def scroll(self, direction: str = "down", amount: str = "half_page") -> ActionResult:
        """Scroll the page."""
        logger.info(f"Scrolling {direction} by {amount}")
        try:
            # Calculate scroll amount in pixels
            viewport_height = self.page.viewport_size["height"] if self.page.viewport_size else 720
            scroll_amounts = {
                "small": viewport_height // 4,
                "half_page": viewport_height // 2,
                "full_page": viewport_height,
            }
            pixels = scroll_amounts.get(amount, viewport_height // 2)

            if direction == "up":
                pixels = -pixels

            await self.page.evaluate(f"window.scrollBy(0, {pixels})")
            return ActionResult(success=True)
        except Exception as e:
            logger.error(f"Scroll error: {e}")
            return ActionResult(success=False, error=str(e))

    async def wait(self, seconds: float = 1.0, for_selector: str | None = None) -> ActionResult:
        """Wait for a duration or for an element to appear."""
        try:
            if for_selector:
                logger.info(f"Waiting for element: {for_selector}")
                await self.page.wait_for_selector(for_selector, timeout=int(seconds * 1000))
            else:
                logger.info(f"Waiting {seconds} seconds")
                await self.page.wait_for_timeout(int(seconds * 1000))
            return ActionResult(success=True)
        except PlaywrightTimeout:
            logger.warning(f"Wait timeout for: {for_selector}")
            return ActionResult(success=False, error=f"Timeout waiting for: {for_selector}")
        except Exception as e:
            logger.error(f"Wait error: {e}")
            return ActionResult(success=False, error=str(e))

    async def press_key(self, key: str) -> ActionResult:
        """Press a keyboard key."""
        logger.info(f"Pressing key: {key}")
        try:
            await self.page.keyboard.press(key)
            return ActionResult(success=True)
        except Exception as e:
            logger.error(f"Key press error: {e}")
            return ActionResult(success=False, error=str(e))

    async def select_option(self, selector: str, value: str) -> ActionResult:
        """Select an option from a dropdown."""
        logger.info(f"Selecting '{value}' from {selector}")
        try:
            await self.page.select_option(selector, value, timeout=self.timeout)
            return ActionResult(success=True)
        except PlaywrightTimeout:
            logger.warning(f"Select timeout: {selector}")
            return ActionResult(success=False, error=f"Element not found: {selector}")
        except Exception as e:
            logger.error(f"Select error: {e}")
            return ActionResult(success=False, error=str(e))
