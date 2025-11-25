# Execute From Excel Endpoint - Examples and Usage

## 📋 Overview

This directory contains comprehensive examples for using the `/execute-from-excel` endpoint in multiple programming languages and formats.

## 🎯 What the Endpoint Does

The `/execute-from-excel` endpoint performs complete end-to-end automation:

1. ✅ **Read Excel file** with test cases
2. ✅ **Generate Playwright prompt** using LLM
3. ✅ **Execute Playwright automation** with specified browser
4. ✅ **Extract structured JSON** with nodes and edges

## 📁 Available Examples

### 1. Python Examples (`test_execute_from_excel.py`)
Comprehensive Python examples using `requests` library.

**Examples included:**
- Basic usage (first test case, chromium)
- Specific test case with Edge browser
- Firefox headless mode
- Test all browsers
- Detailed metadata extraction
- Error handling
- Save results to files (JSON, TXT, CSV)

**Run:**
```bash
python examples/test_execute_from_excel.py
```

### 2. Bash/cURL Examples (`test_execute_from_excel.sh`)
Shell script examples using `curl` and `jq`.

**Examples included:**
- Basic usage
- Specific test case with Edge
- Firefox headless mode
- Save response to file
- Check status with jq
- Error handling with HTTP codes

**Run:**
```bash
chmod +x examples/test_execute_from_excel.sh
./examples/test_execute_from_excel.sh
```

### 3. Windows Batch Script (`test_execute_from_excel.bat`)
Windows command line examples.

**Examples included:**
- Basic usage
- Specific test case with Edge
- Firefox headless mode
- Save to file

**Run:**
```cmd
examples\test_execute_from_excel.bat
```

### 4. JavaScript/Node.js Examples (`test_execute_from_excel.js`)
Comprehensive Node.js examples using `axios` and `form-data`.

**Examples included:**
- Basic usage
- Specific test case with Edge
- Firefox headless mode
- Test all browsers
- Detailed metadata extraction
- Error handling

**Setup:**
```bash
npm install axios form-data
```

**Run:**
```bash
node examples/test_execute_from_excel.js
```

## 🚀 Quick Start

### Prerequisites

1. **Start API Server:**
   ```bash
   cd backend/app
   python llmops_api.py
   ```
   API will be available at: http://localhost:8000

2. **Prepare Excel File:**
   Create `test_cases.xlsx` with these columns:
   - TestCaseID
   - Module
   - Functionality
   - Description
   - Steps (optional)
   - ExpectedResult (optional)
   - Priority (optional)

3. **Install Browsers:**
   ```bash
   python -m playwright install
   ```

### Basic Usage

**cURL:**
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx"
```

**Python:**
```python
import requests

with open("test_cases.xlsx", "rb") as f:
    files = {"file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = requests.post("http://localhost:8000/execute-from-excel", files=files)
    result = response.json()
    print(f"Pages: {len(result['pages'])}")
```

## 🔧 API Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | File | Excel file (.xlsx or .xls) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sheet_name` | String | "Sheet1" | Excel sheet name |
| `test_id` | String | null | Specific test ID (uses first if null) |
| `browser_type` | String | "chromium" | Browser: chromium, firefox, webkit, edge |
| `headless` | Boolean | false | Run in headless mode |
| `max_iterations` | Integer | 10 | Maximum automation steps |

## 📤 Response Format

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
  ]
}
```

## 🌐 Browser Support

| Browser | Value | Notes |
|---------|-------|-------|
| Chromium | `chromium` | Default, fast and reliable |
| Firefox | `firefox` | Good for cross-browser testing |
| WebKit | `webkit` | Safari engine |
| Edge | `edge` | Microsoft Edge (Chromium-based) |

## 📊 Example Scenarios

### Scenario 1: Login Test with Edge
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "test_id=TC_LOGIN_001" \
     -F "browser_type=edge" \
     -F "headless=false"
```

