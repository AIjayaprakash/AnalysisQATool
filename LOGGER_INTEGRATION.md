# Logger Integration Guide

## Overview
The logger module has been integrated throughout the application to provide comprehensive logging of operations, errors, and debug information.

## Logger Module Location
```
backend/app/llmops/common/logger.py
```

## Available Logging Functions

### 1. **get_logger(name)**
Initialize and return a configured logger instance.
```python
from llmops.common.logger import get_logger

logger = get_logger(__name__)
logger.info("Custom message")
```

### 2. **log_info(message, logger_name, node, extra)**
Log informational messages with optional node context.
```python
from llmops.common.logger import log_info

log_info("User logged in", node="auth", extra={"user_id": 123})
```

### 3. **log_warning(message, logger_name, extra)**
Log warning messages.
```python
from llmops.common.logger import log_warning

log_warning("API rate limit approaching", extra={"remaining": 10})
```

### 4. **log_error(message, logger_name, error, extra)**
Log error messages with exception details.
```python
from llmops.common.logger import log_error

try:
    # some operation
    pass
except Exception as e:
    log_error("Operation failed", error=e, extra={"context": "data"})
```

### 5. **log_debug(message, logger_name, extra)**
Log debug messages.
```python
from llmops.common.logger import log_debug

log_debug("Variable check", extra={"value": some_var})
```

### 6. **log_llm(message, operation, model, tokens, extra)**
Log LLM-specific operations.
```python
from llmops.common.logger import log_llm

log_llm("Generated response", operation="completion", model="gpt-4o", tokens=150)
```

### 7. **log_langfuse(message, trace_id, span_id, extra)**
Log Langfuse integration events.
```python
from llmops.common.logger import log_langfuse

log_langfuse("Trace started", trace_id="abc123", span_id="def456")
```

### 8. **log_db(message, operation, table, rows_affected, extra)**
Log database operations.
```python
from llmops.common.logger import log_db

log_db("Query executed", operation="SELECT", table="users", rows_affected=10)
```

### 9. **log_prompt(message, prompt_type, prompt_length, template, extra)**
Log prompt-related operations.
```python
from llmops.common.logger import log_prompt

log_prompt("Prompt generated", prompt_type="system", prompt_length=200)
```

## Integration Points

### 1. **API Endpoints** (llmops_api.py)

#### Health Check
```python
@app.get("/health")
async def health_check():
    log_info("Health check requested", node="api")
    # ... endpoint logic
```

#### Generate Prompt
```python
@app.post("/generate-prompt")
async def generate_single_prompt(request: TestCaseRequest):
    log_info(
        f"Generating prompt for test case: {request.test_id}",
        node="api.generate_prompt",
        extra={"module": request.module}
    )
    
    log_llm("Calling LLM to generate prompt", operation="generate_prompt")
    # ... generate prompt
    
    log_prompt("Prompt generated successfully", prompt_length=len(prompt))
```

#### Execute Playwright
```python
@app.post("/execute-playwright")
async def execute_playwright_automation(request: PlaywrightExecutionRequest):
    log_info(
        f"Starting Playwright automation for test: {request.test_id}",
        node="api.execute_playwright",
        extra={"browser_type": config.browser_type, "headless": request.headless}
    )
    
    try:
        # ... execution logic
        log_info(f"Automation {status} - Extracted {len(pages)} pages", node="playwright")
    except Exception as e:
        log_error(f"Playwright automation failed", error=e, extra={"test_id": request.test_id})
```

#### Server Startup
```python
if __name__ == "__main__":
    log_info(
        "Starting LLMOps API Server",
        node="startup",
        extra={
            "app_env": config.app_env,
            "provider": provider_info['provider'],
            "model": provider_info['model']
        }
    )
```

### 2. **Playwright Agent** (playwright_agent.py)
```python
# Add to agent operations
log_info("Initializing Playwright Agent", node="playwright_agent")
log_llm("Executing LLM call", operation="agent_run", model=self.model)
```

### 3. **Test Case Generator** (generators/)
```python
# Add to generator methods
log_llm("Generating test case prompt", operation="generation", model=config.model)
log_prompt("Prompt template applied", template="test_case_template")
```

### 4. **Excel Processing** (excel_reader.py, excel_writer.py)
```python
# Add to Excel operations
log_info(f"Reading Excel file: {file_path}", node="excel_reader")
log_info(f"Writing {len(test_cases)} test cases to Excel", node="excel_writer")
```

