#!/usr/bin/env python3
"""
Example usage of Playwright + Custom OpenAI Gateway Agent

This demonstrates how to use your specific OpenAI client configuration 
with the LangGraph Playwright agent.
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Import the custom OpenAI gateway version
from playwright_custom_openai_agent import run_test_with_custom_openai

def example_with_your_openai_config():
    """Example using your exact OpenAI configuration"""
    print("🔥 Custom OpenAI Gateway Example")
    print("=" * 50)
    
    # Your OpenAI configuration
    api_key = "Your Key Here"  # Replace with your actual key
    model = "gpt-4o"
    
    # Note: The gateway URL is automatically constructed as:
    # f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
    
    print(f"Using model: {model}")
    print(f"Gateway: https://gateway.ai-npe.humana.com/openai/deployments/{model}")
    print()
    
    # Test with your configuration
    result = run_test_with_custom_openai(
        prompt="""
        Please perform a web automation test:
        
        1. Navigate to https://httpbin.org/forms/post
        2. Take a screenshot to document the initial page
        3. Get the page content to analyze the form structure
        4. Fill in the form fields:
           - Customer name: "Test User"
           - Telephone: "555-1234"
           - Email: "test@example.com"
        5. Take another screenshot of the filled form
        6. Close the browser when done
        """,
        max_iterations=8,
        headless=False,  # Visible browser so you can see it working
        browser_type="chromium",
        api_key=api_key,  # Your actual API key
        model=model
    )
    
    print(f"\n📊 Results:")
    print(f"  Status: {result['status']}")
    print(f"  Steps executed: {result['steps_executed']}")
    print(f"  Total messages: {len(result.get('messages', []))}")
    
    if result.get('errors'):
        print(f"  ⚠️ Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    - {error}")
    else:
        print("  ✅ No errors!")
    
    return result

def test_different_browsers():
    """Test with different browsers using your OpenAI config"""
    print("\n🔥 Multi-Browser Test with Custom OpenAI")
    print("=" * 50)
    
    api_key = "Your Key Here"  # Replace with your actual key
    model = "gpt-4o"
    
    browsers = ["chromium", "edge", "firefox"]
    
    for browser in browsers:
        print(f"\n  Testing with {browser.upper()}...")
        
        result = run_test_with_custom_openai(
            prompt=f"Navigate to https://example.com, take screenshot, get page content, close browser",
            max_iterations=4,
            headless=False,
            browser_type=browser,
            api_key=api_key,
            model=model
        )
        
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"  {browser}: {status} {result['status']} ({result['steps_executed']} steps)")

def main():
    """Main example runner"""
    print("🎭 PLAYWRIGHT + CUSTOM OPENAI GATEWAY EXAMPLES")
    print("=" * 60)
    print("This uses your exact OpenAI client configuration:")
    print("  - Custom gateway URL with deployment path")
    print("  - Special headers: api-key and ai-gateway-version")
    print("  - Your specific model and authentication")
    print()
    
    # Replace this with your actual API key
    api_key = os.getenv("CUSTOM_OPENAI_KEY", "Your Key Here")
    
    if api_key == "Your Key Here":
        print("❌ Please set your actual API key!")
        print("   Option 1: Set CUSTOM_OPENAI_KEY environment variable")
        print("   Option 2: Replace 'Your Key Here' in the code with your actual key")
        print()
        print("   Your configuration will be:")
        print("   - API Key: [Your actual key]")
        print("   - Model: gpt-4o")
        print("   - Gateway: https://gateway.ai-npe.humana.com/openai/deployments/gpt-4o")
        print("   - Headers: api-key + ai-gateway-version: v2")
        return
    
    print("✅ API key configured")
    print("\n🚀 Running examples...\n")
    
    try:
        # Run the main example
        result = example_with_your_openai_config()
        
        if result['status'] == 'success':
            print("\n🎉 SUCCESS! Your custom OpenAI configuration works with LangGraph!")
            print("   ✅ No model_dump errors")
            print("   ✅ Custom gateway integration working")
            print("   ✅ Playwright automation successful")
            
            # Run multi-browser test if main test worked
            test_different_browsers()
        else:
            print(f"\n❌ Main test failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        
        if 'model_dump' in str(e):
            print("   This appears to be a model_dump serialization error")
            print("   The fix may need additional adjustments for your environment")
        elif 'api' in str(e).lower() or 'key' in str(e).lower():
            print("   This appears to be an API authentication error")
            print("   Please check your API key and gateway configuration")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()