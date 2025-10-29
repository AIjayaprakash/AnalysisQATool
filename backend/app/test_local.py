import asyncio
import time

from selenium_request_types import (
    BrowserType,
    BrowserOptions,
    StartBrowserRequest,
    NavigateRequest,
    ScreenshotRequest,
)

import server


async def run_demo():
    # Start a Chrome browser session (set headless=False to open a visible window)
    start_req = StartBrowserRequest(browser=BrowserType.CHROME, options=BrowserOptions(headless=False))
    print("Starting browser...")
    resp = await server.start_browser(start_req)
    print(resp)

    # Navigate to example.com
    nav_req = NavigateRequest(url="https://example.com")
    print("Navigating to https://example.com...")
    resp = await server.navigate(nav_req)
    print(resp)

    # Wait a short moment to allow page to render
    await server.wait_for_page_load()

    # Take a screenshot and save it to a file so you can open it locally
    ss_path = "screenshot.png"
    ss_req = ScreenshotRequest(output_path=ss_path)
    print(f"Taking screenshot and saving to {ss_path}...")
    resp = await server.take_screenshot(ss_req)
    print(resp)
    # If the screenshot was returned as base64 instead, save it as a fallback
    contents = resp.get("content", [])
    if len(contents) >= 2 and contents[1].get("text"):
        b64 = contents[1]["text"]
        try:
            with open(ss_path, "wb") as f:
                import base64 as _b64

                f.write(_b64.b64decode(b64))
            print(f"Fallback: screenshot written to {ss_path}")
        except Exception as e:
            print(f"Failed to write fallback screenshot: {e}")

    # Close the browser session
    print("Closing session...")
    resp = await server.close_session()
    print(resp)


if __name__ == "__main__":
    asyncio.run(run_demo())
