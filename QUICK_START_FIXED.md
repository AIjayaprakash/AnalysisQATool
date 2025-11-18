# Quick Start Guide - Playwright Agent with OpenAI/Groq

## ✅ FIXED: No More Custom LLM Connection Errors

The agent now uses standard OpenAI or Groq providers instead of custom gateway.

## 🚀 Setup (3 Steps)

### Step 1: Create `.env` file

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 2: Add Your API Key

Edit `.env` and add your API key:

**For OpenAI:**
```bash
USE_GROQ=false
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**For Groq (Free & Fast):**
```bash
USE_GROQ=true
GROQ_API_KEY=gsk-your-actual-groq-key-here
```

### Step 3: Run the Test

```bash
cd "backend\app"
python test_agent_providers.py
```

## 🧪 Test the API

### 1. Start the Server

```bash
cd "backend\app"
python llmops_api.py
```

### 2. Test Playwright Execution

**Windows PowerShell:**
```powershell
$body = @{
    test_id = "TC_001"
    generated_prompt = "1) Navigate to https://example.com`n2) Take screenshot`n3) Close browser"
    browser_type = "edge"
    headless = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/execute-playwright" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/execute-playwright" \
  -H "Content-Type: application/json" \
  -d "{
    \"test_id\": \"TC_001\",
    \"generated_prompt\": \"1) Navigate to https://example.com\\n2) Take screenshot\\n3) Close browser\",
    \"browser_type\": \"edge\",
    \"headless\": false
  }"
```

## 📊 What Changed

| Before | After |
|--------|-------|
| ❌ CustomOpenAILLM (connection errors) | ✅ OpenAI or Groq providers |
| ❌ Hardcoded custom gateway | ✅ Standard LangChain ChatOpenAI/ChatGroq |
| ❌ Required CUSTOM_OPENAI_KEY | ✅ Use OPENAI_API_KEY or GROQ_API_KEY |
| ❌ Connection error failures | ✅ Reliable standard API calls |

## 🎯 Expected Output

```
[INFO] Using OpenAIProvider with model: gpt-4o
[INFO] Playwright Agent initialized with 10 tools

[🎭 PLAYWRIGHT] Starting automation test
[TOOL] playwright_navigate -> Success
[TOOL] playwright_get_page_metadata -> Success
[TOOL] playwright_screenshot -> Success
[TOOL] playwright_close_browser -> Success

✅ Test PASSED - Agent works correctly with OpenAI/Groq!
```

## 🔧 Troubleshooting

### Issue: "API key not found"
**Solution:** Check your `.env` file has the correct API key:
```bash
# For OpenAI
OPENAI_API_KEY=sk-...

# For Groq
GROQ_API_KEY=gsk-...
```

### Issue: "Module not found"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Still getting "Custom OpenAI LLM error"
**Solution:** Make sure you're using the updated code. Verify:
```bash
cd backend/app
python -c "from llmops import PlaywrightAgent; print('✅ Updated code loaded')"
```

## 🎓 Getting API Keys

### OpenAI (Paid)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy key starting with `sk-`

### Groq (Free & Fast)
1. Go to https://console.groq.com/keys
2. Create new API key
3. Copy key starting with `gsk-`

**Recommendation:** Start with Groq - it's free and fast for testing!

## 📖 More Information

- Full migration details: `PLAYWRIGHT_PROVIDER_MIGRATION.md`
- API documentation: `http://localhost:8000/docs` (when server is running)
- Test script: `backend/app/test_agent_providers.py`
