# 🗂️ Playwright Metadata Extraction Feature

## Overview

The Playwright API now automatically extracts and returns structured metadata for all pages and elements processed during automation. The metadata is returned in a standardized JSON format suitable for visualization and analysis.

## 📋 Metadata Structure

### Complete Response Format

```json
{
  "test_id": "TC_001",
  "status": "success",
  "execution_time": 12.5,
  "steps_executed": 8,
  "agent_output": "...",
  "screenshots": ["step1.png"],
  "error_message": null,
  "executed_at": "2025-11-18T10:30:00",
  "pages": [
    {
      "id": "page_1",
      "label": "Example Domain (example.com)",
      "x": 200,
      "y": 100,
      "metadata": {
        "url": "https://example.com/",
        "title": "Example Domain",
        "key_elements": [
          {
            "id": "element_1",
            "type": "link",
            "tag": "a",
            "text": "More information...",
            "element_id": null,
            "name": null,
            "class_name": null,
            "href": "https://www.iana.org/domains/example",
            "input_type": null,
            "depends_on": []
          }
        ]
      }
    }
  ]
}
```

## 📐 Schema Definitions

### PageNode

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique page identifier (e.g., "page_1") |
| label | string | Display label with title and domain |
| x | integer | X coordinate for visualization (auto-calculated) |
| y | integer | Y coordinate for visualization (default: 100) |
| metadata | PageMetadata | Page metadata object |

### PageMetadata

| Field | Type | Description |
|-------|------|-------------|
| url | string | Full page URL |
| title | string | Page title from `<title>` tag |
| key_elements | array[ElementMetadata] | Array of extracted elements |

### ElementMetadata

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique element identifier (e.g., "element_1") |
| type | string | Element type (link, button, input, form, etc.) |
| tag | string | HTML tag name (a, button, input, etc.) |
| text | string \| null | Element text content (truncated to 200 chars) |
| element_id | string \| null | HTML `id` attribute value |
| name | string \| null | HTML `name` attribute value |
| class_name | string \| null | HTML `class` attribute value |
| href | string \| null | Link `href` attribute (for `<a>` tags) |
| input_type | string \| null | Input `type` attribute (for `<input>` tags) |
| depends_on | array[string] | Dependencies on other elements (for future use) |

## 🔧 How It Works

### 1. Agent Instructions

The Playwright agent is instructed to:
- Use `playwright_get_page_metadata(selector=null)` after navigating to each page
- Use `playwright_get_page_metadata(selector="...")` before interacting with elements
- Extract metadata for all links, buttons, inputs, and forms

### 2. Metadata Extraction

The `playwright_get_page_metadata` tool extracts:
- **Page-level:** URL, title
- **Element-level:** Tag, type, text, id, name, class, href, input_type, position, visibility, etc.

### 3. Output Parsing

The API endpoint parses the agent output to:
- Find all metadata blocks (page and element)
- Structure data into PageNode format
- Assign unique IDs to pages and elements
- Calculate coordinates for visualization

### 4. Response Structure

Metadata is returned in the `pages` array of the response, with each page containing:
- Page identification and coordinates
- URL and title
- Array of extracted elements with full attributes

## 📝 Usage Examples

### Example 1: Basic Metadata Extraction

```python
import requests

response = requests.post(
    "http://localhost:8000/execute-playwright-from-testcase",
    json={
        "test_id": "TC_001",
        "module": "Navigation",
        "functionality": "Page Analysis",
        "description": "Extract metadata from example.com"
    }
)

result = response.json()

# Access pages
for page in result['pages']:
    print(f"Page: {page['label']}")
    print(f"URL: {page['metadata']['url']}")
    print(f"Elements: {len(page['metadata']['key_elements'])}")
    
    # Access elements
    for element in page['metadata']['key_elements']:
        print(f"  - {element['type']}: {element['text']}")
```

### Example 2: Extract Specific Element Types

```python
# Get all links from all pages
all_links = []
for page in result['pages']:
    links = [e for e in page['metadata']['key_elements'] if e['type'] == 'link']
    all_links.extend(links)

print(f"Total links found: {len(all_links)}")
for link in all_links:
    print(f"  {link['text']}: {link['href']}")
```

### Example 3: Build Visualization Data

```python
# Create node-edge graph for visualization
nodes = []
edges = []

for page in result['pages']:
    # Add page node
    nodes.append({
        "id": page['id'],
        "label": page['label'],
        "type": "page",
        "x": page['x'],
        "y": page['y']
    })
    
    # Add element nodes
    for element in page['metadata']['key_elements']:
        nodes.append({
            "id": element['id'],
            "label": element['text'] or element['type'],
            "type": element['type'],
            "x": page['x'],
            "y": page['y'] + 50
        })
        
        # Create edge from page to element
        edges.append({
            "from": page['id'],
            "to": element['id']
        })
```

## 🎯 Element Types

The `type` field is automatically determined from the HTML tag:

| Tag | Type | Description |
|-----|------|-------------|
| `a` | link | Hyperlinks |
| `button` | button | Buttons |
| `input` | input | Input fields |
| `form` | form | Forms |
| `select` | select | Dropdowns |
| `textarea` | textarea | Text areas |
| Other | tag name | Falls back to tag name |

## 📊 Metadata Extraction Rules

### Page Metadata
- Extracted after `playwright_navigate` tool is used
- Captured when `playwright_get_page_metadata(selector=null)` is called
- Includes URL from browser and title from page

### Element Metadata
- Extracted when `playwright_get_page_metadata(selector="...")` is called
- Agent is instructed to extract metadata before interactions
- Only "key elements" (interacted with) are captured

