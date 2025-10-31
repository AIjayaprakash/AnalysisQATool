# Playwright LangGraph Automation Agent

A powerful automation testing agent that uses LangGraph and Groq LLM to perform browser automation using Playwright MCP tools from VS Code's MCP integration.

## Architecture

This agent leverages the **Playwright MCP server** configured in `.vscode/mcp.json`:
- The `@playwright/mcp` server is automatically started by VS Code
- Tools are accessed through VS Code's MCP integration (not HTTP endpoints)
- The agent uses actual browser automation via the MCP protocol
- No need to manage separate HTTP servers or ports

## MCP Configuration

The Playwright MCP server is configured in `.vscode/mcp.json`:
```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    }
  }
}
```

This configuration ensures the Playwright browser tools are available when running the agent through VS Code.

## Recent Fixes (Oct 31, 2025)

### Fixed Infinite Loop Issue
**Problem**: Agent was looping infinitely and hitting token limits (8000 TPM) with error 413.

**Root Cause**: 
1. After executing tools, the agent would return to planning with all previous messages
2. The LLM would see tool responses and generate new plans indefinitely
3. Context grew exponentially until hitting rate limits

**Solutions Applied**:
1. ✅ **Max Iterations Guard** - Added `max_iterations` parameter (default: 10) to prevent infinite loops
2. ✅ **Proper Completion Detection** - LLM now signals completion by responding WITHOUT tool calls
3. ✅ **Improved Prompting** - Agent explicitly asks LLM to summarize when test is complete
4. ✅ **Better should_continue Logic** - Checks completion status before routing to next node
5. ✅ **Switched to Smaller Model** - Changed from `openai/gpt-oss-120b` to `llama-3.3-70b-versatile` to avoid rate limits

### Latest Fix: Message Flow Error (Error 400)

**Problem**: Error when using Groq with manual tool calls:
```
Error code: 400 - messages with role 'tool' must be a response to a preceeding message with 'tool_calls'
```

**Root Cause**: Creating `ToolMessage` objects without proper `tool_calls` in preceding message violates LangChain message flow rules.

**Solution**: Use different message types for different LLM providers:

#### OpenAI Flow (Native Function Calls):
```
1. HumanMessage: "Navigate to example.com"
2. AIMessage: tool_calls=[{name: "navigate", args: {...}}]  
3. ToolMessage: "Navigation completed" ✅ Valid
```

#### Groq Flow (Manual Parsing):
```
1. HumanMessage: "Navigate to example.com"
2. AIMessage: "TOOL_CALL: navigate\nARGS: {...}"
3. AIMessage: "Tool execution results:\n✓ Executed navigate" ✅ Valid
```

**Changes Applied**:
1. **OpenAI**: Uses `ToolMessage` with proper `tool_calls` flow
2. **Groq**: Uses `AIMessage` to avoid message flow violations
3. **Auto-detection**: Tries OpenAI first, falls back to Groq safely

### Model Configuration
- **Preferred**: OpenAI GPT-4 (native function calling support)
- **Fallback**: Groq `llama-3.3-70b-versatile` with custom parsing
- **Previous**: Direct Groq binding (caused 400 errors)

cd backend/app/agents
pip install -r requirements.txt
## Features

- **24+ Playwright MCP Tools** integrated as LangChain tools
- **Natural Language Interface** - describe tests in plain English
- **Intelligent Planning** - AI breaks down complex tests into steps
- **Error Handling** - graceful error recovery and reporting
- **State Management** - tracks execution progress and results

## Available Tools

### Navigation
- `browser_navigate` - Navigate to URLs
- `browser_navigate_back` - Go back in history

### Element Interaction
- `browser_click` - Click elements
- `browser_type` - Type text with delays
- `browser_fill_form` - Fill multiple form fields
- `browser_hover` - Hover over elements

### Selection & Input
- `browser_select_option` - Select dropdown options
- `browser_press_key` - Press keyboard keys
- `browser_file_upload` - Upload files

### Inspection
- `browser_snapshot` - Capture accessibility tree
- `browser_take_screenshot` - Take screenshots
- `browser_console_messages` - Get console logs
- `browser_network_requests` - Get network activity

### Advanced
- `browser_evaluate` - Execute JavaScript
- `browser_drag` - Drag and drop
- `browser_wait_for` - Wait for conditions
- `browser_handle_dialog` - Handle alerts/confirms

### Management
- `browser_tabs` - Manage browser tabs
- `browser_resize` - Resize browser window
- `browser_close` - Close browser

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"  # Linux/Mac
$env:OPENAI_API_KEY="your-api-key-here"   # PowerShell

