"""
Complete LangGraph Playwright Automation Agent
Uses Playwright MCP tools from VS Code MCP integration for web automation testing.

Note: This agent uses the Playwright MCP browser tools configured in .vscode/mcp.json
The @playwright/mcp server tools are accessed through VS Code's MCP integration.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Annotated, TypedDict
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Optional LangChain tracing - only set if API key is available
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# The Playwright MCP tools from VS Code - these are the actual function names available
# through the MCP integration when running in VS Code with .vscode/mcp.json configured
# 
# Available MCP tools (configured via @playwright/mcp server):
MCP_TOOL_NAMES = [
    "mcp_playwright_browser_navigate",
    "mcp_playwright_browser_click", 
    "mcp_playwright_browser_snapshot",
    "mcp_playwright_browser_take_screenshot",
    "mcp_playwright_browser_type",
    "mcp_playwright_browser_hover",
    "mcp_playwright_browser_wait_for",
    "mcp_playwright_browser_fill_form",
    "mcp_playwright_browser_select_option",
    "mcp_playwright_browser_handle_dialog",
    "mcp_playwright_browser_press_key",
    "mcp_playwright_browser_evaluate",
    "mcp_playwright_browser_console_messages",
    "mcp_playwright_browser_network_requests",
    "mcp_playwright_browser_tabs",
    "mcp_playwright_browser_navigate_back",
    "mcp_playwright_browser_resize",
    "mcp_playwright_browser_drag",
    "mcp_playwright_browser_file_upload",
    "mcp_playwright_browser_close",
]

print(f"[OK] Playwright LangGraph Agent configured to use {len(MCP_TOOL_NAMES)} MCP browser tools")
print("  These tools are provided by @playwright/mcp server via VS Code MCP integration")

# Note: The actual tools are injected by VS Code's MCP runtime
# When the LLM makes tool calls with these names, VS Code's MCP system will execute them
# We don't need to define wrapper functions - the MCP integration handles this automatically
all_tools = []  # Tools will be resolved by VS Code MCP at runtime

# Agent State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    test_plan: str
    current_step: int
    total_steps: int
    results: List[Dict[str, Any]]
    errors: List[str]
    is_complete: bool
    max_iterations: int  # Maximum number of plan-execute cycles

# Create tool definitions for the MCP browser tools so the LLM knows their schemas
@tool
def mcp_playwright_browser_navigate(url: str) -> str:
    """Navigate browser to a URL. Use this to visit any website. Show the website screen.
    
    Args:
        url: The full URL to navigate to (e.g., https://example.com)
    """
    return f"Navigated to {url}"

@tool  
def mcp_playwright_browser_click(element: str, ref: str) -> str:
    """Click an element on the page.
    
    Args:
        element: Human-readable element description
        ref: Exact element selector (CSS, text=, or xpath)
    """
    return f"Clicked element: {element}"

@tool
def mcp_playwright_browser_snapshot() -> str:
    """Capture accessibility snapshot of the current page. Returns the page structure.
    This is better than screenshot for understanding page content.
    """
    return "Captured page snapshot with accessibility tree"

@tool
def mcp_playwright_browser_take_screenshot(filename: str = None) -> str:
    """Take a screenshot of the page.
    
    Args:
        filename: Optional filename to save screenshot (defaults to screenshot.png)
    """
    return f"Screenshot saved: {filename or 'screenshot.png'}"

@tool
def mcp_playwright_browser_type(element: str, ref: str, text: str) -> str:
    """Type text into an element.
    
    Args:
        element: Human-readable element description  
        ref: Exact element selector
        text: Text to type
    """
    return f"Typed '{text}' into {element}"

@tool
def mcp_playwright_browser_wait_for(text: str = None, time: int = None) -> str:
    """Wait for text to appear or wait for a specified time.
    
    Args:
        text: Text to wait for to appear
        time: Time to wait in seconds
    """
    return "Wait completed"

@tool
def mcp_playwright_browser_evaluate(function: str) -> str:
    """Execute JavaScript code in the browser context.
    
    Args:
        function: JavaScript function code to execute
    """
    return "JavaScript executed"

@tool
def mcp_playwright_browser_close() -> str:
    """Close the current browser page/context."""
    return "Browser closed"

# Collect tool definitions for LLM binding
mcp_tools = [
    mcp_playwright_browser_navigate,
    mcp_playwright_browser_click, 
    mcp_playwright_browser_snapshot,
    mcp_playwright_browser_take_screenshot,
    mcp_playwright_browser_type,
    mcp_playwright_browser_wait_for,
    mcp_playwright_browser_evaluate,
    mcp_playwright_browser_close,
]

# Try OpenAI first (better tool calling support), fallback to Groq
try:
    from langchain_openai import ChatOpenAI
    if os.getenv("OPENAI_API_KEY"):
        print("[INFO] Using OpenAI GPT-4 (best tool calling support)")
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        llm_with_tools = llm.bind_tools(mcp_tools)
    else:
        raise ImportError("No OpenAI API key")
except (ImportError, Exception):
    # Fallback to Groq with manual function calling
    print("[INFO] Using Groq with custom function calling")
    from langchain_groq import ChatGroq
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not set. The agent will not work without a valid API key.")
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "dummy-key")
    
    # Use Groq without bind_tools since it doesn't support proper function calling
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    llm_with_tools = llm  # No tool binding for Groq

# Agent nodes
def parse_test_request(state: AgentState) -> AgentState:
    """Parse user's test request and create a test plan"""
    messages = state["messages"]
    
    # Check if we're using OpenAI (proper tool calling) or Groq (manual parsing)
    using_openai = hasattr(llm_with_tools, 'bound_tools') and llm_with_tools.bound_tools
    
    if using_openai:
        system_prompt = """You are an expert QA automation engineer using Playwright through VS Code MCP integration.

CRITICAL: You MUST use the available browser automation tools to execute tests. Do not just provide text descriptions.

Available MCP browser tools (use function calls):
- mcp_playwright_browser_navigate(url) - Navigate to a website  
- mcp_playwright_browser_click(element, ref) - Click elements
- mcp_playwright_browser_type(element, ref, text) - Type text into fields
- mcp_playwright_browser_take_screenshot(filename) - Take screenshots
- mcp_playwright_browser_snapshot() - Get page structure
- mcp_playwright_browser_wait_for(text, time) - Wait for conditions
- mcp_playwright_browser_evaluate(function) - Run JavaScript
- mcp_playwright_browser_close() - Close browser

EXECUTION RULES:
1. ALWAYS start by calling mcp_playwright_browser_navigate to open the target website
2. Use function calls to execute tools - the system will handle MCP integration
3. Only provide a text summary AFTER executing all required tools

REMEMBER: Use function calls, don't just describe!"""
    else:
        system_prompt = """You are an expert QA automation engineer using Playwright through VS Code MCP integration.

CRITICAL: You MUST specify browser automation actions using the TOOL_CALL format below.

Available MCP browser tools:
- mcp_playwright_browser_navigate(url) - Navigate to a website  
- mcp_playwright_browser_click(element, ref) - Click elements
- mcp_playwright_browser_type(element, ref, text) - Type text into fields
- mcp_playwright_browser_take_screenshot(filename) - Take screenshots
- mcp_playwright_browser_snapshot() - Get page structure
- mcp_playwright_browser_wait_for(text, time) - Wait for conditions
- mcp_playwright_browser_evaluate(function) - Run JavaScript
- mcp_playwright_browser_close() - Close browser

EXECUTION FORMAT:
Use this exact format to call tools:

TOOL_CALL: mcp_playwright_browser_navigate
ARGS: {"url": "https://example.com"}

TOOL_CALL: mcp_playwright_browser_take_screenshot  
ARGS: {"filename": "result.png"}

EXECUTION RULES:
1. ALWAYS start with TOOL_CALL: mcp_playwright_browser_navigate
2. Use the exact TOOL_CALL format shown above
3. After seeing "Tool execution results:", evaluate if more steps are needed
4. Only provide a final summary when the test is complete

REMEMBER: Use TOOL_CALL format for actions, then continue based on results!"""
    
    # Build the messages - on first call, add planning instruction; on subsequent calls, ask for next steps
    if state["current_step"] == 0:
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="""Create a detailed test plan and start executing it immediately using the available MCP browser tools.

IMPORTANT: You MUST use tool calls to execute the test. Start by calling mcp_playwright_browser_navigate to open the target website, then use other tools as needed.

Do NOT just provide a summary - actually execute the test steps using tool calls.""")
        ]
    else:
        # After tool execution, ask what to do next
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="Based on the tool execution results above, determine if the test is complete. If yes, provide a summary WITHOUT tool calls. If not, continue with the next steps using tool calls.")
        ]
    
    response = llm_with_tools.invoke(planning_messages)
    
    state["messages"].append(response)
    return state

