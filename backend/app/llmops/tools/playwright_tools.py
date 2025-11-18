"""Playwright automation tools for LLMOps"""

import os
from typing import List, Optional
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


@tool
async def playwright_get_page_metadata(selector: Optional[str] = None) -> str:
    """Get comprehensive metadata of the current page or a specific element.
    
    Args:
        selector: Optional CSS selector, XPath, or text to get element metadata.
                 If not provided, returns page-level metadata only.
    
    Returns page metadata like URL, title, and if selector is provided,
    returns element metadata like id, type, tag, text, name, class, href, input_type, etc.
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        # Collect page-level metadata
        page_meta = {
            "page_url": pw_state.page.url,
            "page_title": await pw_state.page.title(),
        }
        
        # If no selector provided, return only page metadata
        if not selector:
            metadata_str = "📄 Page Metadata:\n"
            metadata_str += f"  • URL: {page_meta['page_url']}\n"
            metadata_str += f"  • Title: {page_meta['page_title']}\n"
            return metadata_str
        
        # Find element by selector
        locator = None
        if selector.startswith("text="):
            locator = pw_state.page.locator(selector)
        elif selector.startswith("//"):
            locator = pw_state.page.locator(f"xpath={selector}")
        else:
            locator = pw_state.page.locator(selector)
        
        # Check if element exists
        count = await locator.count()
        if count == 0:
            return f"❌ No element found with selector: {selector}"
        
        # Get first element
        element = locator.first
        
        # Extract comprehensive element metadata using JavaScript
        element_meta = await element.evaluate("""
            (el) => {
                return {
                    tag: el.tagName.toLowerCase(),
                    id: el.id || null,
                    type: el.type || null,
                    name: el.name || null,
                    className: el.className || null,
                    text: el.textContent?.trim().substring(0, 200) || null,
                    value: el.value || null,
                    href: el.href || null,
                    src: el.src || null,
                    alt: el.alt || null,
                    title: el.title || null,
                    placeholder: el.placeholder || null,
                    ariaLabel: el.ariaLabel || null,
                    role: el.role || null,
                    disabled: el.disabled || null,
                    checked: el.checked || null,
                    selected: el.selected || null,
                    readonly: el.readOnly || null,
                    required: el.required || null,
                    hidden: el.hidden || null,
                    inputType: el.type || null,
                    maxLength: el.maxLength || null,
                    pattern: el.pattern || null,
                    min: el.min || null,
                    max: el.max || null,
                    step: el.step || null,
                    autocomplete: el.autocomplete || null,
                    tabIndex: el.tabIndex || null,
                    dataset: el.dataset ? JSON.stringify(el.dataset) : null,
                    boundingBox: {
                        x: el.getBoundingClientRect().x,
                        y: el.getBoundingClientRect().y,
                        width: el.getBoundingClientRect().width,
                        height: el.getBoundingClientRect().height
                    },
                    isVisible: el.offsetParent !== null,
                    innerHTML: el.innerHTML?.substring(0, 300) || null,
                    outerHTML: el.outerHTML?.substring(0, 300) || null
                };
            }
        """)
        
        # Format metadata for display
        metadata_str = f"📄 Page Metadata:\n"
        metadata_str += f"  • URL: {page_meta['page_url']}\n"
        metadata_str += f"  • Title: {page_meta['page_title']}\n\n"
        
        metadata_str += f"🎯 Element Metadata (Found {count} element(s)):\n"
        metadata_str += f"  • Selector: {selector}\n"
        metadata_str += f"  • Tag: <{element_meta.get('tag')}>\n"
        
        # Add non-null attributes
        if element_meta.get('id'):
            metadata_str += f"  • ID: {element_meta['id']}\n"
        if element_meta.get('type'):
            metadata_str += f"  • Type: {element_meta['type']}\n"
        if element_meta.get('name'):
            metadata_str += f"  • Name: {element_meta['name']}\n"
        if element_meta.get('className'):
            metadata_str += f"  • Class: {element_meta['className']}\n"
        if element_meta.get('text'):
            metadata_str += f"  • Text: {element_meta['text']}\n"
        if element_meta.get('value'):
            metadata_str += f"  • Value: {element_meta['value']}\n"
        if element_meta.get('href'):
            metadata_str += f"  • Href: {element_meta['href']}\n"
        if element_meta.get('src'):
            metadata_str += f"  • Src: {element_meta['src']}\n"
        if element_meta.get('alt'):
            metadata_str += f"  • Alt: {element_meta['alt']}\n"
        if element_meta.get('title'):
            metadata_str += f"  • Title: {element_meta['title']}\n"
        if element_meta.get('placeholder'):
            metadata_str += f"  • Placeholder: {element_meta['placeholder']}\n"
        if element_meta.get('ariaLabel'):
            metadata_str += f"  • Aria-Label: {element_meta['ariaLabel']}\n"
        if element_meta.get('role'):
            metadata_str += f"  • Role: {element_meta['role']}\n"
        if element_meta.get('inputType'):
            metadata_str += f"  • Input Type: {element_meta['inputType']}\n"
        if element_meta.get('maxLength') and element_meta['maxLength'] != -1:
            metadata_str += f"  • Max Length: {element_meta['maxLength']}\n"
        if element_meta.get('pattern'):
            metadata_str += f"  • Pattern: {element_meta['pattern']}\n"
        if element_meta.get('min'):
            metadata_str += f"  • Min: {element_meta['min']}\n"
        if element_meta.get('max'):
            metadata_str += f"  • Max: {element_meta['max']}\n"
        if element_meta.get('step'):
            metadata_str += f"  • Step: {element_meta['step']}\n"
        if element_meta.get('autocomplete'):
            metadata_str += f"  • Autocomplete: {element_meta['autocomplete']}\n"
        if element_meta.get('dataset'):
            metadata_str += f"  • Data Attributes: {element_meta['dataset']}\n"
        
        # Boolean attributes
        metadata_str += f"  • Disabled: {element_meta.get('disabled', False)}\n"
        metadata_str += f"  • Checked: {element_meta.get('checked', False)}\n"
        metadata_str += f"  • Selected: {element_meta.get('selected', False)}\n"
        metadata_str += f"  • Readonly: {element_meta.get('readonly', False)}\n"
        metadata_str += f"  • Required: {element_meta.get('required', False)}\n"
        metadata_str += f"  • Hidden: {element_meta.get('hidden', False)}\n"
        metadata_str += f"  • Visible: {element_meta.get('isVisible', False)}\n"
        
        # Position and size
        bbox = element_meta.get('boundingBox', {})
        metadata_str += f"  • Position: (x={bbox.get('x', 0):.1f}, y={bbox.get('y', 0):.1f})\n"
        metadata_str += f"  • Size: {bbox.get('width', 0):.1f}x{bbox.get('height', 0):.1f}px\n"
        metadata_str += f"  • Tab Index: {element_meta.get('tabIndex', 0)}\n"
        
        if element_meta.get('innerHTML'):
            metadata_str += f"  • Inner HTML: {element_meta['innerHTML'][:100]}...\n"
        
        return metadata_str
        
    except Exception as e:
        return f"❌ Failed to get metadata: {str(e)}"


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
    playwright_get_page_metadata,
    playwright_close_browser,
]


def get_playwright_tools() -> List:
    """Get all Playwright automation tools"""
    return PLAYWRIGHT_TOOLS
