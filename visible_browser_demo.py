"""
Simple Demo - Playwright Direct Agent with Visible Browser
This will open a browser window and perform automation that you can see happening.
"""

import asyncio
import sys
import os

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents'))

from playwright_direct_agent import run_playwright_automation

async def visible_browser_demo():
    """Demo with visible browser - you will see the automation happening!"""
    
    print("🎭 VISIBLE BROWSER AUTOMATION DEMO")
    print("==================================")
    print("🚀 A browser window will open and you can watch the automation!")
    print("📺 Watch your screen - the browser will be visible throughout")
    print()
    
    # Simple test that shows clear visible actions
    test_prompt = """
    Please do the following automation steps with a visible browser:
    1. Navigate to https://example.com
    2. Take a screenshot of the page
    3. Get the page content to analyze what's on the page
    4. Wait 3 seconds so we can see the browser
    5. Navigate to https://httpbin.org/html (a different page)
    6. Take another screenshot
    7. Close the browser when done
    
    Make sure each step is clearly visible and take your time between actions.
    """
    
    print("🎯 Test: Multi-step visible browser automation")
    print("📋 Steps: Navigate → Screenshot → Content → Wait → New page → Screenshot → Close")
    print("👀 WATCH YOUR SCREEN - Browser window will open!")
    print()
    
    # Configure for maximum visibility
    browser_config = {
        "headless": False,      # Visible browser
        "browser_type": "chromium",
        "slow_mo": 1000,       # Slow down actions for visibility
    }
    
    try:
        result = await run_playwright_automation(
            test_prompt=test_prompt,
            max_iterations=15,
            browser_config=browser_config
        )
        
        print(f"\n🎉 DEMO COMPLETED!")
        print(f"📊 Results:")
        print(f"  ✅ Status: {result['status']}")
        print(f"  📈 Steps executed: {result.get('steps_executed', 0)}")
        print(f"  🔧 Tools used in steps: {len(result.get('results', []))}")
        
        if result.get('errors'):
            print(f"  ⚠️ Errors: {result['errors']}")
        
        print(f"\n💡 Did you see the browser window open and automation happen?")
        print(f"📁 Screenshots should be saved in the current directory")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("💡 Make sure you have the required API keys set up")

if __name__ == "__main__":
    print("Starting visible browser demo in 3 seconds...")
    print("Get ready to watch your screen!")
    
    import time
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    print("🚀 GO!")
    asyncio.run(visible_browser_demo())