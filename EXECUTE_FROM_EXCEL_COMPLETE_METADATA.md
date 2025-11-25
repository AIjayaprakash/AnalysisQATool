# Execute From Excel - Complete Metadata Response

## 🎯 Updated Response Structure

The `/execute-from-excel` endpoint now returns **complete metadata** including the full agent output with all execution details.

## 📤 New Response Model: CompleteMetadataResponse

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `test_id` | string | Test case ID that was executed |
| `status` | string | Execution status: "success", "failed", or "error" |
| `execution_time` | float | Total execution time in seconds |
| `steps_executed` | int | Number of automation steps executed |
| `agent_output` | string | **Complete agent output with all tool executions and metadata** |
| `pages` | array | Parsed page nodes with structured metadata |
| `edges` | array | Navigation edges between pages |
| `screenshots` | array | List of screenshot filenames |
| `error_message` | string | Error details if execution failed (null on success) |
| `executed_at` | string | ISO 8601 timestamp of execution |

## 📋 Complete Response Example

```json
{
  "test_id": "TC_LOGIN_001",
  "status": "success",
  "execution_time": 15.43,
  "steps_executed": 8,
  "agent_output": "✅ playwright_navigate: Navigated to https://example.com\n\n📄 Page Metadata:\n  • URL: https://example.com/\n  • Title: Example Domain\n\n🎯 Element Metadata (Found 1 element(s)):\n  Element 1:\n  • Selector: a\n  • Tag: <a>\n  • Type: link\n  • Text: More information...\n  • Href: https://www.iana.org/domains/example\n  • ID: None\n  • Name: None\n  • Class: None\n\n✅ playwright_click: Clicked on element: a\n\n📄 Page Metadata:\n  • URL: https://www.iana.org/domains/example\n  • Title: IANA — IANA-managed Reserved Domains\n\n🎯 Element Metadata (Found 3 element(s)):\n  Element 1:\n  • Selector: a[href=\"/\"]\n  • Tag: <a>\n  • Type: link\n  • Text: Home\n  • Href: /\n  ...",
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
            "href": "https://www.iana.org/domains/example",
            "element_id": null,
            "name": null,
            "class_name": null,
            "input_type": null,
            "depends_on": []
          }
        ]
      }
    },
    {
      "id": "page_2",
      "label": "IANA — IANA-managed Reserved Domains (www.iana.org)",
      "x": 500,
      "y": 100,
      "metadata": {
        "url": "https://www.iana.org/domains/example",
        "title": "IANA — IANA-managed Reserved Domains",
        "key_elements": [
          {
            "id": "element_1",
            "type": "link",
            "tag": "a",
            "text": "Home",
            "href": "/",
            "element_id": null,
            "name": null,
            "class_name": null,
            "input_type": null,
            "depends_on": []
          }
        ]
      }
    }
  ],
  "edges": [
    {
      "source": "page_1",
      "target": "page_2",
      "label": "Click More information..."
    }
  ],
  "screenshots": ["screenshot_1732567890.png"],
  "error_message": null,
  "executed_at": "2025-11-25T10:30:45.123456"
}
```

## 🔑 Key Benefits

### 1. **Complete Agent Output**
The `agent_output` field contains the **full execution log** including:
- All tool calls (navigate, click, type, etc.)
- Page metadata extraction results
- Element details with selectors
- Tool execution confirmations
- Navigation flow details

### 2. **Parsed Metadata**
The `pages` and `edges` arrays provide **structured data** parsed from the agent output:
- Clean, structured page nodes
- Element metadata with types and attributes
- Navigation graph with edges

### 3. **Execution Details**
Complete execution information:
- Status (success/failed/error)
- Execution time
- Steps executed
- Screenshots captured
- Error messages (if any)

## 💻 Updated Python Example

```python
import requests

API_URL = "http://localhost:8000/execute-from-excel"

with open("test_cases.xlsx", "rb") as f:
    files = {"file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    
    data = {
        "sheet_name": "Sheet1",
        "test_id": "TC_LOGIN_001",
        "browser_type": "edge",
        "headless": False,
        "max_iterations": 10
    }
    
    response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        # Basic execution info
        print(f"✅ Status: {result['status']}")
        print(f"⏱️  Execution Time: {result['execution_time']}s")
        print(f"📊 Steps Executed: {result['steps_executed']}")
        
        # Parsed metadata
        print(f"\n📄 Pages Extracted: {len(result['pages'])}")
        print(f"🔗 Edges Extracted: {len(result['edges'])}")
        
        # Complete agent output
        print(f"\n📋 Full Agent Output:")
        print(result['agent_output'])
        
        # Page details
        for page in result['pages']:
            print(f"\n  Page: {page['label']}")
            print(f"  URL: {page['metadata']['url']}")
            print(f"  Elements: {len(page['metadata']['key_elements'])}")
            
            for elem in page['metadata']['key_elements']:
                print(f"    - {elem['type']}: {elem['text'] or elem['tag']}")
        
        # Navigation flow
        if result['edges']:
            print(f"\n🔀 Navigation Flow:")
            for edge in result['edges']:
                print(f"  {edge['source']} → {edge['target']}: {edge['label']}")
        
        # Save complete output to file
        import json
        with open("complete_automation_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Complete results saved to: complete_automation_result.json")
```

