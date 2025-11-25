# Dynamic Browser Type Implementation

## Overview
Browser type is now **fully dynamic** and flows from the test case definition through the entire execution chain. The browser type is NOT hardcoded and does NOT come from the config file during test execution.

## Flow Diagram
```
test_case['browser_type'] (test_metadata_extraction.py)
    ↓
TestCaseRequest.browser_type (llmops_api.py)
    ↓
PlaywrightExecutionRequest.browser_type (llmops_api.py)
    ↓
agent.run(browser_config={'browser_type': request.browser_type})
    ↓
playwright_state.initialize(browser_type)
    ↓
Playwright launches the specified browser
```

## Supported Browsers
- `chromium` - Default Chromium browser
- `firefox` - Mozilla Firefox
- `webkit` - Safari WebKit
- `edge` - Microsoft Edge (uses msedge channel)

## Implementation Details

### 1. Test Case Definition (test_metadata_extraction.py)
```python
test_case = {
    "test_id": "TC_METADATA_001",
    "application_url": "https://example.com",
    "browser_type": "edge"  # Dynamic: chromium, firefox, webkit, or edge
}
```

**Key Point:** Browser type is specified in the test case itself, making it dynamic per test.

### 2. API Model (llmops_api.py - Line 57-65)
```python
class TestCaseRequest(BaseModel):
    test_id: str
    application_url: str
    user_actions: List[str]
    expected_results: List[str]
    browser_type: str = Field(
        default="chromium",
        description="Browser type to use: chromium, firefox, webkit, or edge"
    )
    headless: bool = True
```

**Key Point:** TestCaseRequest accepts browser_type from the incoming request.

### 3. Execution Request (llmops_api.py - Line 903)
```python
exec_request = PlaywrightExecutionRequest(
    test_id=request.test_id,
    generated_prompt=generated_prompt,
    browser_type=request.browser_type,  # From test case, NOT config
    headless=False
)
```

**Key Point:** Browser type flows from TestCaseRequest to PlaywrightExecutionRequest.

### 4. Agent Execution (llmops_api.py - Line 705)
```python
result = await agent.run(
    test_prompt=request.generated_prompt,
    max_iterations=request.max_iterations,
    browser_config={
        "browser_type": request.browser_type,  # From request, NOT config
        "headless": request.headless
    }
)
```

**Key Point:** Agent receives browser_type from request, ensuring dynamic browser selection.

### 5. Logging (llmops_api.py - Line 682, 707)
```python
# Log the browser type being used
log_info(
    f"Executing Playwright automation for test: {request.test_id}",
    node="playwright",
    extra={
        "test_id": request.test_id,
        "browser_type": request.browser_type,  # From request
        "headless": request.headless,
        "max_iterations": request.max_iterations
    }
)

log_info(
    f"Using browser type from request: {request.browser_type}",
    node="playwright",
    extra={"browser_type": request.browser_type}
)
```

**Key Point:** Logs show the actual browser type from the request, not the config default.

## What About config.browser_type?

### Config Browser Type Usage
The `config.browser_type` is ONLY used for:
1. **Startup logging** (llmops_api.py line 943) - Shows the default browser type in system configuration
2. **Test files** (test_agent_providers.py, test_app_env.py) - Shows environment configuration

### Execution Browser Type Usage
During actual test execution, `request.browser_type` is used, which comes from the test case.

## Testing Different Browsers

### Example 1: Test with Edge
```python
test_case = {
    "test_id": "TC_001",
    "application_url": "https://example.com",
    "browser_type": "edge",  # Edge browser
    # ... other fields
}
```

### Example 2: Test with Firefox
```python
test_case = {
    "test_id": "TC_002",
    "application_url": "https://example.com",
    "browser_type": "firefox",  # Firefox browser
    # ... other fields
}
```

### Example 3: Test with Chromium
```python
test_case = {
    "test_id": "TC_003",
    "application_url": "https://example.com",
    "browser_type": "chromium",  # Chromium browser (default)
    # ... other fields
}
```

## Verification

To verify the browser type is dynamic:

1. **Check logs** - Look for:
   ```
   Executing Playwright automation for test: TC_XXX
   extra: {"browser_type": "edge"}
   
   Using browser type from request: edge
   ```

2. **Observe browser launch** - The actual browser window should match the specified type

3. **Test multiple browsers** - Run the same test with different `browser_type` values

## Common Issues

### Issue: Browser type still using config value
**Cause:** Old code using `config.browser_type` instead of `request.browser_type`

**Solution:** Verify these files use `request.browser_type`:
- llmops_api.py line 682 (logging)
- llmops_api.py line 705 (agent execution) - **MOST CRITICAL**
- llmops_api.py line 903 (execution request creation)

### Issue: Edge browser not launching
**Cause:** Microsoft Edge not installed or msedge channel not available

**Solution:** 
```bash
# Install Edge browser channel for Playwright
python -m playwright install msedge
```

## Summary

✅ **Browser type is fully dynamic**
- Specified in test_case, not config file
- Flows through: test_case → API → agent → playwright_state
- Supports 4 browsers: chromium, firefox, webkit, edge
- Each test can use a different browser

✅ **No hardcoded values**
- All execution paths use `request.browser_type`
- Config browser type only used for startup logging (showing defaults)
- Logs show actual browser type from request

✅ **Easy to test**
- Change `browser_type` in test_case
- No code changes needed
- Supports parallel testing with different browsers
