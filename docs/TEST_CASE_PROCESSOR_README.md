# Test Case Processor - Excel to Playwright Automation

Convert test cases from Excel files into detailed Playwright automation prompts using LLM, then execute them with the Playwright agent.

## 📋 Features

- **Excel Integration**: Read test cases from Excel files with flexible column mapping
- **LLM-Powered Conversion**: Use OpenAI/Custom LLM to convert short descriptions into detailed step-by-step prompts
- **Playwright Execution**: Automatically execute generated prompts with Playwright agent
- **Batch Processing**: Process multiple test cases in one run
- **Results Export**: Save execution results back to Excel
- **Flexible Configuration**: Support for custom gateway URLs and API keys

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas openpyxl openai python-dotenv
```

### 2. Set API Key

```bash
# For standard OpenAI
export OPENAI_API_KEY="your-key-here"

# For custom gateway
export CUSTOM_OPENAI_KEY="your-key-here"
```

### 3. Prepare Excel File

Create an Excel file with at least a "Short Description" column:

| Test ID | Short Description | Priority | Module |
|---------|------------------|----------|---------|
| TC_001 | Login to qa4-www.365.com with username ABC and password 12345 | High | Auth |
| TC_002 | Navigate to user profile and update email | Medium | Profile |

### 4. Run Test Case Processor

#### Option A: Process Only (Generate Prompts)

```python
from backend.app.test_case_processor import TestCaseProcessor

processor = TestCaseProcessor()
processed_cases = processor.process_test_cases(
    excel_file="your_test_cases.xlsx",
    short_description_column="Short Description",
    test_id_column="Test ID",
    output_file="processed_prompts.xlsx"
)

# Print generated prompts
processor.print_test_case_prompts(processed_cases)
```

#### Option B: Process and Execute (Full Automation)

```python
import asyncio
from backend.app.test_case_executor import TestCaseExecutor

async def run():
    executor = TestCaseExecutor()
    results = await executor.execute_all_from_excel(
        excel_file="your_test_cases.xlsx",
        browser_config={"headless": False, "browser_type": "chromium"},
        save_results=True
    )

asyncio.run(run())
```

## 📝 Example Input/Output

### Input (Excel - Short Description)
```
Login to qa4-www.365.com with username ABC and password 12345
```

### Output (Generated Playwright Prompt)
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

## 🔧 Configuration

### TestCaseProcessor Options

```python
processor = TestCaseProcessor(
    api_key="your-api-key",           # Optional: defaults to env var
    model="gpt-4o",                    # Model to use
    gateway_url="https://..."          # Optional: custom gateway URL
)
```

### process_test_cases() Parameters

```python
processed = processor.process_test_cases(
    excel_file="tests.xlsx",                          # Required: Excel file path
    sheet_name="Sheet1",                              # Optional: specific sheet
    short_description_column="Short Description",     # Column with test descriptions
    test_id_column="Test ID",                         # Column with test IDs
    output_file="processed.xlsx"                      # Optional: save results
)
```

### TestCaseExecutor Options

```python
executor = TestCaseExecutor(
    api_key="your-api-key",
    model="gpt-4o"
)

results = await executor.execute_all_from_excel(
    excel_file="tests.xlsx",
    short_description_column="Short Description",
    test_id_column="Test ID",
    browser_config={
        "headless": False,           # Visible browser
        "browser_type": "chromium"   # Browser type
    },
    save_results=True                # Save execution results
)
```

## 📊 Excel File Structure

### Minimum Required

| Short Description |
|------------------|
| Your test case description here |

### Recommended

| Test ID | Short Description | Priority | Module | Expected Result |
|---------|------------------|----------|---------|-----------------|
| TC_001 | Login with valid credentials | High | Auth | User logged in successfully |
| TC_002 | Search for product | Medium | Search | Products displayed |

**Note**: All columns except "Short Description" are optional. Additional columns are passed as context to the LLM.

## 🎯 LLM Prompt Engineering

The processor uses a carefully crafted system prompt to ensure consistent output:

- **Numbered Steps**: Each step is clearly numbered (1), 2), 3)...)
- **Action Verbs**: Navigate, Click, Type, Wait for, etc.
- **Wait Conditions**: Explicit wait steps before interactions
- **Preserve Values**: Keeps exact usernames, passwords, URLs as provided
- **Verification Steps**: Includes wait conditions after actions

## 📁 Project Structure

```
backend/app/
├── test_case_processor.py      # Main processor class
├── test_case_executor.py       # Integration with Playwright agent
└── agents/
    └── playwright_custom_openai_agent.py  # Playwright automation agent

