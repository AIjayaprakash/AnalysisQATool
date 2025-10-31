"""
Test script to demonstrate the expected Groq manual function calling format
"""

def test_groq_parsing():
    # Example of what Groq should generate for tool calls
    sample_groq_response = """I'll help you navigate to the website and take a screenshot. Let me execute this test step by step.

TOOL_CALL: mcp_playwright_browser_navigate
ARGS: {"url": "https://example.com"}

TOOL_CALL: mcp_playwright_browser_take_screenshot
ARGS: {"filename": "example_page.png"}

I have executed the browser automation steps to navigate to example.com and capture a screenshot."""

    # Test the parsing logic
    import re
    import json
    
    pattern = r'TOOL_CALL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]+\})'
    matches = re.findall(pattern, sample_groq_response, re.MULTILINE)
    
    print("Parsed tool calls:")
    for tool_name, args_str in matches:
        tool_name = tool_name.strip()
        try:
            args = json.loads(args_str)
            print(f"  - {tool_name}: {args}")
        except json.JSONDecodeError as e:
            print(f"  - ERROR parsing {tool_name}: {e}")

if __name__ == "__main__":
    test_groq_parsing()