# Ensure Playwright MCP server is configured in .vscode/mcp.json
```

## Usage

### Interactive Mode

```bash
python backend/app/agents/run_test.py
```

Select from predefined scenarios or create custom tests.

### Programmatic Usage

```python
from playwright_langgraph_agent import run_automation_test

# Run a test with natural language prompt
result = await run_automation_test(
    "Navigate to https://example.com, click the 'More information' link, "
    "and take a screenshot"
)

print(f"Status: {result['status']}")
print(f"Steps: {result['steps_executed']}")
```

## Example Prompts

### Simple Navigation
```
"Open https://example.com and take a screenshot"
```

### Form Testing
```
"Go to the login page at https://app.com/login, 
fill username with 'testuser' and password with 'pass123', 
then click the Sign In button"
```

### Search Testing
```
"Navigate to Google, search for 'Playwright automation', 
wait for results, and click the first result"
```

### E-commerce Testing
```
"Go to Amazon, search for 'laptop', 
click the first product, 
scroll to reviews section, 
and take a screenshot"
```

### Multi-Step Workflow
```
"Open GitHub, click Sign in, 
fill the login form (username: test@example.com), 
take a screenshot, 
then navigate back to homepage"
```

## Advanced Features

### Custom Selectors
The agent supports multiple selector types:
- **CSS**: `.class-name`, `#element-id`, `button.primary`
- **Text**: `text=Sign In`, `text=Click me`
- **XPath**: `//button[@type='submit']`, `//div[contains(text(), 'Hello')]`

### Error Handling
The agent automatically:
- Retries failed operations
- Provides detailed error messages
- Continues execution when possible
- Logs all errors for debugging

### State Tracking
Each test run tracks:
- Steps executed
- Tool calls made
- Timestamps
- Results for each step
- Any errors encountered

## Architecture

```
User Prompt
    ↓
[Parse & Plan Node]
    ↓
[LLM creates test plan with tool calls]
    ↓
[Execute Tools Node]
    ↓
[Playwright MCP tools execute]
    ↓
[Should Continue?] ─→ [More steps] ─→ Loop back
    ↓
[Test Complete]
```

## Configuration

### LLM Model
Edit `playwright_langgraph_agent.py`:
```python
llm = ChatOpenAI(
    model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### MCP Server URL
Edit `PlaywrightMCPClient`:
```python
def __init__(self, mcp_url: str = "http://localhost:3000"):
    self.mcp_url = mcp_url
```

## Troubleshooting

### "No API key provided"
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-..."
```

### "MCP server not responding"
Ensure the Playwright MCP server is running:
```bash
npx -y @playwright/mcp
```

### "Element not found"
- Try different selector types (CSS, text, XPath)
- Add waits before interacting: `browser_wait_for`
- Use `browser_snapshot` to see page structure

## Best Practices

1. **Be Specific**: Provide clear, detailed test descriptions
2. **Use Waits**: Add explicit waits for dynamic content
3. **Verify Results**: Include verification steps in prompts
4. **Handle Errors**: Describe expected errors in prompts
5. **Take Screenshots**: Capture evidence at key steps

## Examples Directory Structure

```
backend/app/agents/
├── playwright_langgraph_agent.py  # Main agent implementation
├── run_test.py                     # Interactive test runner
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Current Status: Tool Call Generation Working ✅

The agent successfully generates proper MCP tool calls and completes automation flows:

```
[DEBUG] -> execute_tools (manual format)
  -> Step 0: Executing 1 MCP tool(s): functions.mcp_playwright_browser_navigate
  -> Step 1: Executing 1 MCP tool(s): functions.mcp_playwright_browser_take_screenshot
Status: success, Steps Executed: 2
```

### Why No Real Screenshots Yet?

The agent currently **simulates** tool execution for testing purposes. To get real browser automation:

#### Option 1: VS Code MCP Integration (Recommended)
- Run the agent within VS Code's integrated environment
- VS Code's MCP runtime will intercept tool calls automatically  
- The @playwright/mcp server (configured in `.vscode/mcp.json`) will execute real browser actions
- Screenshots will be saved to the workspace

#### Option 2: Direct MCP Server Connection
- Start the @playwright/mcp server manually: `npx -y @playwright/mcp`
- Update the agent to make HTTP calls to the MCP server
- Replace simulated responses with actual MCP server responses

### Next Steps for Real Execution
1. **Verify MCP server**: `npx -y @playwright/mcp --help`
2. **Test manual execution**: Use the MCP tools available in this VS Code environment
3. **Integration**: Connect the agent's tool calls to the running MCP server

## Contributing

To add new tools or features:
1. Define tool with `@tool` decorator
2. Add to `all_tools` list
3. Update system prompt with tool description
4. Test with example prompts

## License

MIT License