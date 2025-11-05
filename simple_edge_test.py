"""
Simple Edge browser test for Playwright
"""
import asyncio
from playwright.async_api import async_playwright

async def test_edge_simple():
    """Simple test to verify Edge browser works"""
    print("🌐 Testing Microsoft Edge browser...")
    
    try:
        async with async_playwright() as p:
            # Launch Edge browser
            browser = await p.chromium.launch(
                headless=False,
                channel="msedge"
            )
            
            page = await browser.new_page()
            print("✅ Microsoft Edge browser launched successfully!")
            
            # Navigate to a simple page
            await page.goto("https://example.com")
            title = await page.title()
            print(f"✅ Navigated to page: {title}")
            
            # Take screenshot
            await page.screenshot(path="edge_test.png")
            print("✅ Screenshot saved: edge_test.png")
            
            # Wait briefly to see the browser
            await asyncio.sleep(3)
            
            # Close browser
            await browser.close()
            print("✅ Browser closed successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Edge browser test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Simple Microsoft Edge Browser Test")
    print("=====================================")
    
    success = asyncio.run(test_edge_simple())
    
    if success:
        print("\n🎉 Microsoft Edge browser is working correctly!")
        print("Your Playwright agent now supports Edge browser!")
    else:
        print("\n❌ Microsoft Edge browser test failed")
        print("Make sure Microsoft Edge is installed on your system")