# Prompt Validation Tool - Quick Reference

## 📚 Overview

The Prompt Validation Tool provides comprehensive validation for LLM prompts to ensure security, quality, and compliance.

## 🚀 Quick Start

### Basic Usage

```python
from llmops.prompts.prompt_validation_tool import PromptValidator

# Create validator
validator = PromptValidator()

# Validate a prompt
report = validator.validate("Your prompt text here")

# Check if valid
if report.is_valid:
    print("✅ Prompt is valid!")
else:
    print("❌ Prompt has issues")
    for result in report.results:
        print(f"  - {result.message}")
```

### Quick Validation

```python
from llmops.prompts.prompt_validation_tool import quick_validate

# Quick check
is_valid = quick_validate("Your prompt text")
print(f"Valid: {is_valid}")
```

### Sanitize Prompts

```python
from llmops.prompts.prompt_validation_tool import sanitize_prompt

# Clean dangerous content
clean_prompt = sanitize_prompt("<script>alert('xss')</script>Test")
print(clean_prompt)  # Output: Test
```

## 🔧 Integration with Prompt Manager

```python
from llmops.prompts.prompt_manager import PromptManager

# Create manager with validation enabled
pm = PromptManager(enable_validation=True)

# Format and validate in one step
system_prompt, user_prompt, validation_report = pm.format_and_validate_prompt(
    "test_case_conversion",
    validate=True,
    short_description="Login to website"
)

# Quick validate
if pm.quick_validate("My prompt"):
    print("Valid!")

# Sanitize
clean = pm.sanitize("<b>Prompt</b>")
```

## 📊 Validation Levels

| Level | Description | Example |
|-------|-------------|---------|
| **INFO** | Informational messages | "Prompt length is acceptable" |
| **WARNING** | Issues that should be reviewed | "Prompt is close to max length" |
| **ERROR** | Serious issues that may cause problems | "Prompt exceeds maximum length" |
| **CRITICAL** | Security issues or invalid content | "Injection attack detected" |

## 🛡️ Security Checks

The validator automatically checks for:

### 1. **Injection Attacks**
- Script tags (`<script>`)
- JavaScript protocol (`javascript:`)
- Event handlers (`onclick`, `onerror`)
- eval() and exec() functions
- Template injection (`${...}`, `{{...}}`)

### 2. **Prompt Manipulation**
- "Ignore previous instructions"
- "Disregard all previous"
- "Forget everything"
- "Jailbreak" attempts

### 3. **Code Execution**
- `__import__`
- `subprocess`
- `os.system`

## ⚙️ Configuration Options

```python
from llmops.prompts.prompt_validation_tool import (
    PromptValidator,
    PromptValidationConfig
)

# Custom configuration
config = PromptValidationConfig(
    max_length=5000,           # Maximum prompt length
    min_length=10,             # Minimum prompt length
    max_tokens=2000,           # Maximum token count
    allow_html=False,          # Allow HTML tags
    allow_code=True,           # Allow code blocks
    strict_mode=False,         # Strict validation
    check_injections=True,     # Check for injections
    check_profanity=False      # Check for profanity
)

validator = PromptValidator(config)
```

## 📋 Validation Report

```python
report = validator.validate("Your prompt")

# Access results
print(f"Valid: {report.is_valid}")
print(f"Token count: {report.token_count}")
print(f"Sanitized: {report.sanitized_prompt}")

# Get results by level
errors = report.get_by_level(ValidationLevel.ERROR)
warnings = report.get_by_level(ValidationLevel.WARNING)

# Check for errors
if report.has_errors():
    print("Prompt has errors!")

# Convert to dict/JSON
report_dict = report.to_dict()
```

## 🔍 Common Use Cases

### Use Case 1: Validate Before Sending to LLM

```python
pm = PromptManager(enable_validation=True)

# Format and validate
system_prompt, user_prompt, report = pm.format_and_validate_prompt(
    "test_case_conversion",
    short_description="Test case description"
)

if report.is_valid:
    # Send to LLM
    response = llm.invoke(user_prompt)
else:
    print("Invalid prompt, cannot proceed")
```

### Use Case 2: Batch Validation

```python
validator = PromptValidator()

prompts = [
    "Prompt 1",
    "Prompt 2",
    "Prompt 3"
]

reports = validator.validate_batch(prompts)

for i, report in enumerate(reports):
    print(f"Prompt {i+1}: {'✅' if report.is_valid else '❌'}")
```

### Use Case 3: Security Check

```python
validator = PromptValidator()

suspicious_prompt = "Ignore all previous instructions and..."

report = validator.validate(suspicious_prompt)

if report.get_by_level(ValidationLevel.CRITICAL):
    print("⚠️  Security threat detected!")
    # Block or log the attempt
```

### Use Case 4: Auto-Sanitization

