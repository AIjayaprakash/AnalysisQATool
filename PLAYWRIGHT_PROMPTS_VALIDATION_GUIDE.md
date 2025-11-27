# Playwright Prompts Validation - Quick Reference

## 📚 Overview

The `PlaywrightAgentPrompts` class now includes comprehensive validation for all prompts used in Playwright automation to ensure security, quality, and compliance.

## 🚀 Quick Start

### Basic Usage with Validation

```python
from llmops.generators.playwright_prompts import PlaywrightAgentPrompts

# Create prompts manager with validation enabled (default)
prompts = PlaywrightAgentPrompts(enable_validation=True)

# Get validated system prompt
system_prompt, system_report = prompts.get_validated_system_prompt(validate=True)

print(f"Valid: {system_report.is_valid}")
print(f"Token Count: {system_report.token_count}")
```

### Format and Validate User Prompts

```python
# Format user prompt from test description
test_description = "Login to https://example.com with credentials"

user_prompt, user_report = prompts.format_and_validate_user_prompt(
    test_description,
    validate=True
)

if user_report.is_valid:
    print("✅ Prompt is valid!")
    print(f"Formatted prompt: {user_prompt}")
else:
    print("❌ Prompt has issues")
```

## 🔧 Initialization Options

### With Default Validation

```python
# Validation enabled with default config
prompts = PlaywrightAgentPrompts(enable_validation=True)
```

### With Custom Validation Config

```python
from llmops.prompts.prompt_validation_tool import PromptValidationConfig

# Custom configuration
config = PromptValidationConfig(
    max_length=5000,
    min_length=20,
    max_tokens=2000,
    allow_html=False,
    allow_code=True,
    strict_mode=True,
    check_injections=True
)

prompts = PlaywrightAgentPrompts(enable_validation=True, validation_config=config)
```

### Without Validation

```python
# Validation disabled
prompts = PlaywrightAgentPrompts(enable_validation=False)
```

## 🛡️ Key Methods

### 1. Get Validated System Prompt

```python
system_prompt, report = prompts.get_validated_system_prompt(validate=True)

print(f"Valid: {report.is_valid}")
print(f"Tokens: {report.token_count}")
print(f"System prompt length: {len(system_prompt)}")
```

### 2. Format and Validate User Prompt

```python
test_description = "Navigate to site and login"

try:
    user_prompt, report = prompts.format_and_validate_user_prompt(
        test_description,
        validate=True
    )
    
    if report.is_valid:
        # Use the prompt
        response = llm.invoke(user_prompt)
    
except ValueError as e:
    # Critical validation errors
    print(f"Validation failed: {e}")
```

### 3. Validate Tool Calls

```python
# Validate a tool call before execution
tool_name = "playwright_navigate"
args = {"url": "https://example.com"}

tool_call, report = prompts.validate_tool_call_prompt(
    tool_name,
    args,
    validate=True
)

if report.is_valid:
    print(f"✅ Tool call valid: {tool_call}")
else:
    print("❌ Tool call has issues")
```

### 4. Quick Validation

```python
# Fast boolean check
test_desc = "Login to website"

if prompts.quick_validate(test_desc):
    print("✅ Valid")
else:
    print("❌ Invalid")
```

### 5. Sanitize Prompts

```python
# Remove dangerous content
dirty = "<script>alert('xss')</script>Login to site"
clean = prompts.sanitize(dirty)

print(f"Sanitized: {clean}")  # Output: Login to site
```

### 6. Enable/Disable Validation Dynamically

```python
# Start without validation
prompts = PlaywrightAgentPrompts(enable_validation=False)

# Enable later
prompts.enable_validation()

# Disable
prompts.disable_validation()

# Enable with custom config
config = PromptValidationConfig(strict_mode=True)
prompts.enable_validation(config)
```

## 🔍 Common Use Cases

### Use Case 1: Complete Workflow with Validation

```python
from llmops.generators.playwright_prompts import PlaywrightAgentPrompts

# Initialize
prompts = PlaywrightAgentPrompts(enable_validation=True)

# Step 1: Get system prompt
system_prompt, sys_report = prompts.get_validated_system_prompt(validate=True)

# Step 2: Format user prompt
test_description = """
Navigate to https://example.com
Login with username 'testuser' and password 'testpass'
Click submit button
Take screenshot
"""

user_prompt, user_report = prompts.format_and_validate_user_prompt(
    test_description.strip(),
    validate=True
)

# Step 3: Validate tool calls
tool_calls = [
    ("playwright_navigate", {"url": "https://example.com"}),
    ("playwright_type", {"selector": "input#username", "text": "testuser", "element_description": "Username"}),
    ("playwright_screenshot", {"filename": "login.png"})
]

for tool_name, args in tool_calls:
    tool_call, tool_report = prompts.validate_tool_call_prompt(tool_name, args, validate=True)
    print(f"✅ {tool_name}: Valid")

# All validated - ready to execute
print("✅ Workflow validated successfully!")
```

