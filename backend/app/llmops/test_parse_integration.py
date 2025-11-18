"""
Quick test to verify parse_metadata_from_output works with test_metadata_extraction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llmops_api import parse_metadata_from_output
import json

# Sample agent output (what the Playwright agent returns)
SAMPLE_AGENT_OUTPUT = """Tool execution results:
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
  • ID: None
  • Name: None
  • Class: None

✅ playwright_screenshot: ✅ Screenshot saved to: example_com_screenshot.png
✅ playwright_close_browser: ✅ Browser closed successfully"""

def test_parse():
    print("=" * 70)
    print("Testing parse_metadata_from_output Function")
    print("=" * 70)
    
    print("\n[1/3] Parsing sample agent output...")
    pages = parse_metadata_from_output(SAMPLE_AGENT_OUTPUT)
    
    if not pages:
        print("❌ No pages parsed!")
        return False
    
    print(f"✅ Parsed {len(pages)} page(s)")
    
    print("\n[2/3] Converting to clean JSON format...")
    clean_output = {
        "pages": [
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
    }
    
    print("\n[3/3] Formatted Output:")
    print("=" * 70)
    print(json.dumps(clean_output, indent=2))
    print("=" * 70)
    
    # Save to file
    output_file = "test_clean_metadata.json"
    with open(output_file, 'w') as f:
        json.dump(clean_output, f, indent=2)
    
    print(f"\n✅ Saved to: {output_file}")
    
    # Verify structure
    page = clean_output["pages"][0]
    assert page["id"] == "page_1"
    assert page["label"] == "Example Domain (example.com)"
    assert page["metadata"]["url"] == "https://example.com/"
    assert page["metadata"]["title"] == "Example Domain"
    assert len(page["metadata"]["key_elements"]) == 1
    
    elem = page["metadata"]["key_elements"][0]
    assert elem["type"] == "link"
    assert elem["tag"] == "a"
    assert elem["text"] == "More information..."
    assert elem["href"] == "https://www.iana.org/domains/example"
    
    print("\n✅ All assertions passed!")
    return True

if __name__ == "__main__":
    success = test_parse()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ TEST PASSED - parse_metadata_from_output works correctly!")
        print("=" * 70)
        print("\n💡 This function is now integrated into test_metadata_extraction.py")
    else:
        print("\n❌ TEST FAILED")
