# 🎭 Playwright Automation API Documentation

## Overview

FastAPI endpoints for automated Playwright test execution based on generated prompts from test cases.

## Base URL
```
http://localhost:8000
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🆕 New Endpoints

### 1. Execute Playwright Automation
**Endpoint:** `POST /execute-playwright`

Execute Playwright automation using a generated prompt.

#### Request Body
```json
{
  "test_id": "TC_001",
  "generated_prompt": "Navigate to https://example.com and verify the login functionality...",
  "browser_type": "chromium",
  "headless": false,
  "max_iterations": 10
}
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| test_id | string | ✅ Yes | - | Test case identifier |
| generated_prompt | string | ✅ Yes | - | Generated prompt from `/generate-prompt` |
| browser_type | string | No | "chromium" | Browser: chromium, firefox, webkit |
| headless | boolean | No | false | Run browser in headless mode |
| max_iterations | integer | No | 10 | Maximum automation steps |

#### Response
```json
{
  "test_id": "TC_001",
  "status": "success",
  "execution_time": 12.5,
  "steps_executed": 8,
  "agent_output": "Automation completed successfully. Navigated to site, performed login...",
  "screenshots": ["step1.png", "step2.png"],
  "error_message": null,
  "executed_at": "2025-11-18T10:30:00"
}
```

#### Status Values
- `"success"` - Automation completed successfully
- `"failed"` - Automation completed with issues
- `"error"` - Execution error occurred

#### Example (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/execute-playwright",
    json={
        "test_id": "TC_001",
        "generated_prompt": "Navigate to https://example.com...",
        "browser_type": "chromium",
        "headless": False
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Time: {result['execution_time']}s")
```

#### Example (cURL)
```bash
curl -X POST "http://localhost:8000/execute-playwright" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TC_001",
    "generated_prompt": "Navigate to https://example.com and click login",
    "browser_type": "chromium",
    "headless": false,
    "max_iterations": 10
  }'
```

---

### 2. Execute Playwright from Test Case (Combined)
**Endpoint:** `POST /execute-playwright-from-testcase`

Combined endpoint: Generates prompt AND executes automation in one call.

#### Request Body
```json
{
  "test_id": "TC_001",
  "module": "Authentication",
  "functionality": "User Login",
  "description": "Verify user can login with valid credentials",
  "steps": "1. Navigate to login page\n2. Enter username\n3. Enter password\n4. Click login",
  "expected_result": "User logged in successfully",
  "priority": "High"
}
```

#### Parameters
Same as `/generate-prompt` endpoint (TestCaseRequest model)

#### Response
Same as `/execute-playwright` endpoint (PlaywrightExecutionResponse)

#### Example (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/execute-playwright-from-testcase",
    json={
        "test_id": "TC_001",
        "module": "Authentication",
        "functionality": "Login",
        "description": "Test login functionality",
        "steps": "1. Open login page\n2. Enter credentials\n3. Submit"
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Steps: {result['steps_executed']}")
```

---

## 📊 Workflow Options

### Option 1: Two-Step Workflow (Recommended for Review)

**Step 1:** Generate Prompt
```python
# Generate prompt from test case
prompt_response = requests.post(
    "http://localhost:8000/generate-prompt",
    json={
        "test_id": "TC_001",
        "module": "Login",
        "functionality": "User Authentication",
        "description": "Verify login works"
    }
)
generated_prompt = prompt_response.json()["generated_prompt"]

# Review the generated prompt here if needed
print(f"Generated Prompt: {generated_prompt}")
```

**Step 2:** Execute Automation
```python
# Execute automation with the prompt
exec_response = requests.post(
    "http://localhost:8000/execute-playwright",
    json={
        "test_id": "TC_001",
        "generated_prompt": generated_prompt,
        "browser_type": "chromium"
    }
)
result = exec_response.json()
```

**Benefits:**
- ✅ Review generated prompt before execution
- ✅ Modify prompt if needed
- ✅ Reuse same prompt multiple times
- ✅ Better debugging

---

### Option 2: Single-Step Workflow (Quick Automation)

