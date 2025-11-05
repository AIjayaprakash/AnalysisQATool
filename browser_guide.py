"""
Playwright Direct Agent - Browser Support Guide
===============================================

This guide shows how to use different browsers with the Playwright Direct Agent.

Supported Browsers:
- chromium: Google Chrome/Chromium (default)
- edge: Microsoft Edge
- firefox: Mozilla Firefox  
- webkit: Safari WebKit (macOS mainly)

Usage Examples:
"""

import asyncio
import sys
import os

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents'))

from playwright_direct_agent import run_test_with_visible_browser, run_playwright_automation

def test_chromium():
    """Test with Chromium browser"""
    print("🔵 Testing Chromium Browser")
    result = run_test_with_visible_browser(
        "Navigate to https://httpbin.org/html and take a screenshot",
        browser_type="chromium"
    )
    print(f"Result: {result['status']}")

def test_edge():
    """Test with Microsoft Edge browser"""
    print("🟢 Testing Microsoft Edge Browser")  
    result = run_test_with_visible_browser(
        "Navigate to https://httpbin.org/html and take a screenshot",
        browser_type="edge"
    )
    print(f"Result: {result['status']}")

def test_firefox():
    """Test with Firefox browser"""
    print("🟠 Testing Firefox Browser")
    result = run_test_with_visible_browser(
        "Navigate to https://httpbin.org/html and take a screenshot", 
        browser_type="firefox"
    )
    print(f"Result: {result['status']}")

async def test_custom_config():
    """Test with custom browser configuration"""
    print("⚙️ Testing with Custom Configuration")
    
    # Custom Edge configuration
    edge_config = {
        "headless": False,
        "browser_type": "edge"
    }
    
    result = await run_playwright_automation(
        "Navigate to https://www.microsoft.com, take a screenshot, and close browser",
        max_iterations=8,
        browser_config=edge_config
    )
    
    print(f"Edge test result: {result['status']}")

def show_usage_examples():
    """Show code examples for different browser usage"""
    
    print("📚 PLAYWRIGHT BROWSER USAGE EXAMPLES")
    print("====================================")
    print()
    
    print("1. Using Chromium (default):")
    print("   result = run_test_with_visible_browser('your test', browser_type='chromium')")
    print()
    
    print("2. Using Microsoft Edge:")
    print("   result = run_test_with_visible_browser('your test', browser_type='edge')")
    print()
    
    print("3. Using Firefox:")
    print("   result = run_test_with_visible_browser('your test', browser_type='firefox')")
    print()
    
    print("4. Using WebKit:")
    print("   result = run_test_with_visible_browser('your test', browser_type='webkit')")
    print()
    
    print("5. Custom async configuration:")
    print("   config = {'headless': False, 'browser_type': 'edge'}")
    print("   result = await run_playwright_automation('test', browser_config=config)")
    print()
    
    print("6. Available browser types:")
    browsers = [
        {"type": "chromium", "desc": "Google Chrome/Chromium - Fast, reliable"},
        {"type": "edge", "desc": "Microsoft Edge - Windows integrated browser"},
        {"type": "firefox", "desc": "Mozilla Firefox - Privacy focused"},
        {"type": "webkit", "desc": "Safari WebKit - Apple's browser engine"}
    ]
    
    for browser in browsers:
        print(f"   - {browser['type']}: {browser['desc']}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser Support Guide")
    parser.add_argument("--chromium", action="store_true", help="Test Chromium")
    parser.add_argument("--edge", action="store_true", help="Test Edge")
    parser.add_argument("--firefox", action="store_true", help="Test Firefox")
    parser.add_argument("--custom", action="store_true", help="Test custom config")
    parser.add_argument("--examples", action="store_true", help="Show usage examples")
    
    args = parser.parse_args()
    
    if args.chromium:
        test_chromium()
    elif args.edge:
        test_edge()
    elif args.firefox:
        test_firefox()
    elif args.custom:
        asyncio.run(test_custom_config())
    elif args.examples:
        show_usage_examples()
    else:
        show_usage_examples()
        print("\n🎯 To test specific browsers:")
        print("  python browser_guide.py --chromium")
        print("  python browser_guide.py --edge") 
        print("  python browser_guide.py --firefox")
        print("  python browser_guide.py --custom")