# Test Case Processor - Quick Reference Guide

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install pandas openpyxl openai python-dotenv
```

### 2. Set API Key
```bash
export CUSTOM_OPENAI_KEY="your-api-key"
# or
export OPENAI_API_KEY="your-api-key"
```

### 3. Run Example
```bash
python complete_workflow_example.py
```

---

## 📝 Basic Usage

### Convert Single Test Case
```python
from backend.app.test_case_processor import TestCaseProcessor

processor = TestCaseProcessor()
prompt = processor.generate_playwright_prompt(
    short_description="Login to qa4-www.365.com with username ABC and password 12345",
    test_id="TC_001"
)
print(prompt)
```

**Output:**
```
1) Navigate to https://qa4-www.365.com
2) Wait for sign in to appear
3) Click Sign in
4) Wait for Username to appear
5) Type username as ABC. Please don't change username
6) Type password as 12345
7) Click Sign In
8) Wait for Home screen to appear
```

### Process Excel File
```python
processor = TestCaseProcessor()
processed = processor.process_test_cases(
    excel_file="test_cases.xlsx",
    short_description_column="Short Description",
    output_file="prompts.xlsx"
)
```

### Execute with Playwright
```python
import asyncio
from backend.app.test_case_executor import TestCaseExecutor

async def run():
    executor = TestCaseExecutor()
    results = await executor.execute_all_from_excel(
        excel_file="test_cases.xlsx",
        browser_config={"headless": False}
    )

asyncio.run(run())
```

---

## 📊 Excel File Format

### Minimum Required
| Short Description |
|------------------|
| Login to qa4-www.365.com with username ABC and password 12345 |

### Recommended
| Test ID | Short Description | Priority | Module |
|---------|------------------|----------|---------|
| TC_001 | Login to qa4-www.365.com with username ABC and password 12345 | High | Auth |

---

## 🎯 Expected Output Format

All generated prompts follow this structure:
- ✅ Numbered steps: 1), 2), 3)...
- ✅ Action verbs: Navigate, Click, Type, Wait for
- ✅ Wait conditions before interactions
- ✅ Preserves exact values (usernames, passwords)
- ✅ Verification steps after actions

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/app/test_case_processor.py` | Main processor class |
| `backend/app/test_case_executor.py` | Playwright integration |
| `complete_workflow_example.py` | Complete examples |
| `test_case_processor_unittest.py` | Unit tests |

---

## 🔧 Configuration Options

### TestCaseProcessor
```python
processor = TestCaseProcessor(
    api_key="your-key",              # API key
    model="gpt-4o",                   # Model name
    gateway_url="https://..."         # Custom gateway (optional)
)
```

### Browser Config
```python
browser_config = {
    "headless": False,           # Visible/headless
    "browser_type": "chromium"   # chromium, firefox, webkit, edge
}
```

---

## ✅ Verification Checklist

Before execution:
- [ ] API key is set in environment
- [ ] Excel file has "Short Description" column
- [ ] pandas and openpyxl are installed
- [ ] Review generated prompts look correct

---

## 🐛 Troubleshooting

### No API Key
```bash
export CUSTOM_OPENAI_KEY="your-key"
```

### Column Not Found
```python
# Check your column name in Excel
processor.process_test_cases(
    excel_file="tests.xlsx",
    short_description_column="Your_Column_Name"  # ← Update this
)
```

### Import Error
```bash
pip install pandas openpyxl openai
```

---

## 📚 Examples

Run these files for examples:
```bash
# Unit tests
python test_case_processor_unittest.py

# Complete workflow
python complete_workflow_example.py

# Example usage patterns
python examples/test_case_processor_example.py
```

---

## 🎓 Best Practices

1. **Clear Descriptions**: Write complete test case descriptions
2. **Include Context**: Add URLs, credentials in Excel columns
3. **Review Prompts**: Always review before mass execution
4. **Start Visible**: Use `headless=False` for debugging
5. **Batch Wisely**: Process 10-20 cases at a time

---

## 📞 Need Help?

Check:
- `docs/TEST_CASE_PROCESSOR_README.md` - Full documentation
- Code comments in source files
- Example files for patterns

---

**Version**: 1.0.0  
**Last Updated**: November 2025
