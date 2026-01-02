"""Page state extraction: screenshot, DOM summary, interactive elements."""

import base64
from playwright.async_api import Page
from loguru import logger

from api.schemas import PageState, Element


class PageObserver:
    """Extracts page state for the agent."""

    def __init__(self, page: Page, screenshot_quality: int = 50):
        self.page = page
        self.screenshot_quality = screenshot_quality

    async def observe(self) -> PageState:
        """Capture the current page state."""
        logger.debug("Observing page state")

        url = self.page.url
        title = await self.page.title()

        # Run extraction tasks
        screenshot_b64 = await self._capture_screenshot()
        elements = await self._extract_interactive_elements()
        visible_text = await self._extract_visible_text()

        state = PageState(
            url=url,
            title=title,
            interactive_elements=elements,
            visible_text=visible_text,
            screenshot_base64=screenshot_b64,
        )

        logger.debug(f"Observed: {url} with {len(elements)} interactive elements")
        return state

    async def _capture_screenshot(self) -> str:
        """Capture a screenshot and return as base64."""
        try:
            screenshot_bytes = await self.page.screenshot(
                type="jpeg",
                quality=self.screenshot_quality,
                full_page=False,
            )
            return base64.b64encode(screenshot_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ""

    async def _extract_interactive_elements(self) -> list[Element]:
        """Extract interactive elements with numeric IDs, prioritizing inputs."""
        js_code = """
        () => {
            const elements = [];
            const seen = new Set();

            // Helper to check visibility
            function isVisible(el) {
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden') return false;
                if (el.offsetWidth === 0 && el.offsetHeight === 0) return false;
                return true;
            }

            // Helper to get element info
            function getElementInfo(el, priority) {
                const tagName = el.tagName.toLowerCase();
                let type = el.type || el.getAttribute('role') || tagName;
                const text = (el.textContent || el.innerText || '').trim().slice(0, 100);
                const placeholder = el.placeholder || el.getAttribute('aria-label') || null;
                const href = el.href || null;
                const name = el.name || el.getAttribute('aria-label') || null;

                // Better type detection
                if (tagName === 'input') {
                    const inputType = el.type?.toLowerCase() || 'text';
                    if (inputType === 'search' ||
                        placeholder?.toLowerCase().includes('search') ||
                        name?.toLowerCase().includes('search') ||
                        el.id?.toLowerCase().includes('search')) {
                        type = 'search-input';
                    } else if (inputType === 'text' || inputType === 'email' || inputType === 'tel') {
                        type = 'text-input';
                    } else {
                        type = inputType + '-input';
                    }
                } else if (tagName === 'textarea') {
                    type = 'textarea';
                } else if (tagName === 'button' || el.getAttribute('role') === 'button') {
                    type = 'button';
                } else if (tagName === 'a') {
                    type = 'link';
                } else if (tagName === 'select') {
                    type = 'dropdown';
                }

                // Generate selector
                let selector = '';
                if (el.id) {
                    selector = '#' + CSS.escape(el.id);
                } else if (el.name) {
                    selector = `${tagName}[name="${CSS.escape(el.name)}"]`;
                } else {
                    const parent = el.parentElement;
                    if (parent) {
                        const siblings = Array.from(parent.children).filter(s => s.tagName === el.tagName);
                        const index = siblings.indexOf(el) + 1;
                        const parentSelector = parent.id
                            ? '#' + CSS.escape(parent.id)
                            : parent.tagName.toLowerCase();
                        selector = `${parentSelector} > ${tagName}:nth-of-type(${index})`;
                    } else {
                        selector = tagName;
                    }
                }

                return {
                    type,
                    text,
                    placeholder,
                    href,
                    selector,
                    priority
                };
            }

            // Priority 1: Search inputs (most important for search tasks)
            document.querySelectorAll('input[type="search"], input[name*="search" i], input[placeholder*="search" i], input[aria-label*="search" i], input#search, input.search').forEach(el => {
                if (!isVisible(el) || seen.has(el)) return;
                seen.add(el);
                elements.push(getElementInfo(el, 1));
            });

            // Priority 2: Other text inputs
            document.querySelectorAll('input[type="text"], input:not([type]), textarea').forEach(el => {
                if (!isVisible(el) || seen.has(el)) return;
                seen.add(el);
                elements.push(getElementInfo(el, 2));
            });

            // Priority 3: Buttons (especially submit/search buttons)
            document.querySelectorAll('button, input[type="submit"], [role="button"]').forEach(el => {
                if (!isVisible(el) || seen.has(el)) return;
                seen.add(el);
                const info = getElementInfo(el, 3);
                // Boost search-related buttons
                if (info.text?.toLowerCase().includes('search') ||
                    info.text?.toLowerCase().includes('go') ||
                    info.text?.toLowerCase().includes('find')) {
                    info.priority = 1.5;
                }
                elements.push(info);
            });

            // Priority 4: Links
            document.querySelectorAll('a[href]').forEach(el => {
                if (!isVisible(el) || seen.has(el)) return;
                seen.add(el);
                elements.push(getElementInfo(el, 4));
            });

            // Priority 5: Other interactive elements
            document.querySelectorAll('select, [role="checkbox"], [role="radio"], [role="tab"], [onclick], [tabindex]:not([tabindex="-1"])').forEach(el => {
                if (!isVisible(el) || seen.has(el)) return;
                seen.add(el);
                elements.push(getElementInfo(el, 5));
            });

            // Sort by priority
            elements.sort((a, b) => a.priority - b.priority);

            return elements;
        }
        """

        try:
            raw_elements = await self.page.evaluate(js_code)

            # Assign numeric IDs (now sorted by priority)
            elements = []
            for i, el in enumerate(raw_elements, start=1):
                elements.append(Element(
                    id=i,
                    type=el.get("type", "unknown"),
                    text=el.get("text", ""),
                    placeholder=el.get("placeholder"),
                    href=el.get("href"),
                    selector=el.get("selector", ""),
                ))

            return elements[:100]  # Limit to 100 elements
        except Exception as e:
            logger.error(f"Element extraction error: {e}")
            return []

    async def _extract_visible_text(self, max_length: int = 2000) -> str:
        """Extract visible text content from the page."""
        js_code = """
        () => {
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: (node) => {
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;

                        const style = window.getComputedStyle(parent);
                        if (style.display === 'none' || style.visibility === 'hidden') {
                            return NodeFilter.FILTER_REJECT;
                        }

                        const tagName = parent.tagName.toLowerCase();
                        if (['script', 'style', 'noscript'].includes(tagName)) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        const text = node.textContent.trim();
                        if (text.length === 0) return NodeFilter.FILTER_REJECT;

                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );

            const textParts = [];
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text) textParts.push(text);
            }

            return textParts.join(' ').replace(/\\s+/g, ' ').trim();
        }
        """

        try:
            text = await self.page.evaluate(js_code)
            if len(text) > max_length:
                text = text[:max_length] + "..."
            return text
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return ""

    def elements_to_dict(self, elements: list[Element]) -> list[dict]:
        """Convert Element list to dict list for action methods."""
        return [el.model_dump() for el in elements]
