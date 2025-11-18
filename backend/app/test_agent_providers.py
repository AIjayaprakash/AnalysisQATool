"""
Test script to verify Playwright Agent works with OpenAI/Groq
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend/app to path
import sys
sys.path.insert(0, r'e:\Kirsh Naik Academy\SeleniumMCPFlow\backend\app')

from llmops import PlaywrightAgent, LLMOpsConfig

async def test_playwright_agent():
    """Test Playwright Agent with OpenAI or Groq"""
    
    print("=" * 70)
    print("Testing Playwright Agent with OpenAI/Groq")
    print("=" * 70)
    
    # Create config
    config = LLMOpsConfig()
    
    # Show which provider is being used
    provider = "Groq" if config.use_groq else "OpenAI"
    print(f"\n✓ Using Provider: {provider}")
    print(f"✓ Groq API Key: {'Set' if config.groq_api_key else 'Not Set'}")
    print(f"✓ OpenAI API Key: {'Set' if config.openai_api_key else 'Not Set'}")
    print(f"✓ Browser Type: {config.browser_type}")
    
    try:
        # Initialize agent with config
        print(f"\n[1/3] Initializing Playwright Agent...")
        agent = PlaywrightAgent(config=config)
        print("✅ Agent initialized successfully")
        
        # Create a simple test prompt
        test_prompt = """
        1) Navigate to https://example.com
        2) Wait for page to load
        3) Extract page metadata including URL and title
        4) Take a screenshot named 'test_example.png'
        5) Close the browser
        """
        
        print(f"\n[2/3] Running test automation...")
        print(f"Test Prompt:\n{test_prompt}")
        
        # Run the automation
        result = await agent.run(
            test_prompt=test_prompt,
            max_iterations=10,
            browser_config={
                "headless": False,
                "browser_type": config.browser_type
            }
        )
        
        print(f"\n[3/3] Test completed!")
        print(f"\n{'=' * 70}")
        print("RESULTS")
        print('=' * 70)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Tool Calls: {result.get('tool_calls', 0)}")
        print(f"Total Messages: {result.get('total_messages', 0)}")
        print(f"\nFinal Response:\n{result.get('final_response', 'No response')[:500]}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_playwright_agent())
    
    if result and result.get("status") == "success":
        print("\n✅ Test PASSED - Agent works correctly with OpenAI/Groq!")
    else:
        print("\n❌ Test FAILED - Check the error messages above")
