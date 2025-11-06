"""
Test the Custom OpenAI ReAct Agent with proper @tool decorators and LangGraph
"""

import asyncio
import os
from backend.app.agents.playwright_custom_openai_agent import run_playwright_automation

async def test_custom_react_agent():
    """Test the ReAct agent with custom OpenAI gateway"""
    
    print("🧪 Testing Custom OpenAI ReAct Agent")
    print("=" * 50)
    
    # Set your API key (you need to replace this with your actual key)
    api_key = os.getenv("CUSTOM_OPENAI_KEY", "Your Key Here")
    
    if api_key == "Your Key Here":
        print("❌ Please set CUSTOM_OPENAI_KEY environment variable")
        return
    
    # Test prompt
    test_prompt = "Navigate to https://httpbin.org, take a screenshot, get page content, and close browser"
    
    # Browser config
    browser_config = {
        "headless": False,  # Visible browser
        "browser_type": "chromium"
    }
    
    try:
        print(f"📝 Test prompt: {test_prompt}")
        print(f"🌐 Browser config: {browser_config}")
        print()
        
        # Run the agent
        result = await run_playwright_automation(
            test_prompt=test_prompt,
            max_iterations=5,
            browser_config=browser_config
        )
        
        print("\n📊 Test Results:")
        print(f"  Status: {result['status']}")
        print(f"  Tool calls: {result.get('tool_calls', 0)}")
        print(f"  Total messages: {result.get('total_messages', 0)}")
        
        if result['status'] == 'success':
            print("  ✅ ReAct Agent test successful!")
            print(f"  Final response: {result.get('final_response', 'No response')[:100]}...")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_custom_react_agent())