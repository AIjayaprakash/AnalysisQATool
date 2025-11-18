"""Test playwright_get_page_metadata tool with None selector"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from llmops.tools.playwright_tools import (
    playwright_get_page_metadata,
    playwright_navigate,
    playwright_close_browser
)


async def test_metadata_with_none():
    """Test that playwright_get_page_metadata accepts None for selector"""
    
    print("=" * 80)
    print("Testing playwright_get_page_metadata with None selector")
    print("=" * 80)
    
    try:
        # Test 1: Navigate to a page
        print("\n1. Navigating to example.com...")
        result = await playwright_navigate.ainvoke({"url": "https://example.com"})
        print(result)
        
        # Test 2: Get page metadata with None selector
        print("\n2. Testing with selector=None (should work now)...")
        try:
            result = await playwright_get_page_metadata.ainvoke({"selector": None})
            print("✅ SUCCESS! Tool accepts None for selector")
            print(result)
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
        
        # Test 3: Get page metadata without selector parameter
        print("\n3. Testing without selector parameter (default None)...")
        try:
            result = await playwright_get_page_metadata.ainvoke({})
            print("✅ SUCCESS! Tool works with empty dict")
            print(result)
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
        
        # Test 4: Get element metadata with specific selector
        print("\n4. Testing with specific selector (should also work)...")
        try:
            result = await playwright_get_page_metadata.ainvoke({"selector": "h1"})
            print("✅ SUCCESS! Tool works with selector string")
            print(result)
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            return False
        
        # Clean up
        print("\n5. Closing browser...")
        result = await playwright_close_browser.ainvoke({})
        print(result)
        
        print("\n" + "=" * 80)
        print("✅ All tests passed! Tool accepts Optional[str] correctly")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Testing playwright_get_page_metadata with None selector fix\n")
    success = asyncio.run(test_metadata_with_none())
    sys.exit(0 if success else 1)
