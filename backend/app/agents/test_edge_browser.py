"""
Test script to demonstrate Microsoft Edge browser support in Playwright Direct Agent
"""

import asyncio
import sys
import os

# Add backend path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents'))

from playwright_direct_agent import run_playwright_automation

async def test_edge_browser():
    """Test automation with Microsoft Edge browser"""
    
    print("🌐 MICROSOFT EDGE BROWSER TEST")
    print("==============================")
    print("🎯 Testing Playwright automation with Microsoft Edge browser")
    print("📺 Edge browser window will be visible during automation")
    print()
    
    # Test prompt for Edge browser
    test_prompt = """
    Please perform the following steps with Microsoft Edge browser:
    1. Navigate to https://www.microsoft.com
    2. Take a screenshot of the Microsoft homepage
    3. Get the page content to analyze the page structure
    4. Wait 2 seconds to show the browser
    5. Close the browser when done
    
    Make sure to use Microsoft Edge browser for this test.
    """
    
    # Configure for Edge browser
    edge_config = {
        "headless": False,         # Visible browser
        "browser_type": "edge"     # Microsoft Edge
    }
    
    print(f"🎯 Test Prompt: Navigate to Microsoft.com with Edge browser")
    print(f"🔧 Browser Config: {edge_config}")
    print("🚀 Starting Edge browser automation...")
    print()
    
    try:
        result = await run_playwright_automation(
            test_prompt=test_prompt,
            max_iterations=10,
            browser_config=edge_config
        )
        
        print(f"\n🎉 EDGE BROWSER TEST COMPLETED!")
        print(f"📊 Results:")
        print(f"  ✅ Status: {result['status']}")
        print(f"  🌐 Browser: Microsoft Edge")
        print(f"  📈 Steps executed: {result.get('steps_executed', 0)}")
        print(f"  ⚙️ Browser config: {result.get('browser_config', {})}")
        
        if result.get('errors'):
            print(f"  ⚠️ Errors: {result['errors']}")
        
        if result.get('results'):
            print(f"  🔧 Tool execution summary:")
            for i, step_result in enumerate(result['results'], 1):
                tools_used = ', '.join(step_result.get('tool_names', []))
                print(f"    Step {i}: {tools_used}")
        
        print(f"\n💡 Microsoft Edge browser automation completed successfully!")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ Edge browser test failed: {str(e)}")
        print("💡 Make sure Microsoft Edge is installed on your system")
        print("💡 Also ensure GROQ_API_KEY is set in your environment")
        return False

async def test_all_browsers():
    """Test automation with all supported browsers"""
    
    print("🎭 ALL BROWSERS TEST")
    print("===================")
    print("Testing Playwright automation with all supported browsers")
    print()
    
    browsers = [
        {"type": "chromium", "name": "Google Chrome/Chromium"},
        {"type": "edge", "name": "Microsoft Edge"},
        {"type": "firefox", "name": "Mozilla Firefox"},
        {"type": "webkit", "name": "Safari WebKit"}
    ]
    
    test_prompt = "Navigate to https://httpbin.org/html and take a screenshot"
    
    results = {}
    
    for browser in browsers:
        print(f"\n🔧 Testing {browser['name']}...")
        
        browser_config = {
            "headless": False,
            "browser_type": browser['type']
        }
        
        try:
            result = await run_playwright_automation(
                test_prompt=test_prompt,
                max_iterations=5,
                browser_config=browser_config
            )
            
            results[browser['type']] = result['status'] == 'success'
            print(f"  ✅ {browser['name']}: {'SUCCESS' if results[browser['type']] else 'FAILED'}")
            
        except Exception as e:
            results[browser['type']] = False
            print(f"  ❌ {browser['name']}: FAILED - {str(e)}")
        
        # Wait between tests
        await asyncio.sleep(2)
    
    print(f"\n📊 FINAL RESULTS:")
    for browser in browsers:
        status = "✅ SUCCESS" if results.get(browser['type'], False) else "❌ FAILED"
        print(f"  {browser['name']}: {status}")
    
    successful_browsers = sum(results.values())
    print(f"\n🎯 {successful_browsers}/{len(browsers)} browsers working successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Playwright with different browsers")
    parser.add_argument("--edge", action="store_true", help="Test Microsoft Edge browser only")
    parser.add_argument("--all", action="store_true", help="Test all supported browsers")
    
    args = parser.parse_args()
    
    if args.edge:
        print("🌐 Running Microsoft Edge browser test...")
        success = asyncio.run(test_edge_browser())
        if success:
            print("\n🎉 Edge browser test completed successfully!")
        else:
            print("\n❌ Edge browser test failed")
    elif args.all:
        print("🎭 Running all browsers test...")
        asyncio.run(test_all_browsers())
    else:
        print("🎭 Browser Support Test")
        print("Usage:")
        print("  python test_edge_browser.py --edge    # Test Microsoft Edge only")
        print("  python test_edge_browser.py --all     # Test all browsers")
        print()
        print("Supported browsers:")
        print("  - Chromium (Google Chrome)")
        print("  - Microsoft Edge")
        print("  - Mozilla Firefox") 
        print("  - WebKit (Safari)")
        
        # Run Edge test by default
        print("\nRunning Microsoft Edge test by default...")
        success = asyncio.run(test_edge_browser())