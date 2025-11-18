"""
Test script to verify metadata-only endpoint returns clean JSON structure
"""

import asyncio
import json
import sys
sys.path.insert(0, r'e:\Kirsh Naik Academy\SeleniumMCPFlow\backend\app')

from llmops import PlaywrightAgent, LLMOpsConfig
from llmops_api import parse_metadata_from_output

# Sample agent output (simulating what the agent returns)
SAMPLE_OUTPUT = """Tool execution results:
✅ playwright_navigate: ✅ Successfully navigated to https://example.com - Page title: 'Example Domain'
✅ playwright_wait_for_text: ✅ Text 'Example Domain' appeared on page
✅ playwright_get_page_metadata: 📄 Page Metadata:
  • URL: https://example.com/
  • Title: Example Domain

✅ playwright_wait_for_selector: ✅ Element a, button appeared on page
✅ playwright_get_page_metadata: 📄 Page Metadata:
  • URL: https://example.com/
  • Title: Example Domain

🎯 Element Metadata (Found 1 element(s)):
  • Selector: a
  • Tag: <a>
  • Text: More information...
  • Href: https://www.iana.org/domains/example
  • Data Attributes: {}

✅ playwright_screenshot: ✅ Screenshot saved
✅ playwright_close_browser: ✅ Browser closed successfully"""

async def test_metadata_parsing():
    """Test that metadata parsing works correctly"""
    
    print("=" * 70)
    print("Testing Metadata Extraction")
    print("=" * 70)
    
    print("\n[1/2] Parsing sample agent output...")
    
    # Parse the output
    pages = parse_metadata_from_output(SAMPLE_OUTPUT)
    
    print(f"✅ Found {len(pages)} page(s)")
    
    if pages:
        print("\n[2/2] Converting to JSON...")
        
        # Convert to dict for JSON serialization
        pages_data = [
            {
                "id": page.id,
                "label": page.label,
                "x": page.x,
                "y": page.y,
                "metadata": {
                    "url": page.metadata.url,
                    "title": page.metadata.title,
                    "key_elements": [
                        {
                            "id": elem.id,
                            "type": elem.type,
                            "tag": elem.tag,
                            "text": elem.text,
                            "element_id": elem.element_id,
                            "name": elem.name,
                            "class": elem.class_name,
                            "href": elem.href,
                            "input_type": elem.input_type,
                            "depends_on": elem.depends_on
                        }
                        for elem in page.metadata.key_elements
                    ]
                }
            }
            for page in pages
        ]
        
        # Create final output
        output = {"pages": pages_data}
        
        print("\n" + "=" * 70)
        print("EXTRACTED METADATA (Clean JSON)")
        print("=" * 70)
        print(json.dumps(output, indent=2))
        
        # Save to file
        output_file = "metadata_clean_output.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Saved to: {output_file}")
        
        return output
    else:
        print("\n❌ No pages found in output!")
        print("\nDebug: Checking for metadata markers...")
        print(f"  - Found '📄 Page Metadata': {'📄 Page Metadata' in SAMPLE_OUTPUT}")
        print(f"  - Found '🎯 Element Metadata': {'🎯 Element Metadata' in SAMPLE_OUTPUT}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_metadata_parsing())
    
    if result and result.get("pages"):
        print("\n✅ TEST PASSED - Clean metadata extraction works!")
    else:
        print("\n❌ TEST FAILED - No metadata extracted")
