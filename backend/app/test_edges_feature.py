"""
Test the new edges feature in parse_metadata_from_output
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
from llmops_api import parse_metadata_from_output

def test_edges_parsing():
    """Test that edges are correctly parsed from tool execution results"""
    
    # Sample output with multiple pages and click actions
    # Page 1: 2 elements, Page 2: 3 elements, Page 3: 1 element
    sample_output = """
Tool execution results:
✅ playwright_navigate: ✅ Successfully navigated to https://example.com - Page title: 'Example Domain'
✅ playwright_get_page_metadata: 📄 Page Metadata:
  • URL: https://example.com/
  • Title: Example Domain

🎯 Element Metadata (Found 2 element(s)):
  • Selector: a
  • Tag: <a>
  • Type: link
  • Text: More information...
  • ID: None
  • Name: None
  • Class: link-main
  • Href: https://www.iana.org/domains/example
  • Input Type: None

  • Selector: p
  • Tag: <p>
  • Type: paragraph
  • Text: This domain is for use in illustrative examples
  • ID: example-text
  • Name: None
  • Class: description
  • Href: None
  • Input Type: None

✅ playwright_click: ✅ Clicked on element: More information...
✅ playwright_navigate: ✅ Successfully navigated to https://www.iana.org/domains/example
✅ playwright_get_page_metadata: 📄 Page Metadata:
  • URL: https://www.iana.org/domains/example
  • Title: IANA — IANA-managed Reserved Domains

🎯 Element Metadata (Found 3 element(s)):
  • Selector: a
  • Tag: <a>
  • Type: link
  • Text: About
  • ID: about-link
  • Name: None
  • Class: nav-link
  • Href: https://www.iana.org/about
  • Input Type: None

  • Selector: button
  • Tag: <button>
  • Type: button
  • Text: Submit
  • ID: submit-btn
  • Name: submit
  • Class: btn-primary
  • Href: None
  • Input Type: None

  • Selector: input
  • Tag: <input>
  • Type: input
  • Text: None
  • ID: search-input
  • Name: search
  • Class: form-control
  • Href: None
  • Input Type: text

✅ playwright_click: ✅ Clicked on element: About
✅ playwright_navigate: ✅ Successfully navigated to https://www.iana.org/about
✅ playwright_get_page_metadata: 📄 Page Metadata:
  • URL: https://www.iana.org/about
  • Title: About Us

🎯 Element Metadata (Found 1 element(s)):
  • Selector: a
  • Tag: <a>
  • Type: link
  • Text: Contact Us
  • ID: contact-link
  • Name: None
  • Class: footer-link
  • Href: https://www.iana.org/contact
  • Input Type: None

✅ playwright_screenshot: ✅ Screenshot saved to about.png
✅ playwright_close_browser: ✅ Browser closed successfully
"""
    
    print("=" * 80)
    print("Testing Edge Extraction Feature")
    print("=" * 80)
    
    # Parse the output
    pages, edges = parse_metadata_from_output(sample_output)
    
    print(f"\n✅ Parsed {len(pages)} pages")
    for page in pages:
        print(f"   • {page.id}: {page.label}")
    
    print(f"\n✅ Parsed {len(edges)} edges")
    for edge in edges:
        print(f"   • {edge.source} → {edge.target}: {edge.label}")
    
    # Verify structure
    print("\n" + "=" * 80)
    print("Expected Edge Structure:")
    print("=" * 80)
    
    expected_edges = [
        {
            "source": "page_1",
            "target": "page_2",
            "label": "Click More Informati..."
        },
        {
            "source": "page_2",
            "target": "page_3",
            "label": "Click About"
        }
    ]
    
    print("Expected:")
    for edge in expected_edges:
        print(f"   • {edge['source']} → {edge['target']}: {edge['label']}")
    
    # Validate
    print("\n" + "=" * 80)
    print("Validation:")
    print("=" * 80)
    
    if len(pages) == 3:
        print("✅ Correct number of pages (3)")
    else:
        print(f"❌ Expected 3 pages, got {len(pages)}")
    
    # Validate element counts per page
    if len(pages) >= 1:
        page1_elements = len(pages[0].metadata.key_elements)
        if page1_elements == 2:
            print(f"✅ Page 1: Correct number of elements (2)")
        else:
            print(f"❌ Page 1: Expected 2 elements, got {page1_elements}")
    
    if len(pages) >= 2:
        page2_elements = len(pages[1].metadata.key_elements)
        if page2_elements == 3:
            print(f"✅ Page 2: Correct number of elements (3)")
        else:
            print(f"❌ Page 2: Expected 3 elements, got {page2_elements}")
    
    if len(pages) >= 3:
        page3_elements = len(pages[2].metadata.key_elements)
        if page3_elements == 1:
            print(f"✅ Page 3: Correct number of elements (1)")
        else:
            print(f"❌ Page 3: Expected 1 element, got {page3_elements}")
    
    if len(edges) == 2:
        print("✅ Correct number of edges (2)")
    else:
        print(f"❌ Expected 2 edges, got {len(edges)}")
    
    if edges:
        if edges[0].source == "page_1" and edges[0].target == "page_2":
            print("✅ Edge 1: Correct source and target")
        else:
            print(f"❌ Edge 1: Expected page_1 → page_2, got {edges[0].source} → {edges[0].target}")
        
        if "More Informati" in edges[0].label or "Click" in edges[0].label:
            print(f"✅ Edge 1: Label contains action info: '{edges[0].label}'")
        else:
            print(f"⚠️  Edge 1: Label might not contain action info: '{edges[0].label}'")
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)
    
    return pages, edges


if __name__ == "__main__":
    pages, edges = test_edges_parsing()
    
    # Print JSON structure
    print("\n" + "=" * 80)
    print("JSON Output Format:")
    print("=" * 80)
    
    import json
    
    output = {
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
                            "text": elem.text
                        }
                        for elem in page.metadata.key_elements
                    ]
                }
            }
            for page in pages
        ],
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "label": edge.label
            }
            for edge in edges
        ]
    }
    
    print(json.dumps(output, indent=2))