```python
# Generate and execute in one call
response = requests.post(
    "http://localhost:8000/execute-playwright-from-testcase",
    json={
        "test_id": "TC_001",
        "module": "Login",
        "functionality": "User Authentication",
        "description": "Verify login works"
    }
)
result = response.json()
```

**Benefits:**
- ✅ Faster for quick tests
- ✅ Less code
- ✅ Automatic end-to-end flow

---

## 🔧 Environment Variables

Required for Playwright automation:

```bash
# Custom OpenAI Gateway (Required)
CUSTOM_OPENAI_KEY=your-api-key-here
CUSTOM_OPENAI_GATEWAY_URL=https://gateway.ai-npe.humana.com/openai/deployments
CUSTOM_OPENAI_MODEL=gpt-4o

# Alternative headers (if needed)
AI_GATEWAY_VERSION=2024-08-01-preview
```

---

## 🎯 Complete Usage Examples

### Example 1: Login Test Automation

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Generate prompt
prompt_response = requests.post(
    f"{BASE_URL}/generate-prompt",
    json={
        "test_id": "TC_LOGIN_001",
        "module": "Authentication",
        "functionality": "User Login",
        "description": "Verify user can login with valid credentials",
        "steps": """
            1. Navigate to https://example.com/login
            2. Enter username: testuser@example.com
            3. Enter password: Test123!
            4. Click 'Login' button
            5. Verify dashboard is displayed
        """,
        "expected_result": "User successfully logged in and dashboard visible",
        "priority": "High"
    }
)

generated_prompt = prompt_response.json()["generated_prompt"]
print(f"Generated Prompt:\n{generated_prompt}\n")

# Step 2: Execute automation
exec_response = requests.post(
    f"{BASE_URL}/execute-playwright",
    json={
        "test_id": "TC_LOGIN_001",
        "generated_prompt": generated_prompt,
        "browser_type": "chromium",
        "headless": False,
        "max_iterations": 15
    }
)

result = exec_response.json()
print(f"✅ Status: {result['status']}")
print(f"⏱️  Execution Time: {result['execution_time']}s")
print(f"📊 Steps: {result['steps_executed']}")
print(f"📸 Screenshots: {result['screenshots']}")
```

### Example 2: Form Submission Test

```python
# Single-step execution
response = requests.post(
    f"{BASE_URL}/execute-playwright-from-testcase",
    json={
        "test_id": "TC_FORM_001",
        "module": "Contact Form",
        "functionality": "Form Submission",
        "description": "Test contact form submission",
        "steps": """
            1. Go to https://example.com/contact
            2. Fill in name: John Doe
            3. Fill in email: john@example.com
            4. Fill in message: Test message
            5. Click Submit
            6. Verify success message
        """,
        "expected_result": "Form submitted successfully with confirmation"
    }
)

result = response.json()
if result['status'] == 'success':
    print("✅ Form submission test passed!")
else:
    print(f"❌ Test failed: {result['error_message']}")
```

### Example 3: Batch Test Execution

```python
test_cases = [
    {
        "test_id": "TC_001",
        "module": "Login",
        "functionality": "Authentication",
        "description": "Test login"
    },
    {
        "test_id": "TC_002",
        "module": "Search",
        "functionality": "Product Search",
        "description": "Test search feature"
    },
    {
        "test_id": "TC_003",
        "module": "Cart",
        "functionality": "Add to Cart",
        "description": "Test adding items to cart"
    }
]

results = []
for test in test_cases:
    try:
        response = requests.post(
            f"{BASE_URL}/execute-playwright-from-testcase",
            json=test
        )
        results.append(response.json())
        print(f"✅ {test['test_id']}: {response.json()['status']}")
    except Exception as e:
        print(f"❌ {test['test_id']}: Failed - {str(e)}")

# Summary
success_count = sum(1 for r in results if r['status'] == 'success')
print(f"\n📊 Summary: {success_count}/{len(test_cases)} tests passed")
```

---

## 🚀 Starting the API

```bash
# Navigate to project directory
cd "e:\Kirsh Naik Academy\SeleniumMCPFlow"

