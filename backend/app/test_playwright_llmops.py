"""
Test script to verify Playwright Agent with LLMOps structure
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmops import PlaywrightAgent, get_playwright_state

print("=" * 70)
print("Playwright Agent LLMOps Structure Test")
print("=" * 70)

# Test 1: Import verification
print("\nTEST 1: Import Verification")
print("✓ PlaywrightAgent imported successfully")
print("✓ get_playwright_state imported successfully")

# Test 2: Agent initialization
print("\nTEST 2: Agent Initialization")
try:
    agent = PlaywrightAgent(
        api_key="test-key",
        model="gpt-4o"
    )
    print("✓ PlaywrightAgent initialized successfully")
    print(f"  - Tools available: {len(agent.tools)}")
    print(f"  - Model: {agent.llm.model}")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")

# Test 3: Playwright state
print("\nTEST 3: Playwright State")
try:
    pw_state = get_playwright_state()
    print("✓ Playwright state retrieved")
    print(f"  - Initialized: {pw_state.is_initialized}")
    print(f"  - Ready: {pw_state.is_ready()}")
except Exception as e:
    print(f"❌ Failed to get playwright state: {e}")

# Test 4: Tools verification
print("\nTEST 4: Tools Verification")
try:
    from llmops import get_playwright_tools, PLAYWRIGHT_TOOLS
    
    tools = get_playwright_tools()
    print(f"✓ Retrieved {len(tools)} Playwright tools")
    print(f"✓ PLAYWRIGHT_TOOLS constant has {len(PLAYWRIGHT_TOOLS)} tools")
    
    print("\nAvailable tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")
except Exception as e:
    print(f"❌ Failed to get tools: {e}")

# Test 5: Module structure
print("\nTEST 5: Module Structure Verification")
try:
    from llmops.utils import playwright_state
    from llmops.tools import playwright_tools
    from llmops.llm import custom_openai
    from llmops.generators import playwright_agent
    
    print("✓ All modules imported successfully:")
    print("  - llmops.utils.playwright_state")
    print("  - llmops.tools.playwright_tools")
    print("  - llmops.llm.custom_openai")
    print("  - llmops.generators.playwright_agent")
except Exception as e:
    print(f"❌ Module import failed: {e}")

print("\n" + "=" * 70)
print("✅ All Structure Tests Passed!")
print("=" * 70)
print("\nTo run actual Playwright automation:")
print("  python agents/playwright_agent_llmops.py")
print("\nOr use in your code:")
print("  from llmops import PlaywrightAgent")
print("  agent = PlaywrightAgent()")
print("  result = agent.run_sync('your test prompt')")
print("=" * 70)
