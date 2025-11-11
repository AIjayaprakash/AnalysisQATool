# LLMOps FastAPI Service Guide

Complete guide for the LLMOps REST API service.

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd backend/app
python llmops_api.py
```

The server will start on `http://localhost:8000`

### 2. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test the API

```bash
python test_llmops_api.py
```

---

## 📋 API Endpoints

### Health & Configuration

#### 1. **GET /** - Root Endpoint
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "LLMOps Test Case Processing API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### 2. **GET /health** - Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-11T10:30:00",
  "provider": "groq",
  "model": "llama-3.3-70b-versatile"
}
```

#### 3. **GET /config** - Get Configuration
```bash
curl http://localhost:8000/config
```

**Response:**
```json
{
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "temperature": 0.3,
  "use_groq": true
}
```

#### 4. **GET /providers** - List Available Providers
```bash
curl http://localhost:8000/providers
```

**Response:**
```json
{
  "current_provider": "groq",
  "providers": {
    "groq": {
      "available": true,
      "model": "llama-3.3-70b-versatile",
      "temperature": 0.3
    },
    "openai": {
      "available": true,
      "model": "gpt-4o",
      "temperature": 0.3,
      "custom_gateway": true
    }
  }
}
```

#### 5. **POST /change-provider** - Change LLM Provider
```bash
curl -X POST "http://localhost:8000/change-provider?provider=groq"
```

**Response:**
```json
{
  "message": "Provider changed to groq",
  "current_provider": "groq",
  "model": "llama-3.3-70b-versatile"
}
```

---

### Test Case Processing

#### 6. **POST /generate-prompt** - Generate Single Prompt

Generate a Playwright prompt for a single test case.

```bash
curl -X POST "http://localhost:8000/generate-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TC001",
    "module": "Login",
    "functionality": "User Authentication",
    "description": "Verify user can login with valid credentials",
    "steps": "1. Navigate to login\n2. Enter credentials\n3. Click login",
    "expected_result": "User should be logged in",
    "priority": "High"
  }'
```

**Response:**
```json
{
  "test_id": "TC001",
  "module": "Login",
  "functionality": "User Authentication",
  "description": "Verify user can login with valid credentials",
  "generated_prompt": "1. Navigate to the login page...",
  "generated_at": "2025-11-11T10:30:00"
}
```

#### 7. **POST /generate-prompts-batch** - Generate Batch Prompts

Generate prompts for multiple test cases.

```bash
curl -X POST "http://localhost:8000/generate-prompts-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": [
      {
        "test_id": "TC001",
        "module": "Login",
        "functionality": "User Authentication",
        "description": "Verify user can login with valid credentials",
        "priority": "High"
      },
      {
        "test_id": "TC002",
        "module": "Dashboard",
        "functionality": "View Dashboard",
        "description": "Verify user can view dashboard after login",
        "priority": "Medium"
      }
    ]
  }'
```

**Response:**
```json
{
  "total": 2,
  "prompts": [
    {
      "test_id": "TC001",
      "module": "Login",
      "functionality": "User Authentication",
      "description": "Verify user can login with valid credentials",
      "generated_prompt": "1. Navigate to...",
      "generated_at": "2025-11-11T10:30:00"
    },
    {
      "test_id": "TC002",
      "module": "Dashboard",
      "functionality": "View Dashboard",
      "description": "Verify user can view dashboard after login",
      "generated_prompt": "1. After successful login...",
      "generated_at": "2025-11-11T10:30:01"
    }
  ]
}
```

---

### Excel Processing

#### 8. **POST /upload-excel** - Upload Excel and Process

Upload an Excel file with test cases and generate prompts.

```bash
curl -X POST "http://localhost:8000/upload-excel?sheet_name=Sheet1" \
  -F "file=@test_cases.xlsx"
```

**Response:**
```json
{
  "filename": "test_cases.xlsx",
  "sheet_name": "Sheet1",
  "total_test_cases": 5,
  "prompts": [
    {
      "test_id": "TC001",
      "module": "Login",
      "functionality": "User Authentication",
      "description": "Verify user can login with valid credentials",
      "generated_prompt": "1. Navigate to...",
      "generated_at": "2025-11-11T10:30:00"
    }
    // ... more prompts
  ]
}
```

#### 9. **POST /read-excel** - Read Excel Without Processing

Read test cases from Excel without generating prompts.

```bash
curl -X POST "http://localhost:8000/read-excel?sheet_name=Sheet1" \
  -F "file=@test_cases.xlsx"