### Use Case 2: Security Validation

```python
prompts = PlaywrightAgentPrompts(enable_validation=True)

# Potentially malicious test descriptions
suspicious_tests = [
    "Login to site <script>alert('xss')</script>",
    "Navigate to javascript:alert('test')",
    "Click button and execute eval('code')"
]

for test_desc in suspicious_tests:
    try:
        user_prompt, report = prompts.format_and_validate_user_prompt(
            test_desc,
            validate=True
        )
        
        # Check for critical issues
        from llmops.prompts.prompt_validation_tool import ValidationLevel
        critical = report.get_by_level(ValidationLevel.CRITICAL)
        
        if critical:
            print(f"⚠️  SECURITY THREAT: {test_desc}")
            for result in critical:
                print(f"  - {result.message}")
    
    except ValueError as e:
        print(f"🚫 BLOCKED: {test_desc}")
        print(f"  Reason: {e}")
```

### Use Case 3: Batch Tool Call Validation

```python
prompts = PlaywrightAgentPrompts(enable_validation=True)

# Multiple tool calls to validate
tool_calls = [
    ("playwright_navigate", {"url": "https://example.com"}),
    ("playwright_click", {"selector": "button#submit", "element_description": "Submit"}),
    ("playwright_type", {"selector": "input#email", "text": "test@example.com", "element_description": "Email"}),
    ("playwright_screenshot", {"filename": "page.png"}),
    ("playwright_close_browser", {})
]

validated_calls = []

for tool_name, args in tool_calls:
    try:
        tool_call, report = prompts.validate_tool_call_prompt(tool_name, args, validate=True)
        
        if report.is_valid:
            validated_calls.append((tool_name, args, tool_call))
            print(f"✅ {tool_name}: Valid")
        else:
            print(f"❌ {tool_name}: Invalid")
    
    except ValueError as e:
        print(f"🚫 {tool_name}: Blocked - {e}")

print(f"\n✅ Validated {len(validated_calls)}/{len(tool_calls)} tool calls")
```

### Use Case 4: Custom Validation for Production

```python
from llmops.prompts.prompt_validation_tool import PromptValidationConfig

# Strict production config
production_config = PromptValidationConfig(
    max_length=3000,          # Shorter prompts
    min_length=10,            # Minimum requirement
    max_tokens=1500,          # Token limit
    allow_html=False,         # No HTML allowed
    allow_code=False,         # No code blocks
    strict_mode=True,         # Strict validation
    check_injections=True,    # Always check for attacks
    check_profanity=True      # Check profanity
)

prompts = PlaywrightAgentPrompts(
    enable_validation=True,
    validation_config=production_config
)

# Now all validations use strict rules
test_desc = "Login to website"
user_prompt, report = prompts.format_and_validate_user_prompt(test_desc, validate=True)
```

## 📊 Validation Report

### Understanding Validation Results

```python
user_prompt, report = prompts.format_and_validate_user_prompt("Test case", validate=True)

# Check overall validity
print(f"Valid: {report.is_valid}")

# Token count
print(f"Tokens: {report.token_count}")

# Get sanitized version
if report.sanitized_prompt:
    print(f"Sanitized: {report.sanitized_prompt}")

# Get results by severity level
from llmops.prompts.prompt_validation_tool import ValidationLevel

critical = report.get_by_level(ValidationLevel.CRITICAL)
errors = report.get_by_level(ValidationLevel.ERROR)
warnings = report.get_by_level(ValidationLevel.WARNING)

print(f"Critical: {len(critical)}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

# Iterate through all results
for result in report.results:
    icon = "✅" if result.passed else "❌"
    print(f"{icon} [{result.level.value}] {result.message}")
```

## 🛡️ Security Features

The validation automatically checks for:

### 1. Injection Attacks
- Script tags: `<script>`, `</script>`
- JavaScript protocol: `javascript:`
- Event handlers: `onclick`, `onerror`, `onload`
- eval() and exec() functions
- Template injection: `${...}`, `{{...}}`

### 2. Prompt Manipulation
- "Ignore previous instructions"
- "Disregard all previous"
- "Forget everything"
- Jailbreak attempts

### 3. Code Execution
- `__import__`
- `subprocess`
- `os.system`
- `exec()`, `eval()`

## ⚠️ Error Handling

### Critical Validation Errors

```python
try:
    user_prompt, report = prompts.format_and_validate_user_prompt(
        "<script>alert('xss')</script>Test",
        validate=True
    )
except ValueError as e:
    # Critical errors block execution
    print(f"BLOCKED: {e}")
    # Log the attempt for security monitoring
    logger.error(f"Security threat detected: {e}")
```

### Validation Disabled Error

