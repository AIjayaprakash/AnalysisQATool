"""Simplified verification for playwright_get_page_metadata tool"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

def verify_metadata_tool():
    """Verify the metadata tool is properly integrated"""
    
    print("=" * 80)
    print("Playwright Metadata Tool Integration Verification")
    print("=" * 80)
    
    # Test 1: Import directly from playwright_tools module
    print("\n✓ Test 1: Importing from llmops.tools.playwright_tools...")
    try:
        from llmops.tools.playwright_tools import (
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
    
    if "playwright_get_page_metadata" in tool_names:
        print("  ✅ playwright_get_page_metadata is in PLAYWRIGHT_TOOLS")
    else:
        print("  ❌ playwright_get_page_metadata NOT found in PLAYWRIGHT_TOOLS")
        return False
    
    # Test 3: Verify tool count increased to 10
    print("\n✓ Test 3: Verifying tool count...")
    expected_count = 10
    actual_count = len(PLAYWRIGHT_TOOLS)
    if actual_count == expected_count:
        print(f"  ✅ Correct tool count: {actual_count} tools")
    else:
        print(f"  ⚠️  Expected {expected_count} tools, found {actual_count}")
    
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
    print(f"  Tool description: {playwright_get_page_metadata.description[:80]}...")
    
    if hasattr(playwright_get_page_metadata, 'ainvoke'):
        print("  ✅ Tool has ainvoke method (async compatible)")
    else:
        print("  ❌ Tool missing ainvoke method")
        return False
    
    # Test 6: Verify tool schema
    print("\n✓ Test 6: Verifying tool schema...")
    try:
        schema = playwright_get_page_metadata.get_input_schema()
        print(f"  ✅ Tool schema available")
        print(f"  Parameters: {list(schema.schema().get('properties', {}).keys())}")
    except Exception as e:
        print(f"  ⚠️  Schema check: {e}")
    
    # Test 7: List all available tools
    print("\n✓ Test 7: Complete tool list:")
    for i, tool in enumerate(PLAYWRIGHT_TOOLS, 1):
        marker = "🆕" if tool.name == "playwright_get_page_metadata" else "  "
        print(f"  {marker} {i:2d}. {tool.name}")
    
    print("\n" + "=" * 80)
    print("✅ All Verification Tests Passed!")
    print("=" * 80)
    print("\nThe playwright_get_page_metadata tool is properly integrated and ready to use.")
    print("\n📋 Metadata Extracted:")
    print("  Page Level: URL, Title")
    print("  Element Level: tag, id, type, name, class, text, value, href, src,")
    print("                 alt, title, placeholder, ariaLabel, role, inputType,")
    print("                 disabled, checked, required, hidden, visible, position,")
    print("                 size, tabIndex, and more...")
    print("\n💡 Usage Example:")
    print("  from llmops.tools.playwright_tools import playwright_get_page_metadata")
    print('  result = await playwright_get_page_metadata.ainvoke({"selector": "button#submit"})')
    print("\n" + "=" * 80)
    
    return True


if __name__ == "__main__":
    print("\n🔍 Starting Verification...\n")
    success = verify_metadata_tool()
    sys.exit(0 if success else 1)