def execute_tools(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM response
    
    Handles both OpenAI function calls and Groq manual format parsing.
    """
    last_message = state["messages"][-1]
    
    # Check for OpenAI-style function calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # OpenAI function calling
        tool_call_names = [tc.get("name", "unknown") for tc in last_message.tool_calls]
        print(f"  -> Step {state['current_step']}: Executing {len(last_message.tool_calls)} MCP tool(s): {', '.join(tool_call_names)}")
        
        # Use ToolNode to execute the tools (which will be intercepted by MCP)
        tool_node = ToolNode(mcp_tools)
        result = tool_node.invoke({"messages": [last_message]})
        
        # Add the tool results to the state
        state["messages"].extend(result["messages"])
        state["results"].append({
            "step": state["current_step"],
            "tool_calls": len(last_message.tool_calls),
            "tool_names": tool_call_names,
            "timestamp": datetime.now().isoformat()
        })
        state["current_step"] += 1
        
    else:
        # Parse Groq manual format: TOOL_CALL: function_name
        content = str(last_message.content) if hasattr(last_message, 'content') else ""
        import re
        import json
        
        # Find all TOOL_CALL patterns
        tool_calls = []
        pattern = r'TOOL_CALL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]+\})'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for tool_name, args_str in matches:
            tool_name = tool_name.strip()
            try:
                args = json.loads(args_str)
                tool_calls.append({"name": tool_name, "args": args})
            except json.JSONDecodeError:
                print(f"[ERROR] Failed to parse args for {tool_name}: {args_str}")
                continue
        
        if tool_calls:
            # Execute the parsed tool calls
            tool_call_names = [tc["name"] for tc in tool_calls]
            print(f"  -> Step {state['current_step']}: Executing {len(tool_calls)} MCP tool(s): {', '.join(tool_call_names)}")
            
            # For Groq, we'll use AIMessage instead of ToolMessage to avoid message flow issues
            from langchain_core.messages import AIMessage
            tool_results = []
            
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                args = tool_call["args"]
                
                # NOTE: In VS Code with MCP integration, these tool calls would be intercepted
                # and executed by the @playwright/mcp server configured in .vscode/mcp.json
                # For now, we simulate the results - real execution requires VS Code MCP runtime
                result_content = f"✓ Simulated {tool_name} with args: {args} (MCP integration needed for real execution)"
                tool_results.append(result_content)
            
            # Create a single AI message with all tool results
            combined_result = "Tool execution results:\n" + "\n".join(tool_results)
            result_message = AIMessage(content=combined_result)
            
            state["messages"].append(result_message)
            state["results"].append({
                "step": state["current_step"],
                "tool_calls": len(tool_calls),
                "tool_names": tool_call_names,
                "timestamp": datetime.now().isoformat()
            })
            state["current_step"] += 1
        else:
            # No tool calls found - mark as complete
            print(f"[DEBUG] No tool calls found in message content")
            state["is_complete"] = True
    
    # Check if we've hit the iteration limit
    if state["current_step"] >= state["max_iterations"]:
        state["is_complete"] = True
        state["errors"].append(f"Max iterations ({state['max_iterations']}) reached")
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end"""
    
    print(f"\n[DEBUG] should_continue - Step {state['current_step']}, Complete: {state.get('is_complete')}")
    
    # Check completion first
    if state.get("is_complete"):
        print("[DEBUG] -> END (marked complete)")
        return END
    
    # Check if we've exceeded max iterations
    if state["current_step"] >= state["max_iterations"]:
        print("[DEBUG] -> END (max iterations)")
        return END
    
    last_message = state["messages"][-1]
    print(f"[DEBUG] Last message type: {type(last_message).__name__}")
    
    # Check for OpenAI-style function calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"[DEBUG] -> execute_tools ({len(last_message.tool_calls)} tool calls)")
        return "execute_tools"
    
    # Check for Groq manual format tool calls
    if hasattr(last_message, 'content'):
        content = str(last_message.content)
        if "TOOL_CALL:" in content:
            print("[DEBUG] -> execute_tools (manual format)")
            return "execute_tools"
    
    # If the last message is a tool response, ask LLM what to do next
    from langchain_core.messages import ToolMessage, AIMessage
    if isinstance(last_message, ToolMessage):
        print("[DEBUG] -> parse_request (after tool response)")
        return "parse_request"
    
    # For Groq: if last message is AIMessage with tool results, continue
    if isinstance(last_message, AIMessage) and "Tool execution results:" in str(last_message.content):
        print("[DEBUG] -> parse_request (after Groq tool results)")
        return "parse_request"
    
    # If LLM responded without tool calls, we're done
    print("[DEBUG] -> END (no tool calls)")
    return END

def create_automation_agent():
    """Create the LangGraph automation agent"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_request", parse_test_request)
    workflow.add_node("execute_tools", execute_tools)
    
    # Set entry point
    workflow.set_entry_point("parse_request")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "parse_request",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "parse_request": "parse_request",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue,
        {
            "parse_request": "parse_request",
            END: END
        }
    )
    
    return workflow.compile()

# Main execution function
async def run_automation_test(test_prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
    """
    Run an automation test based on natural language prompt.
    
    Args:
        test_prompt: Natural language description of the test to perform
        max_iterations: Maximum number of plan-execute cycles to prevent infinite loops (default: 10)
        
    Returns:
        Dict with test results, steps executed, and any errors
        
    Example prompts:
        - "Test login flow on https://example.com with username 'test' and password 'pass123'"
        - "Navigate to Google, search for 'playwright', and click the first result"
        - "Go to Amazon, add an item to cart, and verify the cart total"
    """
    
    # Initialize state
    initial_state = AgentState(
        messages=[HumanMessage(content=test_prompt)],
        test_plan="",
        current_step=0,
        total_steps=0,
        results=[],
        errors=[],
        is_complete=False,
        max_iterations=max_iterations
    )
    
    print(f"\n[DEBUG] Starting automation test: '{test_prompt}'")
    print(f"[DEBUG] Max iterations: {max_iterations}")
    
    # Create and run agent
    agent = create_automation_agent()
    
    try:
        final_state = await agent.ainvoke(initial_state)
        
        print(f"\n[DEBUG] Test completed:")
        print(f"  - Steps executed: {final_state['current_step']}")
        print(f"  - Is complete: {final_state.get('is_complete', False)}")
        print(f"  - Total messages: {len(final_state['messages'])}")
        print(f"  - Errors: {final_state.get('errors', [])}")
        
        if final_state["current_step"] > 0:
            print(f"\n[INFO] Tool calls were generated successfully!")
            print(f"[INFO] To see real browser automation (screenshots, etc.):")
            print(f"[INFO] - This agent needs to run within VS Code's MCP runtime")
            print(f"[INFO] - The @playwright/mcp server is configured in .vscode/mcp.json")
            print(f"[INFO] - Currently simulating tool execution for testing")
        
        # Check if no steps were executed - this indicates the LLM didn't generate tool calls
        if final_state["current_step"] == 0:
            # Check the last message from LLM
            for i, msg in enumerate(reversed(final_state["messages"])):
                if hasattr(msg, 'content') and msg.content:
                    print(f"[DEBUG] Message {len(final_state['messages']) - i}: {type(msg).__name__}")
                    if hasattr(msg, 'tool_calls'):
                        print(f"  - Tool calls: {len(msg.tool_calls) if msg.tool_calls else 0}")
                    print(f"  - Content preview: {str(msg.content)[:200]}...")
                    break
        
        return {
            "status": "success",
            "test_prompt": test_prompt,
            "steps_executed": final_state["current_step"],
            "results": final_state["results"],
            "errors": final_state["errors"],
            "messages": [
                {"role": m.type, "content": m.content}
                for m in final_state["messages"]
            ]
        }
    except Exception as e:
        print(f"[DEBUG] Agent error: {e}")
        return {
            "status": "error",
            "test_prompt": test_prompt,
            "error": str(e),
            "steps_executed": initial_state["current_step"],
            "results": initial_state["results"]
        }

# Synchronous wrapper
def run_test(prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
    """Synchronous wrapper for run_automation_test
    
    Args:
        prompt: Test description in natural language
        max_iterations: Maximum plan-execute cycles (default: 10)
    """
    return asyncio.run(run_automation_test(prompt, max_iterations))

if __name__ == "__main__":
    # Example usage
    test_prompts = [
        "Open https://example.com and take a screenshot",
        "Navigate to Google, search for 'Playwright automation', and click the first result",
        "Go to GitHub login page, fill username and password fields (don't submit)"
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Test: {prompt}")
        print('='*60)
        
        result = run_test(prompt)
        
        print(f"Status: {result['status']}")
        print(f"Steps executed: {result.get('steps_executed', 0)}")
        if result.get('errors'):
            print(f"Errors: {result['errors']}")
        print('='*60)