# Playwright Metadata Tool Documentation

## Overview
Added comprehensive metadata extraction functionality to `playwright_tools.py` with the new `playwright_get_page_metadata` tool.

## New Tool: `playwright_get_page_metadata`

### Purpose
Extracts comprehensive metadata from the current page or specific elements, providing detailed information about page properties and element attributes.

### Signature
```python
@tool
async def playwright_get_page_metadata(selector: str = None) -> str
```

### Parameters
- **selector** (optional): CSS selector, XPath (prefix with `//`), or text (prefix with `text=`) to identify a specific element
  - If omitted: Returns only page-level metadata
  - If provided: Returns both page and element metadata

### Metadata Collected

#### Page-Level Metadata (Always Returned)
- **URL**: Current page URL
- **Title**: Page title

#### Element-Level Metadata (When Selector Provided)
The tool extracts 30+ attributes from HTML elements:

**Basic Attributes:**
- `tag`: HTML tag name (e.g., input, button, a)
- `id`: Element ID attribute
- `type`: Element type attribute
- `name`: Element name attribute
- `className`: CSS classes
- `text`: Element text content (first 200 characters)
- `value`: Current value (for inputs)

**Link & Media Attributes:**
- `href`: Link URL (for `<a>` tags)
- `src`: Source URL (for `<img>`, `<script>`, etc.)
- `alt`: Alternative text (for images)

**Form-Specific Attributes:**
- `inputType`: Input element type (text, email, password, etc.)
- `placeholder`: Placeholder text
- `maxLength`: Maximum character length
- `pattern`: Validation pattern (regex)
- `min`: Minimum value (for number/date inputs)
- `max`: Maximum value (for number/date inputs)
- `step`: Step value (for number inputs)
- `autocomplete`: Autocomplete setting

**Accessibility Attributes:**
- `ariaLabel`: ARIA label for screen readers
- `role`: ARIA role
- `title`: Title attribute (tooltip text)
- `tabIndex`: Tab navigation index

**State Attributes (Boolean):**
- `disabled`: Whether element is disabled
- `checked`: Whether checkbox/radio is checked
- `selected`: Whether option is selected
- `readonly`: Whether element is read-only
- `required`: Whether field is required
- `hidden`: Whether element has hidden attribute
- `isVisible`: Whether element is visible in viewport

**Layout & Position:**
- `boundingBox`: Element position and dimensions
  - `x`: X coordinate
  - `y`: Y coordinate
  - `width`: Element width in pixels
  - `height`: Element height in pixels

**Advanced Attributes:**
- `dataset`: All data-* attributes (as JSON)
- `innerHTML`: Inner HTML (first 300 characters)
- `outerHTML`: Outer HTML (first 300 characters)

### Usage Examples

#### Example 1: Get Page Metadata Only
```python
from llmops.tools.playwright_tools import playwright_get_page_metadata

# Navigate to a page first
await playwright_navigate.ainvoke({"url": "https://example.com"})

# Get page metadata
result = await playwright_get_page_metadata.ainvoke({"selector": None})
print(result)
```

**Output:**
```
📄 Page Metadata:
  • URL: https://example.com
  • Title: Example Domain
```

#### Example 2: Get Element Metadata (Button)
```python
# Get metadata for a button
result = await playwright_get_page_metadata.ainvoke({"selector": "button#submit"})
print(result)
```

**Output:**
```
📄 Page Metadata:
  • URL: https://example.com/form
  • Title: Contact Form

🎯 Element Metadata (Found 1 element(s)):
  • Selector: button#submit
  • Tag: <button>
  • ID: submit
  • Type: submit
  • Class: btn btn-primary
  • Text: Submit Form
  • Disabled: False
  • Hidden: False
  • Visible: True
  • Position: (x=120.5, y=450.0)
  • Size: 100.0x40.0px
  • Tab Index: 0
```

#### Example 3: Get Input Field Metadata
```python
# Get metadata for an email input
result = await playwright_get_page_metadata.ainvoke({"selector": "input[type='email']"})
print(result)
```

**Output:**
```
📄 Page Metadata:
  • URL: https://example.com/form
  • Title: Contact Form

🎯 Element Metadata (Found 1 element(s)):
  • Selector: input[type='email']
  • Tag: <input>
  • ID: email-field
  • Type: email
  • Name: user_email
  • Class: form-control
  • Placeholder: Enter your email
  • Input Type: email
  • Max Length: 100
  • Autocomplete: email
  • Disabled: False
  • Readonly: False
  • Required: True
  • Hidden: False
  • Visible: True
  • Position: (x=80.0, y=200.0)
  • Size: 300.0x35.0px
  • Tab Index: 0
```

#### Example 4: Get Link Metadata
```python
# Get metadata for a link
result = await playwright_get_page_metadata.ainvoke({"selector": "a.download-link"})
print(result)
```