### 5. **Database Operations** (db.py)
```python
# Add to database operations
log_db("Connecting to database", operation="CONNECT")
log_db("Query executed", operation="SELECT", table="test_cases", rows_affected=10)
log_db("Data inserted", operation="INSERT", table="results", rows_affected=1)
```

## Log Files

### Location
```
logs/
├── 2025-11-24_app.log
├── 2025-11-25_app.log
└── ...
```

### Log Format
**Console Output:**
```
2025-11-24 12:30:11,442 - app - INFO - [main] Application started
```

**File Output (with detailed info):**
```
2025-11-24 12:30:11,442 - app - INFO - [llmops_api.py:152] - [api] Health check requested
```

### Color Coding (Console)
- **DEBUG**: Cyan
- **INFO**: Green  
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Magenta

## Usage Examples

### Example 1: API Request Flow
```python
# Incoming request
log_info("Received generate-prompt request", node="api", extra={"test_id": "TC001"})

# LLM call
log_llm("Calling OpenAI", operation="completion", model="gpt-4o", tokens=100)

# Success
log_info("Prompt generated successfully", node="api")
log_prompt("Generated prompt", prompt_length=500)
```

### Example 2: Error Handling
```python
try:
    # Some operation
    result = perform_operation()
    log_info("Operation completed successfully", node="operation")
except ValueError as e:
    log_error("Validation error", error=e, extra={"input": data})
except Exception as e:
    log_error("Unexpected error", error=e)
```

### Example 3: Database Operations
```python
log_db("Querying test cases", operation="SELECT", table="test_cases")
results = db.query("SELECT * FROM test_cases")
log_db("Query completed", operation="SELECT", table="test_cases", rows_affected=len(results))
```

### Example 4: Playwright Automation
```python
log_info("Starting browser automation", node="playwright")
log_info("Navigating to URL", node="playwright", extra={"url": target_url})
log_info("Extracting metadata", node="playwright")
log_info(f"Found {len(elements)} elements", node="playwright", extra={"page": page_title})
```

## Best Practices

### 1. **Use Appropriate Log Levels**
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures

### 2. **Include Context**
Always include relevant context with `extra` parameter:
```python
log_info("Processing test case", extra={
    "test_id": test_id,
    "module": module,
    "priority": priority
})
```

### 3. **Use Specific Loggers**
- `log_llm()` for LLM operations
- `log_db()` for database operations
- `log_prompt()` for prompt operations
- `log_info()` with `node` for general application flow

### 4. **Log at Key Decision Points**
```python
# Before operation
log_info("Starting operation", node="processor")

# Success path
log_info("Operation completed successfully", node="processor")

# Error path
log_error("Operation failed", error=e, node="processor")
```

### 5. **Don't Log Sensitive Data**
```python
# ❌ Bad - logs API key
log_info(f"Using API key: {api_key}")

# ✅ Good - logs masked value
log_info(f"Using API key: {api_key[:8]}***")
```

## Configuration

### Enable/Disable File Logging
```python
logger = get_logger(__name__, log_to_file=False)
```

### Change Log Level
```python
logger = get_logger(__name__, level=logging.DEBUG)
```

### Disable Colors
```python
logger = get_logger(__name__, use_colors=False)
```

## Testing

Run the logger test:
```bash
python backend/app/llmops/common/logger.py
```

Check log files:
```bash
ls logs/
cat logs/2025-11-24_app.log
```

## Next Steps

### Additional Integration Points

1. **Browser Tools** (playwright_tools.py)
   - Log each tool execution
   - Log navigation events
   - Log element interactions

2. **LLM Providers** (llm/providers.py)
   - Log API calls with token counts
   - Log rate limiting events
   - Log provider switches

3. **Test Runners** (runner.py)
   - Log test execution start/end
   - Log test results
   - Log performance metrics

4. **Configuration** (config.py)
   - Log configuration loading
   - Log environment variable usage
   - Log validation errors

## Monitoring and Analysis

### View Recent Logs
```bash
tail -f logs/$(date +%Y-%m-%d)_app.log
```

### Search for Errors
```bash
grep "ERROR" logs/*.log
```

### Filter by Node
```bash
grep "\[playwright\]" logs/*.log
```

### Count Log Levels
```bash
grep -c "INFO" logs/2025-11-24_app.log
grep -c "ERROR" logs/2025-11-24_app.log
```

## Summary

✅ **Logger module created** with all required functions  
✅ **Integrated into llmops_api.py** for API endpoints  
✅ **Colored console output** for better readability  
✅ **File logging** with daily rotation  
✅ **Specialized loggers** for LLM, DB, Prompt, and Langfuse operations  

The logging system is now ready to use throughout the application!
