# Playwright Agent - OpenAI/Groq Provider Migration

## 🎯 Summary

Successfully migrated `PlaywrightAgent` from using `CustomOpenAILLM` to standard OpenAI/Groq providers.

## ❌ Previous Issue

The agent was using `CustomOpenAILLM` which caused connection errors:
```
Error calling custom OpenAI LLM: Connection error.
```

This happened because:
1. The custom gateway required specific enterprise credentials
2. Connection to custom gateway was failing
3. No fallback to standard OpenAI/Groq providers

## ✅ Changes Made

### 1. Updated `playwright_agent.py`

**Before:**
```python
from ..llm import CustomOpenAILLM

class PlaywrightAgent:
    def __init__(self, api_key: str = None, model: str = "gpt-4o", gateway_url: str = None):
        self.llm = CustomOpenAILLM(api_key=api_key, model=model)
```

**After:**
```python
from ..llm import get_llm_provider
from ..config import LLMOpsConfig

class PlaywrightAgent:
    def __init__(self, provider: str = None, api_key: str = None, 
                 model: str = None, config: LLMOpsConfig = None):
        if config is None:
            config = LLMOpsConfig()
        
        llm_provider = get_llm_provider(
            provider_type=provider,
            config=config,
            api_key=api_key,
            model_name=model
        )
        
        self.llm = llm_provider.get_llm()
```

### 2. Updated `llmops_api.py`

**Before:**
```python
api_key = os.getenv("CUSTOM_OPENAI_KEY")
agent = PlaywrightAgent(api_key=api_key, model=model, gateway_url=gateway_url)
```

**After:**
```python
agent = PlaywrightAgent(config=config)
```

### 3. Created `.env.example`

Added environment configuration template:
```bash
USE_GROQ=false
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
BROWSER_TYPE=edge
```

## 🚀 How to Use

### Option 1: Use OpenAI (Default)

```bash
# .env file
USE_GROQ=false
OPENAI_API_KEY=sk-your-openai-key
```

```python
from llmops import PlaywrightAgent, LLMOpsConfig

config = LLMOpsConfig()  # Auto-detects from .env
agent = PlaywrightAgent(config=config)
```

### Option 2: Use Groq

```bash
# .env file
USE_GROQ=true
GROQ_API_KEY=gsk_your-groq-key
```

```python
config = LLMOpsConfig()  # Auto-detects Groq from USE_GROQ=true
agent = PlaywrightAgent(config=config)
```

### Option 3: Explicit Provider

```python
# Use OpenAI explicitly
agent = PlaywrightAgent(
    provider="openai",
    api_key="sk-your-key",
    model="gpt-4o"
)

# Use Groq explicitly
agent = PlaywrightAgent(
    provider="groq",
    api_key="gsk-your-key",
    model="llama-3.3-70b-versatile"
)
```

## 📋 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_GROQ` | Set to `true` to use Groq, `false` for OpenAI | `false` |
| `GROQ_API_KEY` | Groq API key | None |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `GROQ_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `BROWSER_TYPE` | Browser type for Playwright | `edge` |

## 🧪 Testing

Run the test script:
```bash
cd "e:\Kirsh Naik Academy\SeleniumMCPFlow\backend\app"
python test_agent_providers.py
```

Expected output:
```
✓ Using Provider: OpenAI (or Groq)
✓ OpenAI API Key: Set
[1/3] Initializing Playwright Agent...
[INFO] Using OpenAIProvider with model: gpt-4o
✅ Agent initialized successfully
...
✅ Test PASSED - Agent works correctly with OpenAI/Groq!
```

## 📡 API Endpoints

Both API endpoints now use the new provider system:

### 1. `/execute-playwright`
```bash
curl -X POST "http://localhost:8000/execute-playwright" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TC_001",
    "generated_prompt": "Navigate to https://example.com...",
    "browser_type": "edge",
    "headless": false
  }'
```

### 2. `/execute-playwright-from-testcase`
```bash
curl -X POST "http://localhost:8000/execute-playwright-from-testcase" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TC_001",
    "module": "Login",
    "functionality": "User Authentication",
    "description": "Verify login with valid credentials"
  }'
```

## ✅ Benefits

1. **No Custom Gateway Dependency**: Works with standard OpenAI/Groq APIs
2. **Auto-Detection**: Automatically uses correct provider from environment
3. **Flexible Configuration**: Support for multiple providers
4. **Better Error Handling**: Clear provider initialization errors
5. **Easy Switching**: Toggle between Groq/OpenAI with single env variable

## 🔧 Files Modified

1. `backend/app/llmops/generators/playwright_agent.py` - Refactored to use provider system
2. `backend/app/llmops_api.py` - Updated API to use new agent initialization
3. `.env.example` - Created environment template
4. `test_agent_providers.py` - Created test script

## 📝 Notes

- The `CustomOpenAILLM` class still exists for legacy compatibility
- But `PlaywrightAgent` no longer uses it by default
- All automation now uses standard LangChain ChatOpenAI or ChatGroq
- Provider auto-detection based on `USE_GROQ` environment variable
