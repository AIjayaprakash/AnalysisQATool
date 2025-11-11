# Groq vs OpenAI/Custom Gateway Setup Guide

The Test Case Processor supports both **Groq** and **OpenAI/Custom Gateway** as LLM providers. You can easily switch between them using environment variables.

---

## 🎯 Quick Switch

### Use Groq (Fast & Free Tier Available)
```bash
export GROQ_API_KEY="your-groq-api-key"
export USE_GROQ=true
```

### Use OpenAI/Custom Gateway
```bash
export CUSTOM_OPENAI_KEY="your-openai-key"
# or
export OPENAI_API_KEY="your-openai-key"

# Make sure USE_GROQ is not set or is false
export USE_GROQ=false
```

---

## 🚀 Setup Instructions

### Option 1: Using Groq (Recommended for Testing)

**Advantages:**
- ✅ Fast inference speed
- ✅ Free tier available (generous limits)
- ✅ Multiple open-source models (Llama, Mixtral, Gemma)
- ✅ No custom gateway configuration needed

**Steps:**

1. **Get Groq API Key**
   - Visit: https://console.groq.com/
   - Sign up for free account
   - Generate API key

2. **Set Environment Variables**
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your-groq-api-key-here"
   $env:USE_GROQ="true"
   
   # Windows CMD
   set GROQ_API_KEY=your-groq-api-key-here
   set USE_GROQ=true
   
   # Linux/Mac
   export GROQ_API_KEY="your-groq-api-key-here"
   export USE_GROQ=true
   ```

3. **Install Groq Package**
   ```bash
   pip install groq
   ```

4. **Use in Code**
   ```python
   from backend.app.test_case_processor import TestCaseProcessor
   
   # Will auto-detect Groq based on USE_GROQ env variable
   processor = TestCaseProcessor()
   
   # Or explicitly specify
   processor = TestCaseProcessor(
       api_key="your-groq-api-key",
       model="llama-3.1-70b-versatile",
       use_groq=True
   )
   ```

### Option 2: Using OpenAI/Custom Gateway

**Advantages:**
- ✅ GPT-4 and GPT-3.5 models
- ✅ Enterprise custom gateway support
- ✅ Proven reliability

**Steps:**

1. **Set API Key**
   ```bash
   # For standard OpenAI
   export OPENAI_API_KEY="your-openai-key"
   
   # For custom gateway (like Humana's)
   export CUSTOM_OPENAI_KEY="your-custom-key"
   ```

2. **Set USE_GROQ to false (or don't set it)**
   ```bash
   export USE_GROQ=false
   # or just don't set it (defaults to false)
   ```

3. **Use in Code**
   ```python
   from backend.app.test_case_processor import TestCaseProcessor
   
   # Will auto-detect OpenAI based on USE_GROQ env variable
   processor = TestCaseProcessor()
   
   # Or explicitly specify
   processor = TestCaseProcessor(
       api_key="your-openai-key",
       model="gpt-4o",
       use_groq=False
   )
   ```

---

## 📊 Model Comparison

### Groq Models

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| `llama-3.1-70b-versatile` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 128k | **Recommended** - Best balance |
| `mixtral-8x7b-32768` | ⚡⚡⚡⚡ | ⭐⭐⭐ | 32k | Fast responses |
| `gemma2-9b-it` | ⚡⚡⚡⚡⚡ | ⭐⭐ | 8k | Quick tests |

### OpenAI Models

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| `gpt-4o` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 128k | **Recommended** - Highest quality |
| `gpt-4` | ⚡ | ⭐⭐⭐⭐⭐ | 8k | Complex reasoning |
| `gpt-3.5-turbo` | ⚡⚡⚡ | ⭐⭐⭐ | 16k | Fast & economical |

---

## 🔧 Code Examples

### Example 1: Auto-Detect from Environment

```python
from backend.app.test_case_processor import TestCaseProcessor

# Automatically uses Groq if USE_GROQ=true, otherwise OpenAI
processor = TestCaseProcessor()

