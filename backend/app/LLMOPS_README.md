# LLMOps Structure

Complete LLMOps architecture for test case processing with LLM integration.

## 📁 Structure

```
backend/app/llmops/
├── __init__.py                 # Package exports
├── config/                     # Configuration management
│   ├── __init__.py
│   └── config.py              # LLMOpsConfig, LLMConfig
├── llm/                        # LLM providers
│   ├── __init__.py
│   └── providers.py           # GroqProvider, OpenAIProvider
├── prompts/                    # Prompt management
│   ├── __init__.py
│   └── prompt_manager.py      # PromptManager, templates
├── models/                     # Data models
│   ├── __init__.py
│   └── schemas.py             # TestCase, TestCasePrompt, ExecutionResult
├── utils/                      # Utilities
│   ├── __init__.py
│   └── excel_utils.py         # ExcelReader, ExcelWriter
└── generators/                 # Main generators
    ├── __init__.py
    └── test_case_generator.py # TestCaseGenerator (orchestrator)
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# For Groq
set USE_GROQ=true
set GROQ_API_KEY=your-groq-api-key

# For OpenAI/Custom Gateway
set USE_GROQ=false
set CUSTOM_OPENAI_KEY=your-key
set CUSTOM_OPENAI_BASE_URL=https://gateway.ai-npe.humana.com/openai/deployments/gpt-4o
```

### 2. Basic Usage

```python
from llmops import TestCaseGenerator

# Initialize (auto-detects provider from environment)
generator = TestCaseGenerator()

# Process Excel file
prompts = generator.process_excel(
    excel_path="test_cases.xlsx",
    sheet_name="Sheet1"
)

# Access generated prompts
for prompt in prompts:
    print(f"Test: {prompt.test_case.test_id}")
    print(f"Prompt: {prompt.generated_prompt}")
```

### 3. Advanced Usage

```python
from llmops import (
    TestCaseGenerator,
    ExcelReader,
    get_config,
    TestCaseStatus
)

# Manual configuration
config = get_config()
print(f"Using: {config.get_llm_config('groq').model}")

# Read test cases separately
reader = ExcelReader("test_cases.xlsx")
test_cases = reader.get_test_cases()

# Generate prompts
generator = TestCaseGenerator()
prompts = generator.generate_batch(test_cases)

# Filter by status
pending = [tc for tc in test_cases if tc.status == TestCaseStatus.PENDING]
```

## 📦 Components

### Config Module
- `LLMOpsConfig`: Main configuration dataclass
- `LLMConfig`: Individual LLM configuration
- `get_config()`: Singleton config instance

### LLM Module
- `LLMProvider`: Abstract base class
- `GroqProvider`: Groq implementation
- `OpenAIProvider`: OpenAI/Custom gateway implementation
- `get_llm_provider()`: Factory function

### Prompts Module
- `PromptManager`: Manages prompt templates
- `get_prompt_manager()`: Singleton instance
- Templates for test case conversion

### Models Module
- `TestCase`: Represents a test case
- `TestCasePrompt`: Generated prompt with metadata
- `ExecutionResult`: Execution result data
- `TestCaseStatus`: Enum for test status

### Utils Module
- `ExcelReader`: Read test cases from Excel
- `ExcelWriter`: Write execution results to Excel

### Generators Module
- `TestCaseGenerator`: Main orchestrator
  - Reads Excel files
  - Generates prompts using LLM
  - Batch processing
  - Provider management

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_GROQ` | Use Groq provider | `false` |
| `GROQ_API_KEY` | Groq API key | - |
| `GROQ_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `CUSTOM_OPENAI_KEY` | Custom gateway key | - |
| `CUSTOM_OPENAI_BASE_URL` | Custom gateway URL | - |

### Config File Example

```python
from llmops import LLMOpsConfig

config = LLMOpsConfig(
    use_groq=True,
    groq_api_key="your-key",
    groq_model="llama-3.3-70b-versatile",
    temperature=0.0
)
```

## 📊 Excel Format

Expected Excel columns:

| Column | Description | Required |
|--------|-------------|----------|
| Test ID | Unique test identifier | ✓ |
| Module | Module name | ✓ |
| Functionality | Feature being tested | ✓ |
| Description | Test description | ✓ |
| Steps | Test steps | Optional |
| Expected Result | Expected outcome | Optional |
| Priority | Test priority | Optional |

## 🧪 Testing

### Run Integration Tests

```bash
cd backend/app
python test_llmops_integration.py
```

### Run Example

```bash
python llmops_example.py
```

## 🔄 Migration from Old Code

If you have existing `test_case_processor.py`:

```python
# Old code
from test_case_processor import TestCaseProcessor
processor = TestCaseProcessor()

# New code (LLMOps)
from llmops import TestCaseGenerator
generator = TestCaseGenerator()
```

All functionality is preserved with better organization!

## 📝 Example Output

```
======================================================================
LLMOps Test Case Generator Example
======================================================================

✓ Using Provider: groq
✓ Model: llama-3.3-70b-versatile
✓ Temperature: 0.0

📖 Reading test cases from: test_cases.xlsx
✓ Found 3 test cases

🤖 Generating Playwright prompts using LLM...
✓ Generated 3 prompts

======================================================================
Generated Prompts:
======================================================================

[1] Test Case: TC001
    Module: Login
    Description: Verify user can login with valid credentials...

    Generated Prompt:
    ------------------------------------------------------------------
    1. Navigate to the login page at https://example.com/login
    2. Enter "testuser@example.com" into the username field...
    ------------------------------------------------------------------
```

## 🎯 Benefits

1. **Organized**: Clear separation of concerns
2. **Maintainable**: Each module has single responsibility
3. **Testable**: Easy to test individual components
4. **Extensible**: Add new providers/features easily
5. **Type-Safe**: Proper data models with Pydantic
6. **Documented**: Comprehensive docstrings

## 🔗 Integration with Playwright

Use generated prompts with Playwright agent:

```python
from llmops import TestCaseGenerator
from playwright_custom_openai_agent import PlaywrightAgent

# Generate prompts
generator = TestCaseGenerator()
prompts = generator.process_excel("test_cases.xlsx")

# Execute with Playwright
agent = PlaywrightAgent()
for prompt in prompts:
    result = await agent.execute(prompt.generated_prompt)
```

## 📚 API Reference

See individual module docstrings for detailed API documentation:
- `llmops.config`: Configuration classes
- `llmops.llm`: LLM provider interfaces
- `llmops.prompts`: Prompt management
- `llmops.models`: Data models
- `llmops.utils`: Utility functions
- `llmops.generators`: Main orchestrators