### Automatic Extraction
The agent automatically extracts metadata for:
✅ Navigation targets (main pages)  
✅ Clickable elements (links, buttons)  
✅ Input fields (text, email, password, etc.)  
✅ Form elements  
✅ Any element the agent interacts with  

## 🔍 Accessing Metadata

### Python Example

```python
import requests
import json

# Execute automation
response = requests.post(
    "http://localhost:8000/execute-playwright",
    json={
        "test_id": "TC_001",
        "generated_prompt": "Navigate to example.com and analyze the page",
        "browser_type": "chromium"
    }
)

result = response.json()

# Pretty print metadata
print(json.dumps(result['pages'], indent=2))

# Access specific data
first_page = result['pages'][0]
print(f"URL: {first_page['metadata']['url']}")
print(f"Title: {first_page['metadata']['title']}")
print(f"Elements: {len(first_page['metadata']['key_elements'])}")

# Filter elements
links = [e for e in first_page['metadata']['key_elements'] if e['type'] == 'link']
buttons = [e for e in first_page['metadata']['key_elements'] if e['type'] == 'button']
inputs = [e for e in first_page['metadata']['key_elements'] if e['type'] == 'input']

print(f"Links: {len(links)}")
print(f"Buttons: {len(buttons)}")
print(f"Inputs: {len(inputs)}")
```

### JavaScript/Frontend Example

```javascript
// Fetch automation results
fetch('http://localhost:8000/execute-playwright', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    test_id: 'TC_001',
    generated_prompt: 'Navigate and extract metadata',
    browser_type: 'chromium'
  })
})
.then(res => res.json())
.then(data => {
  // Access pages
  data.pages.forEach(page => {
    console.log(`Page: ${page.label}`);
    console.log(`URL: ${page.metadata.url}`);
    
    // Access elements
    page.metadata.key_elements.forEach(elem => {
      console.log(`  ${elem.type}: ${elem.text}`);
    });
  });
});
```

## 🎨 Visualization Examples

### React Flow Example

```javascript
import ReactFlow from 'reactflow';

// Convert metadata to React Flow nodes
const nodes = result.pages.flatMap(page => {
  const pageNode = {
    id: page.id,
    type: 'page',
    position: { x: page.x, y: page.y },
    data: { label: page.label, url: page.metadata.url }
  };
  
  const elementNodes = page.metadata.key_elements.map((elem, i) => ({
    id: elem.id,
    type: elem.type,
    position: { x: page.x + 50, y: page.y + 100 + (i * 80) },
    data: { label: elem.text || elem.type }
  }));
  
  return [pageNode, ...elementNodes];
});

// Create edges
const edges = result.pages.flatMap(page =>
  page.metadata.key_elements.map(elem => ({
    id: `${page.id}-${elem.id}`,
    source: page.id,
    target: elem.id
  }))
);

<ReactFlow nodes={nodes} edges={edges} />
```

### D3.js Example

```javascript
import * as d3 from 'd3';

// Create force-directed graph
const nodes = result.pages.flatMap(page => ({
  id: page.id,
  label: page.label,
  type: 'page',
  metadata: page.metadata
}));

const links = result.pages.flatMap(page =>
  page.metadata.key_elements.map(elem => ({
    source: page.id,
    target: elem.id
  }))
);

const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id))
  .force('charge', d3.forceManyBody())
  .force('center', d3.forceCenter(400, 300));
```

## 📌 Best Practices

1. **Enable Metadata Extraction**
   - Agent automatically extracts metadata when using `playwright_get_page_metadata`
   - Include metadata extraction in test case descriptions

2. **Filter Elements**
   - Filter by `type` to get specific elements (links, buttons, inputs)
   - Use `href` to identify navigation elements
   - Check `input_type` for different input fields

3. **Build Relationships**
   - Use `depends_on` array for element dependencies (future feature)
   - Track element interactions with page hierarchy

4. **Visualization**
   - Use `x`, `y` coordinates for node positioning
   - Page nodes offset horizontally (x += 300 per page)
   - Element nodes positioned relative to parent page

5. **Performance**
   - Metadata extraction adds minimal overhead
   - Only key elements (interacted with) are extracted
   - Consider `max_iterations` for complex pages

## ⚠️ Limitations

- Only elements that the agent interacts with are captured
- Text content is truncated to 200 characters
- HTML content is truncated to 300 characters
- Maximum metadata extraction depends on `max_iterations` setting
- Metadata parsing relies on agent output format

## 🔄 Workflow Integration

### Complete Flow with Metadata

```
1. Test Case Definition
   ↓
2. POST /generate-prompt
   → Generated Prompt
   ↓
3. POST /execute-playwright
   → Agent executes with metadata extraction
   → playwright_get_page_metadata called
   ↓
4. Response with Metadata
   → pages[] array with structured data
   ↓
5. Process & Visualize
   → Build graphs, charts, reports
```

## 📚 Related Documentation

- [Playwright API Guide](PLAYWRIGHT_API_GUIDE.md) - Complete API documentation
- [Playwright Metadata Tool](PLAYWRIGHT_METADATA_TOOL.md) - Tool documentation
- [API Quick Reference](PLAYWRIGHT_API_QUICK_REF.md) - Quick commands

## ✅ Summary

**New Features:**
- ✅ Automatic metadata extraction during automation
- ✅ Structured JSON format with pages and elements
- ✅ Element attributes: type, tag, text, id, class, href, input_type
- ✅ Page coordinates for visualization
- ✅ Ready for graph visualization libraries

**Response Fields:**
- `pages[]` - Array of PageNode objects
- `metadata.url` - Page URL
- `metadata.title` - Page title  
- `metadata.key_elements[]` - Extracted elements

**Element Types:**
- link, button, input, form, select, textarea, and more

The metadata extraction feature provides comprehensive page and element information for test analysis, visualization, and reporting! 🎉