# Set environment variables (Windows)
set CUSTOM_OPENAI_KEY=your-key-here
set CUSTOM_OPENAI_GATEWAY_URL=your-gateway-url
set CUSTOM_OPENAI_MODEL=gpt-4o

# Start API server
python backend/app/llmops_api.py
```

**Server will start on:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

---

## 📋 Response Model Details

### PlaywrightExecutionResponse

| Field | Type | Description |
|-------|------|-------------|
| test_id | string | Test case identifier |
| status | string | "success", "failed", or "error" |
| execution_time | float | Time taken in seconds |
| steps_executed | integer | Number of automation steps |
| agent_output | string | Detailed output from agent |
| screenshots | array[string] | List of screenshot filenames |
| error_message | string \| null | Error details if failed |
| executed_at | string | ISO timestamp of execution |

---

## 🔍 Browser Options

### Supported Browsers
- **chromium** (Default) - Google Chrome/Chromium
- **firefox** - Mozilla Firefox
- **webkit** - Safari (WebKit)

### Headless Mode
- `headless: false` - Visible browser window (default, recommended for debugging)
- `headless: true` - Background execution (faster, no GUI)

---

## ⚠️ Error Handling

### Common Errors

**1. Missing API Key**
```json
{
  "detail": "CUSTOM_OPENAI_KEY environment variable not set"
}
```
**Solution:** Set the environment variable before starting API

**2. Prompt Generation Failed**
```json
{
  "status": "error",
  "error_message": "Failed to generate prompt"
}
```
**Solution:** Check test case data is complete

**3. Browser Timeout**
```json
{
  "status": "failed",
  "error_message": "Timeout waiting for selector"
}
```
**Solution:** Increase max_iterations or check target website availability

---

## 🎓 Best Practices

1. **Review Prompts First**
   - Use two-step workflow for production
   - Review generated prompts before execution

2. **Set Appropriate Timeouts**
   - Use higher `max_iterations` for complex flows
   - Default 10 is good for simple tests

3. **Use Visible Browser**
   - Keep `headless: false` during development
   - Switch to `headless: true` for CI/CD

4. **Handle Screenshots**
   - Screenshots saved in working directory
   - Check `screenshots` array in response

5. **Batch Execution**
   - Add delays between tests
   - Handle exceptions properly
   - Collect results for reporting

---

## 📚 Related Endpoints

- `POST /generate-prompt` - Generate Playwright prompt from test case
- `POST /generate-prompts-batch` - Batch prompt generation
- `POST /process-excel` - Process Excel file with test cases
- `GET /health` - API health check
- `GET /config` - Get current LLM configuration

---

## 🔗 Complete Workflow Diagram

```
Test Case (JSON)
      ↓
┌─────────────────────────┐
│ POST /generate-prompt   │
└───────────┬─────────────┘
            ↓
    Generated Prompt
            ↓
┌─────────────────────────┐
│ POST /execute-playwright│
└───────────┬─────────────┘
            ↓
    Execution Results
    (status, steps, screenshots)
```

**OR**

```
Test Case (JSON)
      ↓
┌──────────────────────────────────┐
│ POST /execute-playwright-from-   │
│      testcase (Combined)          │
└───────────┬──────────────────────┘
            ↓
    Execution Results
```

---

## 📞 Support

For issues or questions:
1. Check Swagger docs: http://localhost:8000/docs
2. Review API logs in terminal
3. Verify environment variables are set
4. Check test case format matches examples

---

## ✅ Summary

**New Endpoints Added:**
1. ✅ `POST /execute-playwright` - Execute automation with generated prompt
2. ✅ `POST /execute-playwright-from-testcase` - Combined endpoint for end-to-end

**Key Features:**
- 🎭 Playwright automation with LangGraph agent
- 🔄 Two workflow options (2-step or combined)
- 📸 Automatic screenshot capture
- ⚡ Support for multiple browsers
- 🎯 Detailed execution results
- 🔧 Configurable iterations and headless mode

**Ready to use with:**
- Test cases from `/generate-prompt` API
- Excel file processing
- CI/CD pipelines
- Automated test suites
