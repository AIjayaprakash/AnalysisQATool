# 🎯 Playwright API - Quick Reference

## 🚀 Start Server
```bash
cd "e:\Kirsh Naik Academy\SeleniumMCPFlow"
python backend/app/llmops_api.py
```
Server: http://localhost:8000  
Docs: http://localhost:8000/docs

---

## 📍 New Endpoints

### 1️⃣ Execute Playwright Automation
```
POST /execute-playwright
```

**Request:**
```json
{
  "test_id": "TC_001",
  "generated_prompt": "Navigate to site...",
  "browser_type": "chromium",
  "headless": false,
  "max_iterations": 10
}
```

**Response:**
```json
{
  "test_id": "TC_001",
  "status": "success",
  "execution_time": 12.5,
  "steps_executed": 8,
  "screenshots": ["step1.png"],
  "executed_at": "2025-11-18T10:30:00"
}
```

---

### 2️⃣ Combined Endpoint (Generate + Execute)
```
POST /execute-playwright-from-testcase
```

**Request:**
```json
{
  "test_id": "TC_001",
  "module": "Authentication",
  "functionality": "Login",
  "description": "Test login flow",
  "steps": "1. Open page\n2. Login\n3. Verify"
}
```

**Response:** Same as execute-playwright

---

## 🔄 Workflow Options

### Option A: Two-Step (Review Prompt)
```python
# 1. Generate prompt
prompt = requests.post("/generate-prompt", json=test_case)
generated = prompt.json()["generated_prompt"]

# 2. Execute automation
result = requests.post("/execute-playwright", json={
    "test_id": "TC_001",
    "generated_prompt": generated
})
```

### Option B: Single-Step (Quick)
```python
result = requests.post("/execute-playwright-from-testcase", 
                      json=test_case)
```

---

## 🔧 Environment Variables

```bash
# Required
CUSTOM_OPENAI_KEY=your-key
CUSTOM_OPENAI_GATEWAY_URL=https://gateway-url
CUSTOM_OPENAI_MODEL=gpt-4o
```

---

## 📊 Status Values

- `"success"` ✅ - Automation completed
- `"failed"` ⚠️ - Completed with issues
- `"error"` ❌ - Execution error

---

## 🌐 Browser Options

- **chromium** (default)
- **firefox**
- **webkit**

Modes:
- `headless: false` - Visible (debugging)
- `headless: true` - Background (CI/CD)

---

## 📝 Complete Example

```python
import requests

BASE = "http://localhost:8000"

# Test case
test = {
    "test_id": "TC_001",
    "module": "Login",
    "functionality": "Auth",
    "description": "Test login"
}

# Execute
response = requests.post(
    f"{BASE}/execute-playwright-from-testcase",
    json=test
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Time: {result['execution_time']}s")
```

---

## 📚 All Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /generate-prompt | POST | Generate Playwright prompt |
| /execute-playwright | POST | Execute with prompt |
| /execute-playwright-from-testcase | POST | Generate + Execute |
| /generate-prompts-batch | POST | Batch prompt generation |
| /upload-excel | POST | Upload test cases |
| /process-excel | POST | Process Excel file |
| /health | GET | Health check |
| /config | GET | LLM configuration |

---

## ✅ Features

✅ Playwright automation with LangGraph  
✅ Visual browser execution  
✅ Screenshot capture  
✅ Multiple browser support  
✅ Generated prompt from test cases  
✅ Single or two-step workflow  
✅ Detailed execution results  

---

## 🎓 Tips

1. **Use two-step for production** (review prompts)
2. **Keep browser visible** during development
3. **Increase max_iterations** for complex flows
4. **Check screenshots array** for captured images
5. **Handle errors** with try-catch blocks
