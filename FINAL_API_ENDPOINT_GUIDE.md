# 🎯 Final Combined API Endpoint

## Overview
The **`/execute-from-excel`** endpoint is a complete end-to-end automation solution that combines ALL steps in a single API call.

## What It Does

### Complete Workflow (6 Steps):
1. ✅ **Read Excel file** - Uploads and parses test cases from Excel
2. ✅ **Select test case** - Uses specified test_id or first test case
3. ✅ **Generate prompt** - Creates Playwright automation prompt using LLM
4. ✅ **Execute automation** - Runs Playwright with specified browser
5. ✅ **Extract metadata** - Captures page structure and elements
6. ✅ **Return JSON** - Returns structured nodes and edges

## API Endpoint

```
POST /execute-from-excel
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | ✅ Yes | - | Excel file (.xlsx or .xls) with test cases |
| `sheet_name` | String | No | "Sheet1" | Name of the Excel sheet to read |
| `test_id` | String | No | null | Specific test ID to execute (uses first test if null) |
| `browser_type` | String | No | "chromium" | Browser: chromium, firefox, webkit, or edge |
| `headless` | Boolean | No | false | Run browser in headless mode |
| `max_iterations` | Integer | No | 10 | Maximum automation iterations |

### Response Format

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
            "href": "https://www.iana.org/domains/example",
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
      "label": "Navigate to About"
    }
  ]
}
```

## Usage Examples

### Example 1: Basic Usage (First Test Case, Chromium)
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx"
```

### Example 2: Specific Test Case with Edge Browser
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "sheet_name=Sheet1" \
     -F "test_id=TC_001" \
     -F "browser_type=edge" \
     -F "headless=false"
```

### Example 3: Firefox Headless Mode
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "test_id=TC_LOGIN_001" \
     -F "browser_type=firefox" \
     -F "headless=true" \
     -F "max_iterations=15"
```

### Example 4: Python Requests
```python
import requests

url = "http://localhost:8000/execute-from-excel"

# Open Excel file
with open("test_cases.xlsx", "rb") as f:
    files = {"file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    
    data = {
        "sheet_name": "Sheet1",
        "test_id": "TC_001",
        "browser_type": "edge",
        "headless": False,
        "max_iterations": 10
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Pages extracted: {len(result['pages'])}")
        print(f"Edges extracted: {len(result['edges'])}")
    else:
        print(f"Error: {response.text}")
```

### Example 5: JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('sheet_name', 'Sheet1');
formData.append('test_id', 'TC_001');
formData.append('browser_type', 'edge');
formData.append('headless', 'false');
formData.append('max_iterations', '10');

fetch('http://localhost:8000/execute-from-excel', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Pages:', data.pages);
    console.log('Edges:', data.edges);
})
.catch(error => console.error('Error:', error));
```

## Excel File Format

Your Excel file should have these columns:

| Column | Description | Required |
|--------|-------------|----------|
| TestCaseID | Unique test identifier | ✅ Yes |
| Module | Module name | ✅ Yes |
| Functionality | Feature being tested | ✅ Yes |
| Description | Test description | ✅ Yes |
| Steps | Test steps (optional) | No |
| ExpectedResult | Expected outcome (optional) | No |
| Priority | High/Medium/Low | No |

### Example Excel Content:
```
TestCaseID   | Module  | Functionality | Description              | Priority
TC_LOGIN_001 | Auth    | Login         | Verify user can login   | High
TC_SEARCH_01 | Search  | Search        | Search for products     | Medium
```

## Response Structure

### Pages Array
Each page node contains:
- `id`: Unique page identifier (page_1, page_2, etc.)
- `label`: Display label with title and domain
- `x`, `y`: Coordinates for graph visualization
- `metadata`: Page details including:
  - `url`: Page URL
  - `title`: Page title
  - `key_elements`: Array of interactive elements

### Key Elements
Each element contains:
- `id`: Element identifier
- `type`: Element type (link, button, input, etc.)
- `tag`: HTML tag name
- `text`: Element text content
- `href`: Link URL (for links)
- `input_type`: Input type (for inputs)
- `depends_on`: Element dependencies

### Edges Array
Each edge represents navigation:
- `source`: Source page ID
- `target`: Target page ID
- `label`: Action description

## Supported Browsers

| Browser | Value | Notes |
|---------|-------|-------|
| Chromium | `chromium` | Default, fast and reliable |
| Firefox | `firefox` | Good for cross-browser testing |
| WebKit | `webkit` | Safari engine |
| Edge | `edge` | Microsoft Edge (Chromium-based) |

## Error Handling

### Common Errors:

**400 Bad Request**
```json
{
  "detail": "File must be an Excel file (.xlsx or .xls)"
}
```
Solution: Upload a valid Excel file

**404 Not Found**
```json
{
  "detail": "Test case with ID 'TC_999' not found"
}
```
Solution: Use a valid test_id from your Excel file

**500 Internal Server Error**
```json
{
  "detail": "Error in complete automation: Failed to generate Playwright prompt"
}
```
Solution: Check Excel file format and LLM configuration

## Logging

The endpoint logs detailed information at each step:

```
Step 1: Saving Excel file
Step 2: Reading test cases from Excel
Step 3: Selected test case by ID: TC_001
Step 4: Generating Playwright prompt
Step 5: Executing Playwright automation with edge browser
Step 6: Extracting structured metadata (nodes and edges)
```

Check logs for debugging: `logs/llmops.log`

## Comparison with Other Endpoints

| Endpoint | What It Does | Use When |
|----------|-------------|----------|
| `/upload-excel` | Upload Excel only | Need to store file |
| `/read-excel` | Read test cases | Need test case list |
| `/generate-prompt` | Generate prompt | Manual prompt creation |
| `/execute-playwright` | Execute automation | Have prompt ready |
| `/execute-playwright-metadata` | Execute + metadata | Have prompt ready |
| `/execute-playwright-from-testcase` | Prompt + automation | Have test case object |
| **`/execute-from-excel`** | **EVERYTHING** | **One-click automation** ✅ |

## Benefits

✅ **Single API Call** - No need to chain multiple endpoints
✅ **Complete Workflow** - Excel → Prompt → Automation → JSON
✅ **Dynamic Browser** - Choose browser per execution
✅ **Clean Output** - Only structured nodes and edges
✅ **Flexible** - Execute any test case from Excel
✅ **Production Ready** - Full error handling and logging

## Testing the Endpoint

### 1. Start the Server
```bash
cd backend/app
python llmops_api.py
```

### 2. Test with Swagger UI
Open: http://localhost:8000/docs
Navigate to: **Complete Automation** → `/execute-from-excel`
Click: **Try it out**

### 3. Upload Excel and Execute
- Choose your Excel file
- Set parameters (sheet_name, test_id, browser_type)
- Click **Execute**
- View the JSON response

### 4. Verify Results
Check the response for:
- `pages` array with extracted metadata
- `edges` array with page connections
- Element details with types and attributes

## Next Steps

1. **Test with your Excel file** - Upload your test cases
2. **Try different browsers** - Test with edge, firefox, chromium
3. **Check the output** - Verify nodes and edges structure
4. **Integrate into workflow** - Use in your automation pipeline
5. **Visualize results** - Use pages/edges data in frontend

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review logs: `logs/llmops.log`
- Check browser installation: `python -m playwright install`
