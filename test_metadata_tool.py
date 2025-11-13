"""Test script for playwright_get_page_metadata tool"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from llmops.tools.playwright_tools import (
    playwright_navigate,
    playwright_get_page_metadata,
    playwright_close_browser
)


async def test_metadata_tool():
    """Test the metadata extraction functionality"""
    
    print("=" * 80)
    print("Testing playwright_get_page_metadata Tool")
    print("=" * 80)
    
    # Test 1: Navigate to a page
    print("\n1. Navigating to example.com...")
    result = await playwright_navigate.ainvoke({"url": "https://example.com"})
    print(result)
    
    # Test 2: Get page metadata only (no selector)
    print("\n2. Getting page-level metadata...")
    result = await playwright_get_page_metadata.ainvoke({"selector": None})
    print(result)
    
    # Test 3: Get metadata for a specific element (h1)
    print("\n3. Getting metadata for <h1> element...")
    result = await playwright_get_page_metadata.ainvoke({"selector": "h1"})
    print(result)
    
    # Test 4: Get metadata for a link element
    print("\n4. Getting metadata for <a> (link) element...")
    result = await playwright_get_page_metadata.ainvoke({"selector": "a"})
    print(result)
    
    # Test 5: Navigate to a form page and get input metadata
    print("\n5. Navigating to a form example...")
    result = await playwright_navigate.ainvoke({"url": "https://www.w3schools.com/html/html_forms.asp"})
    print(result)
    
    # Wait a moment for page to load
    await asyncio.sleep(2)
    
    # Test 6: Get metadata for input element
    print("\n6. Getting metadata for input element...")
    result = await playwright_get_page_metadata.ainvoke({"selector": "input[type='text']"})
    print(result)
    
    # Clean up
    print("\n7. Closing browser...")
    result = await playwright_close_browser.ainvoke({})
    print(result)
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🧪 Playwright Metadata Tool Test Suite\n")
    asyncio.run(test_metadata_tool())
