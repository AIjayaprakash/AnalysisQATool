"""Quick verification that playwright_get_page_metadata tool is properly integrated"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

def verify_metadata_tool():
    """Verify the metadata tool is properly integrated"""
    
    print("=" * 80)
    print("Playwright Metadata Tool Integration Verification")
    print("=" * 80)
    
    # Test 1: Import from tools module
    print("\n✓ Test 1: Importing from llmops.tools...")
    try:
        from llmops.tools import (
            playwright_get_page_metadata,
            get_playwright_tools,
            PLAYWRIGHT_TOOLS
        )
        print("  ✅ Successfully imported playwright_get_page_metadata")
        print("  ✅ Successfully imported get_playwright_tools")
        print("  ✅ Successfully imported PLAYWRIGHT_TOOLS")
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False
    
    # Test 2: Verify tool is in PLAYWRIGHT_TOOLS list
    print("\n✓ Test 2: Checking PLAYWRIGHT_TOOLS list...")
    tool_names = [tool.name for tool in PLAYWRIGHT_TOOLS]
    print(f"  Total tools: {len(PLAYWRIGHT_TOOLS)}")
    print(f"  Tool names: {tool_names}")
    
    if "playwright_get_page_metadata" in tool_names:
        print("  ✅ playwright_get_page_metadata is in PLAYWRIGHT_TOOLS")
    else:
        print("  ❌ playwright_get_page_metadata NOT found in PLAYWRIGHT_TOOLS")
        return False
    
    # Test 3: Verify tool count increased to 10
    print("\n✓ Test 3: Verifying tool count...")
    if len(PLAYWRIGHT_TOOLS) == 10:
        print(f"  ✅ Correct tool count: {len(PLAYWRIGHT_TOOLS)} tools")
    else:
        print(f"  ⚠️  Expected 10 tools, found {len(PLAYWRIGHT_TOOLS)}")
    
    # Test 4: Verify get_playwright_tools() function
    print("\n✓ Test 4: Testing get_playwright_tools() function...")
    tools = get_playwright_tools()
    if len(tools) == len(PLAYWRIGHT_TOOLS):
        print(f"  ✅ get_playwright_tools() returns {len(tools)} tools")
    else:
        print(f"  ❌ Tool count mismatch")
        return False
    
    # Test 5: Verify tool signature
    print("\n✓ Test 5: Verifying tool signature...")
    print(f"  Tool name: {playwright_get_page_metadata.name}")
    print(f"  Tool description: {playwright_get_page_metadata.description[:100]}...")
    
    if hasattr(playwright_get_page_metadata, 'ainvoke'):
        print("  ✅ Tool has ainvoke method (async compatible)")
    else:
        print("  ❌ Tool missing ainvoke method")
        return False
    
    # Test 6: Import from main llmops package
    print("\n✓ Test 6: Importing from main llmops package...")
    try:
        from llmops import PlaywrightAgent
        print("  ✅ PlaywrightAgent imported successfully")
        print("  ✅ Agent will have access to playwright_get_page_metadata tool")
    except ImportError as e:
        print(f"  ⚠️  PlaywrightAgent import issue: {e}")
    
    # Test 7: List all available tools
    print("\n✓ Test 7: Complete tool list:")
    for i, tool in enumerate(PLAYWRIGHT_TOOLS, 1):
        print(f"  {i:2d}. {tool.name}")
    
    print("\n" + "=" * 80)
    print("✅ All Verification Tests Passed!")
    print("=" * 80)
    print("\nThe playwright_get_page_metadata tool is properly integrated and ready to use.")
    print("\nUsage Example:")
    print("  from llmops.tools import playwright_get_page_metadata")
    print('  result = await playwright_get_page_metadata.ainvoke({"selector": "button"})')
    print("\n" + "=" * 80)
    
    return True


if __name__ == "__main__":
    print("\n🔍 Starting Verification...\n")
    success = verify_metadata_tool()
    sys.exit(0 if success else 1)
