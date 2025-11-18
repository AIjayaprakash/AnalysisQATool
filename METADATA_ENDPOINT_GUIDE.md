# Simplified Metadata Endpoint - Usage Guide

## ✅ Problem Solved

The `playwright_metadata_output.json` was showing all verbose agent logs. Now you get **only clean, structured metadata**.

## 🎯 New Endpoint: `/execute-playwright-metadata`

This endpoint returns ONLY the structured page metadata without verbose logs.

### Request

```json
POST http://localhost:8000/execute-playwright-metadata

{
    "test_id": "TC_METADATA_001",
    "generated_prompt": "1) Navigate to https://example.com\n2) Extract page metadata\n3) Close browser",
    "browser_type": "edge",
    "headless": false,
    "max_iterations": 10
}
```

### Response (Clean JSON)

```json
{
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
                        "class": null,
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

## 📊 Comparison

### Old Output (verbose)
```json
{
    "test_id": "TC_001",
    "status": "success",
    "agent_output": "{'status': 'success', 'test_prompt': '...', 'messages': [...]}",
    "screenshots": ["example.png"],
    "pages": []  // ❌ Empty!
}
```

### New Output (clean)
```json
{
    "pages": [
        {
            "id": "page_1",
            "label": "Example Domain (example.com)",
            "metadata": {
                "url": "https://example.com/",
                "title": "Example Domain",
                "key_elements": [...]
            }
        }
    ]
}
```

## 🚀 PowerShell Example

```powershell
# Step 1: Generate prompt
$testCase = @{
    test_id = "TC_001"
    module = "Login"
    functionality = "Authentication"
    description = "Test login with valid credentials"
} | ConvertTo-Json

$prompt = Invoke-RestMethod -Uri "http://localhost:8000/generate-prompt" `
    -Method Post `
    -Body $testCase `
    -ContentType "application/json"

# Step 2: Execute and get clean metadata
$execRequest = @{
    test_id = "TC_001"
    generated_prompt = $prompt.generated_prompt
    browser_type = "edge"
    headless = $false
} | ConvertTo-Json

$metadata = Invoke-RestMethod -Uri "http://localhost:8000/execute-playwright-metadata" `
    -Method Post `
    -Body $execRequest `
    -ContentType "application/json"

# Step 3: Display clean JSON
$metadata | ConvertTo-Json -Depth 10
```

## 🔧 Python Example

```python
import requests
import json

# Step 1: Generate prompt
response = requests.post("http://localhost:8000/generate-prompt", json={
    "test_id": "TC_001",
    "module": "Login",
    "functionality": "Authentication",
    "description": "Test login"
})
generated_prompt = response.json()["generated_prompt"]

# Step 2: Execute and get clean metadata
response = requests.post("http://localhost:8000/execute-playwright-metadata", json={
    "test_id": "TC_001",
    "generated_prompt": generated_prompt,
    "browser_type": "edge",
    "headless": False
})

metadata = response.json()
print(json.dumps(metadata, indent=2))

# Access the data
for page in metadata["pages"]:
    print(f"Page: {page['label']}")
    print(f"URL: {page['metadata']['url']}")
    for element in page['metadata']['key_elements']:
        print(f"  - {element['type']}: {element['text']}")
```

## 📝 Available Endpoints

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/execute-playwright` | Full execution details | Verbose output + pages |
| `/execute-playwright-metadata` | **Clean metadata only** | **Just pages array** |
| `/execute-playwright-from-testcase` | Generate + Execute | Full details |

## ✅ Benefits

1. **Clean Output**: No verbose agent logs
2. **Structured Data**: Easy to parse and use
3. **Graph-Ready**: Perfect for visualization (x, y coordinates included)
4. **Type-Safe**: Pydantic models ensure data integrity
5. **Focused**: Only what you need - page metadata and elements

## 🎯 Use Cases

- **Data Visualization**: Use `x`, `y` coordinates for graph plotting
- **Test Reports**: Extract element info for documentation
- **API Integration**: Clean JSON for downstream systems
- **Analytics**: Track page elements across test runs
- **Flow Diagrams**: Build user journey visualizations

## 🔑 Key Fields Explained

```javascript
{
    "id": "page_1",              // Unique page identifier
    "label": "Title (domain)",   // Display label for UI
    "x": 200,                    // X coordinate for graph
    "y": 100,                    // Y coordinate for graph
    "metadata": {
        "url": "...",            // Full page URL
        "title": "...",          // Page title
        "key_elements": [        // Array of interactive elements
            {
                "id": "element_1",       // Unique element ID
                "type": "link",          // Element type (link, button, input)
                "tag": "a",              // HTML tag
                "text": "...",           // Visible text
                "element_id": null,      // HTML id attribute
                "name": null,            // HTML name attribute
                "class": null,           // HTML class attribute
                "href": "...",           // Link URL (for <a> tags)
                "input_type": null,      // Input type (for <input> tags)
                "depends_on": []         // Dependencies (for flow analysis)
            }
        ]
    }
}
```

## 📄 Sample Output File

The test script creates `metadata_clean_output.json` showing the exact format you'll receive.

## 🎉 Result

Now your `playwright_metadata_output.json` will contain **only** the clean, structured metadata - exactly what you requested!