prompt = processor.generate_playwright_prompt(
    short_description="Login to qa4-www.365.com with username ABC and password 12345",
    test_id="TC_001"
)
```

### Example 2: Explicitly Use Groq

```python
processor = TestCaseProcessor(
    api_key="your-groq-api-key",
    model="llama-3.1-70b-versatile",
    use_groq=True
)
```

### Example 3: Explicitly Use OpenAI

```python
processor = TestCaseProcessor(
    api_key="your-openai-key",
    model="gpt-4o",
    use_groq=False
)
```

### Example 4: Compare Both

```python
import os

# Test with Groq
groq_processor = TestCaseProcessor(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-70b-versatile",
    use_groq=True
)
groq_result = groq_processor.generate_playwright_prompt(test_description)

# Test with OpenAI
openai_processor = TestCaseProcessor(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    use_groq=False
)
openai_result = openai_processor.generate_playwright_prompt(test_description)

# Compare results
print("Groq:", groq_result)
print("OpenAI:", openai_result)
```

---

## 🧪 Testing Setup

### Test Groq Configuration
```bash
# Set environment
export GROQ_API_KEY="your-key"
export USE_GROQ=true

# Run example
python groq_openai_example.py
```

### Test OpenAI Configuration
```bash
# Set environment
export OPENAI_API_KEY="your-key"
export USE_GROQ=false

# Run example
python groq_openai_example.py
```

---

## 💡 Best Practices

### When to Use Groq
- ✅ Development and testing
- ✅ Need fast response times
- ✅ Budget-conscious projects
- ✅ Want to use open-source models
- ✅ High volume of requests (free tier generous)

### When to Use OpenAI/Custom Gateway
- ✅ Production deployments
- ✅ Need highest quality outputs
- ✅ Enterprise requirements (custom gateway)
- ✅ Complex reasoning tasks
- ✅ Existing OpenAI integrations

### Hybrid Approach
Use both! Test with Groq during development, deploy with OpenAI/Custom Gateway for production:

```python
import os

# Use Groq in development, OpenAI in production
is_production = os.getenv("ENVIRONMENT") == "production"

processor = TestCaseProcessor(
    use_groq=not is_production  # Groq for dev, OpenAI for prod
)
```

---

## 🐛 Troubleshooting

### Groq Issues

**Problem:** `ImportError: No module named 'groq'`
```bash
pip install groq
```

**Problem:** `Authentication failed`
```bash
# Check your API key
echo $GROQ_API_KEY

# Get new key from https://console.groq.com/
```

**Problem:** `Rate limit exceeded`
- Groq has generous free tier but rate limits exist
- Consider spreading requests or upgrading plan
- Check: https://console.groq.com/docs/rate-limits

### OpenAI Issues

**Problem:** `401 Unauthorized`
```bash
# Check your API key is correct
echo $OPENAI_API_KEY
```

**Problem:** `Custom gateway not working`
- Verify gateway URL is correct
- Check custom headers (api-key, ai-gateway-version)
- Contact your gateway administrator

---

## 📈 Performance Comparison

Based on typical test case conversions:

| Metric | Groq (Llama 3.1 70B) | OpenAI (GPT-4o) |
|--------|---------------------|-----------------|
| Response Time | ~0.5-1s | ~2-3s |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost (per 1M tokens) | Free tier / $0.59 | $5.00 |
| Rate Limits | 30 req/min (free) | 500 req/min |

---

## 🔒 Security Notes

1. **Never commit API keys to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use .env files**
   ```bash
   # Create .env file
   GROQ_API_KEY=your-key-here
   USE_GROQ=true
   ```

3. **Rotate keys regularly**
   - Groq: https://console.groq.com/
   - OpenAI: https://platform.openai.com/api-keys

---

## 📚 Additional Resources

- **Groq Documentation**: https://console.groq.com/docs
- **Groq Models**: https://console.groq.com/docs/models
- **OpenAI API**: https://platform.openai.com/docs
- **Example Scripts**: `groq_openai_example.py`

---

## 🎓 Example Workflow

```bash
# 1. Set up environment
export GROQ_API_KEY="your-groq-key"
export USE_GROQ=true

# 2. Install dependencies
pip install groq pandas openpyxl

# 3. Run example
python groq_openai_example.py

# 4. Process your test cases
python complete_workflow_example.py

# 5. Switch to OpenAI if needed
export USE_GROQ=false
export OPENAI_API_KEY="your-openai-key"
python complete_workflow_example.py
```

---

**Version**: 1.0.0  
**Last Updated**: November 2025