examples/
└── test_case_processor_example.py  # Usage examples
```

## 🔍 Advanced Usage

### Single Test Case Conversion

```python
processor = TestCaseProcessor()
prompt = processor.generate_playwright_prompt(
    short_description="Login with username ABC and password 12345",
    test_id="TC_001",
    additional_context={
        "URL": "https://qa4-www.365.com",
        "Priority": "High"
    }
)
print(prompt)
```

### Custom Column Names

```python
processed = processor.process_test_cases(
    excel_file="custom.xlsx",
    short_description_column="Test Scenario",  # Your custom column
    test_id_column="ID",                       # Your custom ID column
    output_file="results.xlsx"
)
```

### Batch Execution with Custom Config

```python
executor = TestCaseExecutor()

browser_configs = [
    {"browser_type": "chromium", "headless": False},
    {"browser_type": "firefox", "headless": False},
    {"browser_type": "webkit", "headless": False}
]

for config in browser_configs:
    results = await executor.execute_all_from_excel(
        excel_file="tests.xlsx",
        browser_config=config
    )
```

## 🛠️ Troubleshooting

### API Key Issues
```
❌ Error: No API key found!
```
**Solution**: Set environment variable:
```bash
export CUSTOM_OPENAI_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"
```

### Column Not Found
```
❌ Column 'Short Description' not found
```
**Solution**: Check column names in Excel file or specify correct column name:
```python
processor.process_test_cases(
    excel_file="tests.xlsx",
    short_description_column="Your_Column_Name"
)
```

### Excel File Not Found
```
❌ File not found: tests.xlsx
```
**Solution**: Provide full path or ensure file is in current directory:
```python
processor.process_test_cases(
    excel_file="C:/path/to/your/tests.xlsx"
)
```

## 📈 Output Files

### Processed Prompts (Excel)
Contains:
- Original test ID and description
- Generated detailed prompt
- Additional context from Excel

### Execution Results (Excel)
Contains:
- Test ID and description
- Execution status (success/error)
- Tool calls count
- Error messages (if any)
- Timestamp

## 🤝 Integration with Playwright Agent

The processor seamlessly integrates with the Playwright agent:

1. **Process**: Excel → LLM → Detailed Prompts
2. **Execute**: Prompts → Playwright Agent → Browser Automation
3. **Report**: Results → Excel Report

## 📚 Examples

See `examples/test_case_processor_example.py` for complete examples:
- Basic usage
- Single test case conversion
- Custom column names
- Batch processing
- Full automation workflow

## 🎓 Best Practices

1. **Clear Descriptions**: Write concise but complete test descriptions
2. **Include Context**: Add URL, credentials, expected results in Excel
3. **Test IDs**: Use unique, meaningful test IDs
4. **Batch Size**: Process 10-20 test cases at a time for better monitoring
5. **Review Prompts**: Always review generated prompts before mass execution
6. **Browser Config**: Start with visible browser (headless=False) for debugging

## 📞 Support

For issues or questions, check:
- Code comments in `test_case_processor.py`
- Examples in `test_case_processor_example.py`
- Playwright agent documentation

---

**Version**: 1.0.0  
**Last Updated**: November 2025
