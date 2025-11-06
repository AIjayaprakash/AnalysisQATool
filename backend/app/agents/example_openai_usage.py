#!/usr/bin/env python3
"""
Example usage of Playwright + OpenAI Agent (model_dump fix included)

This demonstrates how to use the OpenAI version in your environment 
without encountering 'str' object has no attribute 'model_dump' errors.
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Import the OpenAI version of the agent
from playwright_openai_agent import run_test_with_openai

def example_basic_test():
    """Basic example - navigate and screenshot"""
    print("🔥 Example 1: Basic Navigation Test")
    
    result = run_test_with_openai(
        prompt="Navigate to https://example.com and take a screenshot",
        max_iterations=3,
        headless=False,  # Visible browser
        browser_type="chromium"
    )
    
    print(f"Result: {result['status']}")
    print(f"Steps: {result['steps_executed']}")
    return result

def example_form_interaction():
    """Advanced example - form interaction"""
    print("\n🔥 Example 2: Form Interaction Test")
    
    result = run_test_with_openai(
        prompt="""
        Go to https://httpbin.org/forms/post and:
        1. Fill in the customer name field with 'Test User'
        2. Fill in the telephone field with '555-1234'  
        3. Fill in the email field with 'test@example.com'
        4. Take a screenshot of the filled form
        5. Click the submit button
        6. Take a screenshot of the result
        """,
        max_iterations=8,
        headless=False,
        browser_type="chromium"
    )
    
    print(f"Result: {result['status']}")
    print(f"Steps: {result['steps_executed']}")
    return result

def example_multi_browser():
    """Example with different browsers"""
    print("\n🔥 Example 3: Multi-Browser Test")
    
    browsers = ["chromium", "firefox", "edge"]
    
    for browser in browsers:
        print(f"\n  Testing with {browser.upper()}...")
        
        result = run_test_with_openai(
            prompt=f"Navigate to https://httpbin.org, take screenshot, close browser",
            max_iterations=3,
            headless=False,
            browser_type=browser
        )
        
        print(f"  {browser}: {result['status']} ({result['steps_executed']} steps)")

def main():
    """Main example runner"""
    print("🎭 PLAYWRIGHT + OPENAI AGENT EXAMPLES")
    print("====================================")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Get your key from: https://platform.openai.com/api-keys")
        return
    
    print("✅ OpenAI API key found")
    print("\n🚀 Running examples...\n")
    
    try:
        # Run examples
        example_basic_test()
        example_form_interaction() 
        example_multi_browser()
        
        print("\n🎉 All examples completed successfully!")
        print("   ✅ No model_dump errors encountered")
        print("   ✅ OpenAI + LangGraph + Pydantic working together")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        
        if 'model_dump' in str(e):
            print("   This appears to be a model_dump serialization error")
            print("   The fix may need additional adjustments for your environment")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()