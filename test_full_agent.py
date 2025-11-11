"""
Test the complete agent with fixed tool execution
"""

import asyncio
import os
from backend.app.agents.playwright_custom_openai_agent import run_playwright_automation

async def test_full_agent():
    """Test the complete agent workflow"""
    
    print("🧪 Testing Complete Agent with Fixed Tool Execution")
    print("=" * 60)
    
    # Test with a simple automation task
    test_prompt = "Navigate to https://httpbin.org and take a screenshot"
    
    browser_config = {
        "headless": False,  # Visible browser for testing
        "browser_type": "chromium"
    }
    
    try:
        print(f"📝 Test prompt: {test_prompt}")
        print(f"🌐 Browser config: {browser_config}")
        print()
        
        # Run the agent
        result = await run_playwright_automation(
            test_prompt=test_prompt,
            max_iterations=3,
            browser_config=browser_config
        )
        
        print("\n📊 Agent Test Results:")
        print(f"  Status: {result['status']}")
        
        if result['status'] == 'success':
            print(f"  Tool calls: {result.get('tool_calls', 0)}")
            print(f"  Total messages: {result.get('total_messages', 0)}")
            print("  ✅ Agent test successful!")
            
            # Show last few messages
            messages = result.get('messages', [])
            if messages:
                print(f"\n📝 Final response preview:")
                final_content = result.get('final_response', 'No response')
                print(f"  {final_content[:200]}..." if len(final_content) > 200 else f"  {final_content}")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
            
        return result['status'] == 'success'
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

if __name__ == "__main__":
    # Note: This test requires a valid API key to work fully
    # But it will test the tool execution mechanism
    success = asyncio.run(test_full_agent())
    print(f"\n🎯 Overall test result: {'PASSED' if success else 'FAILED'}")