**Output:**
```
📄 Page Metadata:
  • URL: https://example.com
  • Title: Downloads

🎯 Element Metadata (Found 1 element(s)):
  • Selector: a.download-link
  • Tag: <a>
  • Class: download-link
  • Text: Download PDF
  • Href: https://example.com/files/document.pdf
  • Title: Download the user guide
  • Visible: True
  • Position: (x=50.0, y=300.0)
  • Size: 150.0x30.0px
```

#### Example 5: Using XPath Selector
```python
# Get metadata using XPath
result = await playwright_get_page_metadata.ainvoke({"selector": "//div[@class='header']/h1"})
print(result)
```

#### Example 6: Using Text Selector
```python
# Get metadata by visible text
result = await playwright_get_page_metadata.ainvoke({"selector": "text=Click Here"})
print(result)
```

### Integration with Playwright Agent

The tool is automatically available in the LangGraph Playwright agent:

```python
from llmops import PlaywrightAgent

# Create agent
agent = PlaywrightAgent(
    api_key="your-api-key",
    model_name="gpt-4",
    browser_type="chromium"
)

# Use in agent workflow
result = await agent.run(
    "Go to example.com and extract all metadata from the submit button"
)
```

### Use Cases

1. **Automated Testing**: Verify element attributes match specifications
2. **Web Scraping**: Extract structured data from web elements
3. **Accessibility Audits**: Check ARIA labels and roles
4. **Form Validation**: Inspect input constraints and validation rules
5. **Layout Analysis**: Get element positions and dimensions
6. **Dynamic Element Discovery**: Find elements and their properties
7. **Test Case Generation**: Generate comprehensive element descriptions
8. **Debugging**: Inspect element state during automation

### Error Handling

The tool handles common errors gracefully:

```python
# Browser not initialized
result = await playwright_get_page_metadata.ainvoke({"selector": "button"})
# Returns: ❌ Browser not initialized. Please navigate to a page first.

# Element not found
result = await playwright_get_page_metadata.ainvoke({"selector": "#nonexistent"})
# Returns: ❌ No element found with selector: #nonexistent

# JavaScript evaluation error
# Returns: ❌ Failed to get metadata: [error details]
```

### Performance Considerations

- Metadata extraction uses efficient JavaScript evaluation
- Text content truncated to 200 characters
- HTML content truncated to 300 characters
- Only non-null attributes are displayed
- Single element evaluation (first match if multiple elements)

### Tool List Update

The `PLAYWRIGHT_TOOLS` list now includes **10 tools** (previously 9):

```python
PLAYWRIGHT_TOOLS = [
    playwright_navigate,
    playwright_click,
    playwright_type,
    playwright_screenshot,
    playwright_wait_for_selector,
    playwright_wait_for_text,
    playwright_get_page_content,
    playwright_execute_javascript,
    playwright_get_page_metadata,  # ← NEW
    playwright_close_browser,
]
```

### Testing

Run the test suite to verify functionality:

```bash
# Run metadata tool test
python test_metadata_tool.py
```

The test suite covers:
1. Page-level metadata extraction
2. Element metadata for headings
3. Link element metadata
4. Form input metadata with validation rules
5. Browser lifecycle management

### Technical Implementation

**Key Features:**
- Uses Playwright's `locator.evaluate()` for efficient data extraction
- Single JavaScript execution per element (minimal overhead)
- Comprehensive attribute coverage (30+ properties)
- Smart null filtering (only shows present attributes)
- Pretty-printed output with emojis for readability
- Bounding box calculation using `getBoundingClientRect()`
- Visibility detection using `offsetParent` check
- Dataset conversion to JSON string

**JavaScript Evaluation:**
```javascript
(el) => {
    return {
        // Extract all relevant attributes
        tag: el.tagName.toLowerCase(),
        id: el.id || null,
        // ... 30+ more attributes
        boundingBox: {
            x: el.getBoundingClientRect().x,
            y: el.getBoundingClientRect().y,
            width: el.getBoundingClientRect().width,
            height: el.getBoundingClientRect().height
        },
        isVisible: el.offsetParent !== null
    };
}
```

## Summary

✅ Added `playwright_get_page_metadata` tool to `playwright_tools.py`  
✅ Extracts 30+ element attributes and page properties  
✅ Supports CSS selectors, XPath, and text selectors  
✅ Includes page URL, title, element attributes, position, and visibility  
✅ Graceful error handling for missing elements  
✅ Tool count increased from 9 to 10  
✅ Created test suite (`test_metadata_tool.py`)  
✅ Ready for use in Playwright Agent workflows  

The metadata tool provides comprehensive element inspection capabilities for automated testing, web scraping, and test case generation workflows.