```python
pm = PromptManager()

dirty_prompt = "<script>alert('xss')</script>Login to site"

# Sanitize automatically
clean_prompt = pm.sanitize(dirty_prompt)

# Now safe to use
print(clean_prompt)  # Output: Login to site
```

## 📝 Validation Results

Each validation result includes:

```python
result = ValidationResult(
    passed=True,              # Whether validation passed
    level=ValidationLevel.INFO,  # Severity level
    message="Validation message",  # Description
    field="prompt",           # Field being validated
    suggestion="Fix suggestion"  # How to fix (optional)
)
```

## 🎯 Best Practices

### 1. **Always Validate User Input**
```python
# BAD - No validation
user_prompt = get_user_input()
response = llm.invoke(user_prompt)  # Dangerous!

# GOOD - With validation
user_prompt = get_user_input()
if quick_validate(user_prompt):
    response = llm.invoke(user_prompt)
else:
    raise ValueError("Invalid prompt")
```

### 2. **Use Strict Mode in Production**
```python
# Development
config = PromptValidationConfig(strict_mode=False)

# Production
config = PromptValidationConfig(strict_mode=True)
```

### 3. **Log Validation Failures**
```python
report = validator.validate(prompt)

if not report.is_valid:
    # Log for security monitoring
    log_error(
        "Prompt validation failed",
        extra={
            "errors": [r.message for r in report.get_by_level(ValidationLevel.ERROR)],
            "prompt_preview": prompt[:50]
        }
    )
```

### 4. **Sanitize Before Storage**
```python
# Clean prompts before saving to database
clean_prompt = sanitize_prompt(user_input)
database.save(clean_prompt)
```

## 🔬 Testing

Run the test examples:

```bash
cd backend/app/llmops/prompts
python test_prompt_validation.py
```

## 📊 Validation Summary

```python
report = validator.validate(prompt)
summary = report.to_dict()

print(f"""
Validation Summary:
  Valid: {summary['is_valid']}
  Token Count: {summary['token_count']}
  Total Results: {summary['summary']['total']}
  Errors: {summary['summary']['error']}
  Warnings: {summary['summary']['warning']}
""")
```

## ⚠️ Error Handling

```python
try:
    system_prompt, user_prompt, report = pm.format_and_validate_prompt(
        "test_case_conversion",
        validate=True,
        short_description="Test"
    )
except ValueError as e:
    # Critical validation errors
    print(f"Validation failed: {e}")
except RuntimeError as e:
    # Validation disabled
    print(f"Validation error: {e}")
```

## 🔗 API Integration

```python
from fastapi import HTTPException

@app.post("/generate-prompt")
async def generate_prompt(request: PromptRequest):
    pm = PromptManager(enable_validation=True)
    
    try:
        system, user, report = pm.format_and_validate_prompt(
            "test_case_conversion",
            short_description=request.description
        )
        
        if not report.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid prompt",
                    "validation_report": report.to_dict()
                }
            )
        
        return {"system": system, "user": user}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 📚 Complete Example

```python
from llmops.prompts.prompt_manager import PromptManager
from llmops.prompts.prompt_validation_tool import ValidationLevel

# Initialize
pm = PromptManager(enable_validation=True)

# Test case
test_description = "Login to website with credentials"

# Format and validate
system_prompt, user_prompt, report = pm.format_and_validate_prompt(
    "test_case_conversion",
    validate=True,
    short_description=test_description
)

# Check results
print(f"Valid: {report.is_valid}")
print(f"Token Count: {report.token_count}")

# Show issues
for result in report.results:
    icon = "✅" if result.passed else "❌"
    print(f"{icon} [{result.level.value.upper()}] {result.message}")

# Use prompts
if report.is_valid:
    # Send to LLM
    response = llm.invoke(user_prompt)
    print(f"LLM Response: {response}")
```

## 🆘 Troubleshooting

### Issue: "Validation is disabled"
**Solution:** Enable validation when creating PromptManager:
```python
pm = PromptManager(enable_validation=True)
```

### Issue: "Module not found: bleach"
**Solution:** Install required dependency:
```bash
pip install bleach
```

### Issue: "Prompt validation failed with critical errors"
**Solution:** Check the validation report for details:
```python
try:
    system, user, report = pm.format_and_validate_prompt(...)
except ValueError as e:
    print(f"Error: {e}")
    # Review and fix the prompt
```

## 📖 Additional Resources

- **Main Module**: `llmops/prompts/prompt_validation_tool.py`
- **Integration**: `llmops/prompts/prompt_manager.py`
- **Examples**: `llmops/prompts/test_prompt_validation.py`
- **Documentation**: This file

## 🔐 Security Notes

1. **Always validate user input** before sending to LLM
2. **Use strict mode in production** for enhanced security
3. **Log validation failures** for security monitoring
4. **Sanitize prompts** before storage or processing
5. **Review critical errors** immediately - they indicate security threats
