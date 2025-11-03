"""
Test script for Playwright Direct Agent
This will demonstrate visible browser automation using LangGraph + Playwright
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents'))

from playwright_direct_agent import run_test_with_visible_browser, run_playwright_automation

async def demo_visible_automation():
    """Demonstrate visible browser automation"""
    
    print("🎭 PLAYWRIGHT DIRECT AUTOMATION DEMO")
    print("====================================")
    print("This demo will show visible browser automation using Playwright + LangGraph")
    print()
    
    # Test cases that will show visible browser windows
    test_cases = [
        {
            "name": "Basic Navigation Test",
            "prompt": "Navigate to https://example.com, take a screenshot, and describe the page content",
            "description": "Opens browser, navigates to a simple page, takes screenshot"
        },
        {
            "name": "Google Search Test", 
            "prompt": "Go to Google.com, search for 'Playwright automation', and take a screenshot of the results",
            "description": "Demonstrates form interaction and search functionality"
        },
        {
            "name": "GitHub Exploration",
            "prompt": "Navigate to GitHub.com, get the page structure, take a screenshot, then close the browser",
            "description": "Shows page analysis and proper cleanup"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 Test {i}: {test_case['name']}")
        print(f"📝 Description: {test_case['description']}")
        print(f"🎯 Prompt: {test_case['prompt']}")
        print('='*60)
        
        # Run the test with visible browser
        print("🚀 Starting test... You should see a browser window open!")
        
        try:
            result = run_test_with_visible_browser(
                prompt=test_case['prompt'],
                max_iterations=8,
                headless=False  # Ensure visible browser
            )
            
            print(f"\n📊 Test Results:")
            print(f"  ✅ Status: {result['status']}")
            print(f"  📈 Steps executed: {result.get('steps_executed', 0)}")
            
            if result.get('errors'):
                print(f"  ⚠️ Errors: {result['errors']}")
            
            if result.get('results'):
                print(f"  🔧 Tools used: {[r.get('tool_names', []) for r in result['results']]}")
            
        except Exception as e:
            print(f"  ❌ Test failed: {str(e)}")
        
        # Pause between tests
        if i < len(test_cases):
            print(f"\n⏸️  Pausing 5 seconds before next test...")
            await asyncio.sleep(5)
    
    print(f"\n🎉 Demo completed!")
    print("💡 If you saw browser windows opening and automation happening, the setup is working!")

def run_single_test():
    """Run a single quick test"""
    print("🚀 Running single test with visible browser...")
    
    result = run_test_with_visible_browser(
        "Navigate to https://httpbin.org/html and take a screenshot",
        max_iterations=5,
        headless=False
    )
    
    print(f"Result: {result['status']}")
    print(f"Steps: {result.get('steps_executed', 0)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Playwright Direct Agent Demo")
    parser.add_argument("--single", action="store_true", help="Run single quick test")
    parser.add_argument("--full", action="store_true", help="Run full demo")
    
    args = parser.parse_args()
    
    if args.single:
        run_single_test()
    elif args.full:
        asyncio.run(demo_visible_automation())
    else:
        print("🎭 Playwright Direct Agent Demo")
        print("Usage:")
        print("  python test_playwright_direct.py --single   # Quick test")
        print("  python test_playwright_direct.py --full     # Full demo")
        print()
        print("This will demonstrate visible browser automation using Playwright + LangGraph")
        
        # Run single test by default
        print("Running single test...")
        run_single_test()