```

**Response:**
```json
{
  "filename": "test_cases.xlsx",
  "sheet_name": "Sheet1",
  "total_test_cases": 5,
  "test_cases": [
    {
      "test_id": "TC001",
      "module": "Login",
      "functionality": "User Authentication",
      "description": "Verify user can login with valid credentials",
      "steps": "1. Navigate...",
      "expected_result": "User logged in",
      "priority": "High",
      "status": "pending"
    }
    // ... more test cases
  ]
}
```

---

## 🐍 Python Client Examples

### Example 1: Generate Single Prompt

```python
import requests

url = "http://localhost:8000/generate-prompt"
data = {
    "test_id": "TC001",
    "module": "Login",
    "functionality": "User Authentication",
    "description": "Verify user can login with valid credentials",
    "priority": "High"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Generated Prompt: {result['generated_prompt']}")
```

### Example 2: Upload Excel File

```python
import requests

url = "http://localhost:8000/upload-excel"
files = {'file': open('test_cases.xlsx', 'rb')}
params = {'sheet_name': 'Sheet1'}

response = requests.post(url, files=files, params=params)
result = response.json()

print(f"Processed {result['total_test_cases']} test cases")
for prompt in result['prompts']:
    print(f"{prompt['test_id']}: {prompt['generated_prompt'][:100]}...")
```

### Example 3: Batch Processing

```python
import requests

url = "http://localhost:8000/generate-prompts-batch"
data = {
    "test_cases": [
        {
            "test_id": "TC001",
            "module": "Login",
            "functionality": "Login",
            "description": "Test login functionality"
        },
        {
            "test_id": "TC002",
            "module": "Dashboard",
            "functionality": "View",
            "description": "Test dashboard view"
        }
    ]
}

response = requests.post(url, json=data)
result = response.json()

print(f"Generated {result['total']} prompts")
```

### Example 4: Change Provider

```python
import requests

# Switch to Groq
response = requests.post("http://localhost:8000/change-provider?provider=groq")
print(response.json())

# Switch to OpenAI
response = requests.post("http://localhost:8000/change-provider?provider=openai")
print(response.json())
```

---

## 🌐 JavaScript/Frontend Examples

### Example 1: Fetch API

```javascript
// Generate single prompt
async function generatePrompt(testCase) {
  const response = await fetch('http://localhost:8000/generate-prompt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(testCase)
  });
  
  const result = await response.json();
  return result;
}

// Usage
const testCase = {
  test_id: "TC001",
  module: "Login",
  functionality: "User Authentication",
  description: "Verify user can login with valid credentials",
  priority: "High"
};

generatePrompt(testCase).then(result => {
  console.log('Generated:', result.generated_prompt);
});
```

### Example 2: Upload Excel with FormData

```javascript
async function uploadExcel(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/upload-excel?sheet_name=Sheet1', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  return result;
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await uploadExcel(file);
  console.log(`Processed ${result.total_test_cases} test cases`);
});
```

---

## 🔧 Environment Configuration

Set environment variables before starting the server:

```bash
# For Groq
set USE_GROQ=true
set GROQ_API_KEY=your-groq-api-key

# For OpenAI/Custom Gateway
set USE_GROQ=false
set CUSTOM_OPENAI_KEY=your-key
set CUSTOM_OPENAI_BASE_URL=https://gateway.ai-npe.humana.com/openai/deployments/gpt-4o
```

---

## 🚀 Production Deployment

### Using Uvicorn

```bash
uvicorn llmops_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn

```bash
gunicorn llmops_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "llmops_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t llmops-api .
docker run -p 8000:8000 -e USE_GROQ=true -e GROQ_API_KEY=your-key llmops-api
```

---

## 📊 API Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (Invalid input) |
| 404 | Not Found (Test case not found) |
| 500 | Internal Server Error |

---

## 🧪 Testing

Run the test suite:

```bash
# Start the server first
python llmops_api.py

# In another terminal
python test_llmops_api.py
```

---

## 📝 Excel Format

Expected Excel columns:

| Column | Required | Description |
|--------|----------|-------------|
| Test ID | ✓ | Unique identifier |
| Module | ✓ | Module name |
| Functionality | ✓ | Feature being tested |
| Description | ✓ | Test description |
| Steps | - | Test steps |
| Expected Result | - | Expected outcome |
| Priority | - | Test priority |

---

## 🔒 Security Notes

For production deployment:
1. Add authentication (JWT, OAuth)
2. Add rate limiting
3. Validate file uploads
4. Use HTTPS
5. Implement CORS properly
6. Add input sanitization

---

## 🎉 Summary

The LLMOps API provides:
- ✅ REST endpoints for all LLMOps functionality
- ✅ Excel file upload and processing
- ✅ Single and batch prompt generation
- ✅ Provider management (Groq/OpenAI)
- ✅ Interactive API documentation
- ✅ Easy integration with any client

Access the interactive docs at `http://localhost:8000/docs` for more details!
