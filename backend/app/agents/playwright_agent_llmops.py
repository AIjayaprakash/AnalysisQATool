"""
Playwright Automation Agent - Using LLMOps Structure
This is a refactored version that uses the organized LLMOps package.
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Import from LLMOps package
from llmops import PlaywrightAgent

print("[OK] Playwright Agent - Using LLMOps Structure")
print("  All functionality organized in llmops/ package")


def run_playwright_test(
    prompt: str,
    max_iterations: int = 10,
    headless: bool = False,
    browser_type: str = "chromium",
    api_key: str = None,
    model: str = "gpt-4o"
):
    """
    Run Playwright automation test using LLMOps structure
    
    Args:
        prompt: Test description in natural language
        max_iterations: Maximum iterations for the agent
        headless: Whether to run browser in headless mode
        browser_type: Browser type (chromium, firefox, webkit, edge)
        api_key: Custom OpenAI API key (uses env variable if None)
        model: Model to use (default: gpt-4o)
    
    Returns:
        Test results dictionary
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv("CUSTOM_OPENAI_KEY", "placeholder-key")
    
    # Initialize Playwright Agent
    agent = PlaywrightAgent(
        api_key=api_key,
        model=model
    )
    
    # Run the test
    result = agent.run_sync(
        test_prompt=prompt,
        max_iterations=max_iterations,
        headless=headless,
        browser_type=browser_type
    )
    
    return result


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎭 PLAYWRIGHT AUTOMATION AGENT - LLMOps Structure")
    print("=" * 70)
    print("This version uses the organized LLMOps package")
    print()
    
    # Check API key
    CUSTOM_API_KEY = os.getenv("CUSTOM_OPENAI_KEY")
    
    if not CUSTOM_API_KEY or CUSTOM_API_KEY == "Your Key Here":
        print("❌ Please set CUSTOM_OPENAI_KEY environment variable")
        print("   Set it in your .env file or environment")
    else:
        print("✓ API key found in environment")
        
        # Run test
        test_prompt = "Navigate to https://httpbin.org, take a screenshot, get page content, and close browser"
        
        print(f"\n📝 Test Prompt: {test_prompt}")
        print(f"🔧 Configuration: headless=False, browser=chromium, max_iterations=10")
        print()
        
        result = run_playwright_test(
            prompt=test_prompt,
            max_iterations=10,
            headless=False,
            browser_type="chromium"
        )
        
        print("\n" + "=" * 70)
        print("📊 Test Results:")
        print("=" * 70)
        print(f"Status: {result['status']}")
        print(f"Tool Calls: {result.get('tool_calls', 0)}")
        print(f"Total Messages: {result.get('total_messages', 0)}")
        
        if result['status'] == 'error':
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n✅ Test completed successfully!")
            print(f"\nFinal Response Preview:")
            final_response = result.get('final_response', '')
            print(f"  {final_response[:200]}...")
        
        print("\n" + "=" * 70)
