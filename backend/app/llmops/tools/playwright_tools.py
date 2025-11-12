"""Playwright automation tools for LLMOps"""

import os
from typing import List
from langchain_core.tools import tool
from ..utils.playwright_state import get_playwright_state


# Get global playwright state
pw_state = get_playwright_state()


@tool
async def playwright_navigate(url: str) -> str:
    """Navigate browser to a URL. This will open a visible browser window.
    
    Args:
        url: The full URL to navigate to (e.g., https://example.com)
    """
    try:
        if not pw_state.is_initialized:
            await pw_state.initialize(headless=False)
        
        await pw_state.page.goto(url)
        title = await pw_state.page.title()
        return f"✅ Successfully navigated to {url} - Page title: '{title}'"
    except Exception as e:
        return f"❌ Failed to navigate to {url}: {str(e)}"


@tool
async def playwright_click(selector: str, element_description: str = "") -> str:
    """Click an element on the page by CSS selector, XPath, or text.
    
    Args:
        selector: CSS selector, XPath (prefix with //), or text content (prefix with text=)
        element_description: Optional description of the element for clarity
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        if selector.startswith("text="):
            await pw_state.page.click(selector)
        elif selector.startswith("//"):
            await pw_state.page.click(f"xpath={selector}")
        else:
            await pw_state.page.click(selector)
        
        desc = f" ({element_description})" if element_description else ""
        return f"✅ Successfully clicked element: {selector}{desc}"
    except Exception as e:
        return f"❌ Failed to click element {selector}: {str(e)}"


@tool
async def playwright_type(selector: str, text: str, element_description: str = "") -> str:
    """Type text into an input field.
    
    Args:
        selector: CSS selector for the input field
        text: Text to type into the field
        element_description: Optional description of the input field
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.fill(selector, text)
        desc = f" ({element_description})" if element_description else ""
        return f"✅ Successfully typed '{text}' into {selector}{desc}"
    except Exception as e:
        return f"❌ Failed to type into {selector}: {str(e)}"


@tool
async def playwright_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current page.
    
    Args:
        filename: Name of the screenshot file (default: screenshot.png)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        screenshot_path = os.path.join(os.getcwd(), filename)
        await pw_state.page.screenshot(path=screenshot_path)
        return f"✅ Screenshot saved to: {screenshot_path}"
    except Exception as e:
        return f"❌ Failed to take screenshot: {str(e)}"


@tool
async def playwright_wait_for_selector(selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector to wait for
        timeout: Maximum time to wait in milliseconds (default: 5000)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(selector, timeout=timeout)
        return f"✅ Element {selector} appeared on page"
    except Exception as e:
        return f"❌ Element {selector} did not appear within {timeout}ms: {str(e)}"


@tool
async def playwright_wait_for_text(text: str, timeout: int = 5000) -> str:
    """Wait for specific text to appear on the page.
    
    Args:
        text: Text content to wait for
        timeout: Maximum time to wait in milliseconds (default: 5000)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(f"text={text}", timeout=timeout)
        return f"✅ Text '{text}' appeared on page"
    except Exception as e:
        return f"❌ Text '{text}' did not appear within {timeout}ms: {str(e)}"


@tool
async def playwright_get_page_content() -> str:
    """Get the current page content and structure for analysis."""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        title = await pw_state.page.title()
        url = pw_state.page.url
        
        content = await pw_state.page.evaluate("""
            () => {
                const headings = Array.from(document.querySelectorAll('h1, h2, h3')).slice(0, 5).map(h => h.textContent.trim());
                const links = Array.from(document.querySelectorAll('a')).slice(0, 10).map(a => ({text: a.textContent.trim(), href: a.href}));
                const inputs = Array.from(document.querySelectorAll('input, textarea')).slice(0, 5).map(i => ({type: i.type, placeholder: i.placeholder, name: i.name}));
                
                return {
                    headings,
                    links: links.filter(l => l.text),
                    inputs
                };
            }
        """)
        
        result = f"📄 Page Info:\n  Title: {title}\n  URL: {url}\n"
        if content['headings']:
            result += f"  Headings: {', '.join(content['headings'][:3])}\n"
        if content['links']:
            result += f"  Links found: {len(content['links'])}\n"
        if content['inputs']:
            result += f"  Input fields: {len(content['inputs'])}\n"
        
        return result
    except Exception as e:
        return f"❌ Failed to get page content: {str(e)}"


@tool
async def playwright_execute_javascript(script: str) -> str:
    """Execute JavaScript code in the browser context.
    
    Args:
        script: JavaScript code to execute
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        result = await pw_state.page.evaluate(script)
        return f"✅ JavaScript executed. Result: {result}"
    except Exception as e:
        return f"❌ Failed to execute JavaScript: {str(e)}"


@tool
async def playwright_close_browser() -> str:
    """Close the browser and clean up resources."""
    try:
        await pw_state.cleanup()
        return "✅ Browser closed successfully"
    except Exception as e:
        return f"❌ Failed to close browser: {str(e)}"


# Collect all Playwright tools
PLAYWRIGHT_TOOLS = [
    playwright_navigate,
    playwright_click,
    playwright_type,
    playwright_screenshot,
    playwright_wait_for_selector,
    playwright_wait_for_text,
    playwright_get_page_content,
    playwright_execute_javascript,
    playwright_close_browser,
]


def get_playwright_tools() -> List:
    """Get all Playwright automation tools"""
    return PLAYWRIGHT_TOOLS
