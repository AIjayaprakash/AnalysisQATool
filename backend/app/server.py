import base64
from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
from state import state
from utils import get_driver, get_locator
from selenium_request_types import (
    BrowserType,
    BrowserOptions,
    StartBrowserRequest,
    NavigateRequest,
    ElementLocator,
    SendKeysRequest, KeyPressRequest, LocalStorageRequest, ScreenshotRequest, ScrollRequest, IFrameRequest,
)

mcp = FastMCP("MCP-Selenium")

# @mcp.info()
# def info():
#     return {
#         "name": "selenium-fast-mcp-node",
#         "version": "1.0.0",
#         "description": "A simple Selenium node using Fast MCP",
#         "capabilities": ["chrome", "firefox"]
#     }
#
# @mcp.status()
# def status():
#     return {
#         "available": True,
#         "message": "Node is healthy and ready."
#     }

@mcp.tool("start_browser", "Launches browser")
async def start_browser(request: StartBrowserRequest):
    try:
        options = request.options or BrowserOptions()

        if request.browser == BrowserType.CHROME:
            chrome_options = ChromeOptions()
            if options.headless:
                chrome_options.add_argument("--headless=new")
            if options.arguments:
                for arg in options.arguments:
                    chrome_options.add_argument(arg)
            # reduce noisy chrome logs and disable background/networking features that
            # can emit DEPRECATED_ENDPOINT / GCM related errors in Chrome/Chromium
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--log-level=3")
            try:
                # Use webdriver-manager to ensure chromedriver is available
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                # fallback to default constructor
                driver = webdriver.Chrome(options=chrome_options)

        elif request.browser == BrowserType.FIREFOX:
            firefox_options = FirefoxOptions()
            if options.headless:
                firefox_options.add_argument("--headless")
            if options.arguments:
                for arg in options.arguments:
                    firefox_options.add_argument(arg)
            try:
                gecko_path = GeckoDriverManager().install()
                driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)
            except Exception:
                driver = webdriver.Firefox(options=firefox_options)
        else:
            return {"content": [{"type": "text", "text": "Unsupported browser type"}]}

        session_id = f"{request.browser}_{id(driver)}"
        state.drivers[session_id] = driver
        state.current_session = session_id

        return {"content": [{"type": "text", "text": f"Browser started with session_id: {session_id}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error starting browser: {str(e)}"}]}

@mcp.tool("navigate", "Navigates to a URL")
async def navigate(request: NavigateRequest):
    try:
        driver = get_driver()
        driver.get(request.url)
        return {"content": [{"type": "text", "text": f"Navigated to {request.url}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error navigating: {str(e)}"}]}