### Scenario 2: Search Test with Firefox Headless
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "test_id=TC_SEARCH_001" \
     -F "browser_type=firefox" \
     -F "headless=true"
```

### Scenario 3: Form Test with Chromium
```bash
curl -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     -F "test_id=TC_FORM_001" \
     -F "browser_type=chromium" \
     -F "max_iterations=15"
```

## 🐛 Troubleshooting

### Issue: Connection Refused
**Solution:** Make sure API server is running:
```bash
python backend/app/llmops_api.py
```

### Issue: Browser Not Found
**Solution:** Install Playwright browsers:
```bash
python -m playwright install
```

### Issue: Test Case Not Found (404)
**Solution:** Check test_id in your Excel file:
```bash
curl -X POST "http://localhost:8000/read-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '.test_cases[].test_id'
```

### Issue: Invalid Excel File (400)
**Solution:** Ensure file is .xlsx or .xls format with correct columns.

## 📝 Excel File Template

Download template: [test_cases_template.xlsx](./test_cases_template.xlsx)

**Minimum Required Columns:**
```
| TestCaseID | Module | Functionality | Description                    |
|------------|--------|---------------|--------------------------------|
| TC_001     | Login  | Authentication| Verify user can login         |
| TC_002     | Search | Product Search| Search for products by keyword |
```

## 🔍 Viewing Results

### In Browser (Swagger UI)
1. Open: http://localhost:8000/docs
2. Navigate to: **Complete Automation** → `/execute-from-excel`
3. Click: **Try it out**
4. Upload Excel file and set parameters
5. Click: **Execute**
6. View JSON response

### With Python
```python
result = response.json()

# Print pages
for page in result['pages']:
    print(f"Page: {page['label']}")
    print(f"URL: {page['metadata']['url']}")
    print(f"Elements: {len(page['metadata']['key_elements'])}")

# Print edges
for edge in result['edges']:
    print(f"{edge['source']} → {edge['target']}: {edge['label']}")
```

### With jq (command line)
```bash
# Count pages and edges
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '{pages: (.pages|length), edges: (.edges|length)}'

# Get all URLs
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '.pages[].metadata.url'

# Get element summary
curl -s -X POST "http://localhost:8000/execute-from-excel" \
     -F "file=@test_cases.xlsx" \
     | jq '.pages[] | {url: .metadata.url, elements: (.metadata.key_elements|length)}'
```

## 💡 Tips

1. **Start with Chromium** - It's the default and most reliable
2. **Use headless=false** - See what's happening during development
3. **Increase max_iterations** - For complex multi-step tests
4. **Test one case first** - Use test_id to test specific cases
5. **Save results** - Store JSON for later analysis or visualization

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Main Guide:** [FINAL_API_ENDPOINT_GUIDE.md](../FINAL_API_ENDPOINT_GUIDE.md)
- **Dynamic Browser Guide:** [DYNAMIC_BROWSER_TYPE_IMPLEMENTATION.md](../DYNAMIC_BROWSER_TYPE_IMPLEMENTATION.md)

## 🎓 Learning Path

1. **Start Here:** Run `example_1_basic_usage()` in Python
2. **Customize:** Try different browsers and test cases
3. **Analyze:** Run `example_5_detailed_extraction()`
4. **Integrate:** Use in your automation pipeline
5. **Visualize:** Build a frontend to display pages/edges

## ✅ Checklist

Before running examples:
- [ ] API server is running (http://localhost:8000)
- [ ] Excel file exists with correct format
- [ ] Playwright browsers installed
- [ ] Dependencies installed (requests, axios, etc.)
- [ ] .env file configured with API keys

## 🤝 Support

If you encounter issues:
1. Check logs: `logs/llmops.log`
2. Verify API health: http://localhost:8000/health
3. Test Excel reading: `/read-excel` endpoint
4. Validate browser: `python -m playwright install --help`