## 🔍 Accessing Different Parts of the Response

### Get Execution Status
```python
status = result['status']  # "success", "failed", or "error"
if status == "success":
    print("✅ Automation successful!")
elif status == "failed":
    print(f"❌ Automation failed: {result['error_message']}")
```

### Get Agent Output
```python
# Full output with all details
full_output = result['agent_output']

# Search for specific tool calls
if "playwright_navigate" in full_output:
    print("Navigation occurred")

# Extract specific patterns
import re
urls = re.findall(r'URL:\s*([^\n]+)', full_output)
print(f"Visited URLs: {urls}")
```

### Get Parsed Metadata
```python
# Pages
for page in result['pages']:
    print(f"Page: {page['id']}")
    print(f"  URL: {page['metadata']['url']}")
    print(f"  Title: {page['metadata']['title']}")
    print(f"  Elements: {len(page['metadata']['key_elements'])}")

# Edges
for edge in result['edges']:
    print(f"{edge['source']} → {edge['target']}: {edge['label']}")
```

### Get Element Details
```python
for page in result['pages']:
    for element in page['metadata']['key_elements']:
        print(f"Element: {element['id']}")
        print(f"  Type: {element['type']}")
        print(f"  Tag: {element['tag']}")
        print(f"  Text: {element['text']}")
        print(f"  Href: {element['href']}")
        print(f"  ID: {element['element_id']}")
        print(f"  Class: {element['class_name']}")
```

## 📊 Use Cases

### 1. **Debugging and Troubleshooting**
Use `agent_output` to see exactly what happened during execution:
```python
# Check if specific action occurred
if "playwright_click" in result['agent_output']:
    print("Click action was performed")

# Find errors
if "error" in result['agent_output'].lower():
    print("Error occurred during execution")
```

### 2. **Test Report Generation**
Use complete metadata to generate detailed reports:
```python
report = f"""
Test Case: {result['test_id']}
Status: {result['status']}
Execution Time: {result['execution_time']}s
Pages Visited: {len(result['pages'])}
Actions Performed: {result['steps_executed']}

Navigation Flow:
{chr(10).join(f"  {e['source']} → {e['target']}: {e['label']}" for e in result['edges'])}

Detailed Output:
{result['agent_output']}
"""
print(report)
```

### 3. **Data Analysis**
Parse and analyze execution data:
```python
# Count element types across all pages
element_types = {}
for page in result['pages']:
    for elem in page['metadata']['key_elements']:
        elem_type = elem['type']
        element_types[elem_type] = element_types.get(elem_type, 0) + 1

print("Element Distribution:")
for elem_type, count in element_types.items():
    print(f"  {elem_type}: {count}")
```

### 4. **Visualization**
Use pages and edges to create flow diagrams:
```python
# Export to graph visualization format
nodes = [
    {"id": page['id'], "label": page['label'], "url": page['metadata']['url']}
    for page in result['pages']
]

edges = [
    {"from": edge['source'], "to": edge['target'], "label": edge['label']}
    for edge in result['edges']
]

# Use with vis.js, D3.js, or other graph libraries
```

## 🔄 Comparison: Before vs After

### Before (SimplifiedMetadataResponse)
```json
{
  "pages": [...],
  "edges": [...]
}
```
- Only parsed metadata
- No execution details
- No agent output
- Limited debugging info

### After (CompleteMetadataResponse)
```json
{
  "test_id": "TC_001",
  "status": "success",
  "execution_time": 15.43,
  "steps_executed": 8,
  "agent_output": "Full execution log...",
  "pages": [...],
  "edges": [...],
  "screenshots": [...],
  "error_message": null,
  "executed_at": "2025-11-25T10:30:45"
}
```
- Complete execution details
- Full agent output for debugging
- Parsed metadata
- Status and error handling
- Timestamps and metrics

## 🚀 Quick Start

```bash
# Start the server
cd backend/app
python llmops_api.py

# Test the endpoint
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "browser_type=edge" \
     | jq '.'

# Get only agent output
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '.agent_output'

# Get only parsed pages
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '.pages'

# Check execution status
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '{status: .status, time: .execution_time, pages: (.pages|length)}'
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Endpoint**: `/execute-from-excel`
- **Method**: POST
- **Response Model**: `CompleteMetadataResponse`
- **Tag**: Complete Automation