@mcp.tool("find_element", "Finds an element")
async def find_element(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        print("element found in find element")
        return {"content": [{"type": "text", "text": "Element found"}]}
    except Exception as e:
        print("element not found")
        return {"content": [{"type": "text", "text": f"Error finding element: {str(e)}"}]}

@mcp.tool("click_element", "Clicks an element")
async def click_element(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.element_to_be_clickable((by_strategy, selector))
        )
        element.click()
        return {"content": [{"type": "text", "text": "Element clicked"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error clicking element: {str(e)}"}]}

@mcp.tool("send_keys", "Sends keys to an element")
async def send_keys(request: SendKeysRequest):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.element_to_be_clickable((by_strategy, selector))
        )
        element.clear()
        element.send_keys(request.text)
        return {"content": [{"type": "text", "text": f'Text "{request.text}" entered into element'}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error entering text: {str(e)}"}]}

@mcp.tool("get_element_text", "Gets the text() of an element")
async def get_element_text(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        return {"content": [{"type": "text", "text": element.text}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error getting element text: {str(e)}"}]}

@mcp.tool("get_page_content", "Gets the entire page content (HTML source)")
async def get_page_content():
    try:
        driver = get_driver()
        html = driver.page_source
        return {"content": [{"type": "text", "text": html[:10000]}]}  # return first 10,000 chars for safety
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error getting page content: {str(e)}"}]}


@mcp.tool("wait_for_page_load", "waits for page to fully load")
async def wait_for_page_load():
    try:
        driver = get_driver()
        # Wait for document.readyState to be complete
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Wait for page loaded successfully")
        return {
            "content": [{"type": "text", "text": "Page loaded successfully"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error waiting for page load: {str(e)}"}]
        }


@mcp.tool("get_title", "gets the title of the current page")
async def get_title():
    try:
        driver = get_driver()
        title = driver.title
        return {
            "content": [{"type": "text", "text": f"Page title: {title}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting page title: {str(e)}"}]
        }


@mcp.tool("get_current_url", "gets the current URL of the page")
async def get_current_url():
    try:
        driver = get_driver()
        url = driver.current_url
        return {
            "content": [{"type": "text", "text": f"Current URL: {url}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting current URL: {str(e)}"}]
        }
@mcp.tool("clear_field", "clears a text field, handling both basic and sophisticated clearing")
async def clear_field(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.element_to_be_clickable((by_strategy, selector))
        )
        # First try simple clear
        element.clear()

        # Then try more sophisticated clearing technique
        element.click()
        if platform.system() == 'Darwin':  # macOS
            ctrl_key = Keys.COMMAND
        else:  # Windows/Linux
            ctrl_key = Keys.CONTROL

        actions = ActionChains(driver)
        actions.key_down(ctrl_key).send_keys('A').key_up(ctrl_key).send_keys(Keys.DELETE).perform()

        return {
            "content": [{"type": "text", "text": "Field cleared"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error clearing field: {str(e)}"}]
        }


@mcp.tool("get_element_text", "gets the text() of an element")
async def get_element_text(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        text = element.text
        # If no text directly available, try to get innerText
        if len(text) == 0:
            text = element.get_attribute("innerText")
        if text:
            text = text.strip()
        return {
            "content": [{"type": "text", "text": text}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting element text: {str(e)}"}]
        }


@mcp.tool("get_element_attribute", "gets an attribute value from an element")
async def get_element_attribute(request: ElementLocator, attribute: str):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        attr_value = element.get_attribute(attribute)
        return {
            "content": [{"type": "text", "text": f"Attribute value: {attr_value}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting element attribute: {str(e)}"}]
        }


@mcp.tool("is_element_present", "checks if an element is present in the DOM")
async def is_element_present(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        try:
            driver.find_element(by_strategy, selector)
            is_present = True
        except NoSuchElementException:
            is_present = False

        return {
            "content": [{"type": "text", "text": f"Element is present: {is_present}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error checking element presence: {str(e)}"}]
        }


@mcp.tool("is_element_displayed", "checks if an element is visible on the page")
async def is_element_displayed(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        try:
            element = driver.find_element(by_strategy, selector)
            is_displayed = element.is_displayed()
        except NoSuchElementException:
            is_displayed = False

        return {
            "content": [{"type": "text", "text": f"Element is displayed: {is_displayed}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error checking element visibility: {str(e)}"}]
        }


@mcp.tool("is_element_selected", "checks if an element (checkbox, radio) is selected")
async def is_element_selected(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        is_selected = element.is_selected()

        return {
            "content": [{"type": "text", "text": f"Element is selected: {is_selected}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error checking element selection: {str(e)}"}]
        }


@mcp.tool("get_element_list", "gets a list of elements matching the locator")
async def get_element_list(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        elements = driver.find_elements(by_strategy, selector)
        count = len(elements)

        return {
            "content": [{"type": "text", "text": f"Found {count} matching elements"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error finding elements: {str(e)}"}]
        }
@mcp.tool("double_click", "performs a double click on an element")
async def double_click(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        actions = ActionChains(driver)
        actions.double_click(element).perform()
        return {
            "content": [{"type": "text", "text": "Double click performed"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error performing double click: {str(e)}"}]
        }


@mcp.tool("right_click", "performs a right click (context click) on an element")
async def right_click(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )
        actions = ActionChains(driver)
        actions.context_click(element).perform()
        return {
            "content": [{"type": "text", "text": "Right click performed"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error performing right click: {str(e)}"}]
        }


@mcp.tool("press_key", "simulates pressing a keyboard key")
async def press_key(request: KeyPressRequest):
    try:
        driver = get_driver()
        actions = ActionChains(driver)

        # Handle special keys
        key_attr = getattr(Keys, request.key.upper(), None)
        key_to_send = key_attr if key_attr else request.key

        actions.key_down(key_to_send).key_up(key_to_send).perform()
        return {
            "content": [{"type": "text", "text": f"Key '{request.key}' pressed"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error pressing key: {str(e)}"}]
        }
@mcp.tool("scroll_page", "scrolls the page in a specified direction")
async def scroll_page(request: ScrollRequest):
    try:
        driver = get_driver()
        pixels = request.pixels or (800 if request.direction == "down" else 1000)

        if request.direction == "up":
            driver.execute_script(f"window.scrollBy(0, -{pixels});")
        else:  # down
            driver.execute_script(f"window.scrollBy(0, {pixels});")

        return {
            "content": [{"type": "text", "text": f"Scrolled {request.direction} by {pixels} pixels"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error scrolling page: {str(e)}"}]
        }


@mcp.tool("scroll_to_element", "scrolls the page until an element is in view")
async def scroll_to_element(request: ElementLocator):
    try:
        driver = get_driver()
        by_strategy, selector = get_locator(request.by, request.value)
        element = WebDriverWait(driver, request.timeout / 1000).until(
            EC.presence_of_element_located((by_strategy, selector))
        )

        # Scroll element into view smoothly
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

        return {
            "content": [{"type": "text", "text": "Scrolled to element"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error scrolling to element: {str(e)}"}]
        }


# Window handling tools
@mcp.tool("get_window_handles", "gets all window handles")
async def get_window_handles():
    try:
        driver = get_driver()
        handles = driver.window_handles
        current = driver.current_window_handle

        return {
            "content": [{"type": "text", "text": f"Current window: {current}\nAll windows: {handles}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting window handles: {str(e)}"}]
        }


@mcp.tool("switch_to_window", "switches to a specific window by handle")
async def switch_to_window(window_id: str):
    try:
        driver = get_driver()
        driver.switch_to.window(window_id)
        return {
            "content": [{"type": "text", "text": f"Switched to window: {window_id}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error switching to window: {str(e)}"}]
        }


@mcp.tool("switch_to_new_window", "switches to a new window that is not the parent")
async def switch_to_new_window(parent_id: str):
    try:
        driver = get_driver()
        all_handles = driver.window_handles
        current_handle = None

        for handle in all_handles:
            if handle != parent_id:
                driver.switch_to.window(handle)
                current_handle = handle
                break

        if current_handle:
            return {
                "content": [{"type": "text", "text": f"Switched to new window: {current_handle}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": "No new window found to switch to"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error switching to new window: {str(e)}"}]
        }


# iFrame handling tools
@mcp.tool("switch_to_iframe", "switches to an iframe")
async def switch_to_iframe(request: IFrameRequest):
    try:
        driver = get_driver()

        if request.type == "index" and request.value is not None:
            driver.switch_to.frame(int(request.value))
        elif request.type == "id" and request.value is not None:
            driver.switch_to.frame(request.value)
        elif request.type == "name" and request.value is not None:
            driver.switch_to.frame(request.value)
        elif request.type == "element" and request.element_by and request.element_value:
            by_type, selector = get_locator(request.element_by, request.element_value)
            iframe_element = driver.find_element(by_type, selector)
            driver.switch_to.frame(iframe_element)
        else:
            return {
                "content": [{"type": "text", "text": "Invalid iframe request parameters"}]
            }

        return {
            "content": [{"type": "text", "text": "Switched to iframe"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error switching to iframe: {str(e)}"}]
        }


@mcp.tool("switch_to_default_content", "switches back to the main document from an iframe")
async def switch_to_default_content():
    try:
        driver = get_driver()
        driver.switch_to.default_content()
        return {
            "content": [{"type": "text", "text": "Switched back to main document"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error switching to main document: {str(e)}"}]
        }


@mcp.tool("refresh_page", "refreshes the current page")
async def refresh_page():
    try:
        driver = get_driver()
        driver.refresh()
        # Wait for page to load after refresh
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return {
            "content": [{"type": "text", "text": "Page refreshed"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error refreshing page: {str(e)}"}]
        }


# Local storage tools
@mcp.tool("manage_local_storage", "manages browser local storage")
async def manage_local_storage(request: LocalStorageRequest):
    try:
        driver = get_driver()

        if request.operation == "get":
            value = driver.execute_script(f"return window.localStorage.getItem('{request.key}');")
            return {
                "content": [{"type": "text", "text": f"Local storage value for '{request.key}': {value}"}]
            }
        elif request.operation == "set" and request.value is not None:
            driver.execute_script(f"window.localStorage.setItem('{request.key}', '{request.value}');")
            return {
                "content": [{"type": "text", "text": f"Local storage key '{request.key}' set to '{request.value}'"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error refreshing page: {str(e)}"}]

        }


@mcp.tool("close_session", "closes the current browser session")
async def close_session():
    try:
        driver = get_driver()
        session_id = state.current_session
        driver.quit()
        del state.drivers[state.current_session]
        state.current_session = None
        return {
            "content": [{"type": "text", "text": f"Browser session {session_id} closed"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error closing session: {str(e)}"}]
        }
@mcp.tool("take_screenshot", "captures a screenshot of the current page")
async def take_screenshot(request: ScreenshotRequest):
    try:
        driver = get_driver()
        screenshot = driver.get_screenshot_as_base64()

        if request.output_path:
            with open(request.output_path, "wb") as file:
                file.write(base64.b64decode(screenshot))
            return {
                "content": [{"type": "text", "text": f"Screenshot saved to {request.output_path}"}]
            }
        else:
            return {
                "content": [
                    {"type": "text", "text": "Screenshot captured as base64:"},
                    {"type": "text", "text": screenshot}
                ]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error taking screenshot: {str(e)}"}]
        }



if __name__== "__main__":
    mcp.run()
