"""Playwright browser state management for LLMOps"""

from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class PlaywrightState:
    """Global browser state management for Playwright automation"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_initialized = False
    
    async def initialize(self, headless: bool = False, browser_type: str = "chromium"):
        """
        Initialize Playwright browser
        
        Args:
            headless: Run browser in headless mode
            browser_type: Browser type (chromium, firefox, webkit, edge)
        """
        if self.is_initialized:
            return
        
        self.playwright = await async_playwright().start()
        
        # Launch browser based on type
        if browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=headless)
        elif browser_type == "edge":
            # Microsoft Edge support
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                channel="msedge"
            )
        else:  # chromium (default)
            self.browser = await self.playwright.chromium.launch(headless=headless)
        
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.is_initialized = True
        
        print(f"[BROWSER] Launched {browser_type} browser (headless={headless})")
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()  
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.is_initialized = False
        print("[BROWSER] Cleaned up browser resources")
    
    def is_ready(self) -> bool:
        """Check if browser is initialized and ready"""
        return self.is_initialized and self.page is not None


# Global playwright state instance
pw_state = PlaywrightState()


def get_playwright_state() -> PlaywrightState:
    """Get the global Playwright state instance"""
    return pw_state