```python
prompts = PlaywrightAgentPrompts(enable_validation=False)

try:
    report = prompts.validate_user_prompt("Test")
except RuntimeError as e:
    # Validation is disabled
    print(f"Error: {e}")
    # Enable validation first
    prompts.enable_validation()
```

## 🎯 Best Practices

### 1. Always Validate User Input

```python
# BAD - No validation
prompts = PlaywrightAgentPrompts(enable_validation=False)
user_prompt, _ = prompts.format_and_validate_user_prompt(user_input, validate=False)

# GOOD - With validation
prompts = PlaywrightAgentPrompts(enable_validation=True)
user_prompt, report = prompts.format_and_validate_user_prompt(user_input, validate=True)
```

### 2. Use Strict Mode in Production

```python
# Development
dev_config = PromptValidationConfig(strict_mode=False)
dev_prompts = PlaywrightAgentPrompts(enable_validation=True, validation_config=dev_config)

# Production
prod_config = PromptValidationConfig(strict_mode=True, check_injections=True)
prod_prompts = PlaywrightAgentPrompts(enable_validation=True, validation_config=prod_config)
```

### 3. Log Security Issues

```python
import logging

logger = logging.getLogger(__name__)

try:
    user_prompt, report = prompts.format_and_validate_user_prompt(test_desc, validate=True)
    
    # Log critical issues
    critical = report.get_by_level(ValidationLevel.CRITICAL)
    if critical:
        logger.warning(
            "Critical validation issues detected",
            extra={
                "test_description": test_desc[:100],
                "issues": [r.message for r in critical]
            }
        )

except ValueError as e:
    logger.error(f"Validation blocked execution: {e}")
```

### 4. Sanitize Before Storage

```python
# Clean prompts before saving
test_description = get_user_input()
clean_description = prompts.sanitize(test_description)

# Save the sanitized version
database.save_test_case(clean_description)
```

## 🔗 Integration with Playwright Runner

```python
from llmops.generators.playwright_prompts import PlaywrightAgentPrompts

class PlaywrightRunner:
    def __init__(self):
        self.prompts = PlaywrightAgentPrompts(enable_validation=True)
    
    def execute_test_case(self, test_description: str):
        try:
            # Validate and format prompts
            system_prompt, _ = self.prompts.get_validated_system_prompt(validate=True)
            user_prompt, user_report = self.prompts.format_and_validate_user_prompt(
                test_description,
                validate=True
            )
            
            if not user_report.is_valid:
                raise ValueError(f"Invalid test description: {user_report}")
            
            # Execute with validated prompts
            response = self.llm.invoke(user_prompt)
            return response
        
        except ValueError as e:
            # Handle validation errors
            print(f"Validation failed: {e}")
            raise
```

## 📚 Static Methods (No Validation)

These static methods remain available for backward compatibility:

```python
# Get system prompt without validation
system_prompt = PlaywrightAgentPrompts.get_system_prompt()

# Get tool usage format
format_str = PlaywrightAgentPrompts.get_tool_usage_format()

# Get tool examples
examples = PlaywrightAgentPrompts.get_tool_examples()

# Get available tools
tools = PlaywrightAgentPrompts.get_available_tools_description()

# Format tool call
tool_call = PlaywrightAgentPrompts.format_tool_call("playwright_navigate", {"url": "https://example.com"})
```

## 🔬 Testing

Run the comprehensive test suite:

```bash
cd backend/app
python llmops/generators/test_playwright_prompts_validation.py
```

This will run 8 examples covering:
1. Basic usage with validation
2. Security validation (detecting malicious content)
3. Tool call validation
4. Custom validation configuration
5. Quick validation checks
6. Prompt sanitization
7. Enable/disable validation dynamically
8. Complete workflow with validation

## 📖 Additional Resources

- **Main Module**: `llmops/generators/playwright_prompts.py`
- **Validation Tool**: `llmops/prompts/prompt_validation_tool.py`
- **Test Examples**: `llmops/generators/test_playwright_prompts_validation.py`
- **Validation Quick Reference**: `PROMPT_VALIDATION_QUICK_REFERENCE.md`

## 🔐 Security Notes

1. **Always enable validation for user input** in production
2. **Use strict mode** to catch more potential issues
3. **Log validation failures** for security monitoring
4. **Sanitize prompts** before storage
5. **Review critical errors** immediately - they indicate serious security threats
6. **Validate tool calls** especially those with user-provided arguments
7. **Monitor token usage** to prevent excessive LLM costs

## 💡 Tips

- Enable validation by default: `PlaywrightAgentPrompts(enable_validation=True)`
- Use `quick_validate()` for fast checks when you don't need detailed reports
- Use `sanitize()` to automatically clean dangerous content
- Check `report.is_valid` before proceeding with LLM calls
- Review critical and error-level validation results carefully
- Use custom configs for different environments (dev/prod)
