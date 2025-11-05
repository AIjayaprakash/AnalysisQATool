"""
Simple test for Groq-only Playwright Direct Agent
This will test the agent using only Groq AI without OpenAI dependency
"""

import asyncio
import sys
import os

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents'))

from playwright_direct_agent import run_test_with_visible_browser

def test_groq_only_agent():
    """Test the agent with Groq AI only"""
    
    print("🤖 GROQ-ONLY PLAYWRIGHT AUTOMATION TEST")
    print("======================================")
    print("🎯 Testing Playwright automation using only Groq AI (llama-3.3-70b-versatile)")
    print("📺 Browser window will be visible during automation")
    print()
    
    # Simple test case
    test_prompt = "Navigate to https://example.com, take a screenshot, and close the browser"
    
    print(f"🎯 Test: {test_prompt}")
    print("🚀 Starting automation...")
    
    try:
        result = run_test_with_visible_browser(
            prompt=test_prompt,
            max_iterations=8,
            headless=False  # Visible browser
        )
        
        print(f"\n✅ TEST COMPLETED!")
        print(f"📊 Results:")
        print(f"  Status: {result['status']}")
        print(f"  Steps executed: {result.get('steps_executed', 0)}")
        print(f"  Browser config: {result.get('browser_config', {})}")
        
        if result.get('errors'):
            print(f"  ⚠️ Errors: {result['errors']}")
        
        if result.get('results'):
            print(f"  🔧 Tool execution steps:")
            for i, step_result in enumerate(result['results'], 1):
                tools_used = ', '.join(step_result.get('tool_names', []))
                print(f"    Step {i}: {tools_used}")
        
        print(f"\n💡 This test used ONLY Groq AI - no OpenAI dependency!")
        
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("💡 Make sure GROQ_API_KEY is set in your environment")
        return False

if __name__ == "__main__":
    print("🔧 Groq-Only Agent Test")
    print("Make sure you have GROQ_API_KEY set in your environment variables")
    print("Get your free API key from: https://console.groq.com/keys")
    print()
    
    success = test_groq_only_agent()
    
    if success:
        print("\n🎉 SUCCESS: Groq-only Playwright automation is working!")
    else:
        print("\n❌ FAILED: Check your Groq API key and try again")