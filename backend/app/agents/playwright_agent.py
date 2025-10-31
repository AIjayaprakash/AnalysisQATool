"""
LangGraph-based Playwright automation agent that wraps the MCP server tools
and provides natural language interface for web automation tasks.
"""

import os
from typing import Dict, List, Annotated, TypedDict, Union
from langgraph.graph import Graph
import operator
from datetime import datetime
from openai import AsyncOpenAI
import json
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
import asyncio
import httpx

# Load OpenAI key from environment
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-key-here"),
)

# MCP Server configuration
MCP_SERVER = "http://localhost:5001"  # Default Playwright MCP server URL

class AgentState(TypedDict):
    """Tracks the agent's memory and state between steps."""
    messages: List[BaseMessage]
    current_browser: str | None  # Track browser context ID
    current_page: str | None     # Track page ID
    current_url: str | None      # Track current page URL
    last_found_elements: Dict[str, str]  # Map readable names to selectors
    scratchpad: str  # Working memory for complex tasks
    status: str
    error: str | None

class MCPError(Exception):
    """Custom error for MCP server issues."""
    pass

async def call_mcp_endpoint(endpoint: str, data: Dict = None, method: str = "POST") -> Dict:
    """Make HTTP request to MCP server endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{MCP_SERVER}/{endpoint}"
            if method == "POST":
                response = await client.post(url, json=data)
            else:
                response = await client.get(url)
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MCPError(f"MCP server error: {str(e)}")

# Tool definitions that map to Playwright MCP functions
async def start_browser_tool(headless: bool = False) -> Dict:
    """Start a new browser context."""
    try:
        result = await call_mcp_endpoint("browser/launch", {
            "browser": "chromium",
            "headless": headless
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def new_page_tool(url: str = None) -> Dict:
    """Create a new page and optionally navigate to URL."""
    try:
        result = await call_mcp_endpoint("page/new", {
            "url": url
        } if url else None)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def navigate_tool(url: str) -> Dict:
    """Navigate current page to URL."""
    try:
        result = await call_mcp_endpoint("page/goto", {
            "url": url
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def find_element_tool(selector: str, strict: bool = False) -> Dict:
    """Find an element on the page."""
    try:
        result = await call_mcp_endpoint("element/locator", {
            "selector": selector,
            "strict": strict
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def click_element_tool(selector: str, strict: bool = False) -> Dict:
    """Click an element on the page."""
    try:
        result = await call_mcp_endpoint("element/click", {
            "selector": selector,
            "strict": strict
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def fill_element_tool(selector: str, text: str, strict: bool = False) -> Dict:
    """Fill text into an element."""
    try:
        result = await call_mcp_endpoint("element/fill", {
            "selector": selector,
            "text": text,
            "strict": strict
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def type_element_tool(selector: str, text: str, delay: int = 100) -> Dict:
    """Type text into an element with delay between keystrokes."""
    try:
        result = await call_mcp_endpoint("element/type", {
            "selector": selector,
            "text": text,
            "delay": delay
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_text_tool(selector: str, strict: bool = False) -> Dict:
    """Get text content of an element."""
    try:
        result = await call_mcp_endpoint("element/text", {
            "selector": selector,
            "strict": strict
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def take_screenshot_tool(selector: str = None, path: str = None) -> Dict:
    """Take a screenshot of the page or element."""
    try:
        data = {}
        if selector:
            data["selector"] = selector
        if path:
            data["path"] = path
            
        result = await call_mcp_endpoint("page/screenshot", data)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def wait_for_load_tool() -> Dict:
    """Wait for page load state."""
    try:
        result = await call_mcp_endpoint("page/wait_for_load_state", {
            "state": "networkidle"
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Agent function definitions for LangGraph
async def parse_user_input(state: AgentState) -> Dict:
    """Parse the user's request and plan actions."""
    messages = state["messages"]
    
    # Build prompt with available tools and current state
    tools_desc = """Available Playwright tools:
- start_browser_tool(headless: bool = False) -> Start Chromium browser
- new_page_tool(url: str = None) -> Create new page, optionally navigate
- navigate_tool(url: str) -> Navigate to URL
- find_element_tool(selector: str, strict: bool = False) -> Find element
- click_element_tool(selector: str, strict: bool = False) -> Click element
- fill_element_tool(selector: str, text: str) -> Fill text instantly
- type_element_tool(selector: str, text: str, delay: int = 100) -> Type with delay
- get_text_tool(selector: str) -> Get element text
- take_screenshot_tool(selector: str = None, path: str = None) -> Take screenshot
- wait_for_load_tool() -> Wait for page load

Playwright uses these selector types:
- text=Button -> find by text content
- css=.class -> CSS selector
- xpath=//button -> XPath
- id=submit -> by ID
- [placeholder="Search"] -> by attribute
"""

    context = f"""Current state:
- Browser: {"Active" if state["current_browser"] else "Not started"}
- Page: {"Active" if state["current_page"] else "None"}
- URL: {state["current_url"] or "None"}
- Last action status: {state["status"]}
{f'- Error: {state["error"]}' if state["error"] else ""}

{tools_desc}

Based on the user's request, break down the task into steps using available tools.
Return a JSON array of steps to execute. Each step should have:
- tool: name of the tool to call
- args: dictionary of arguments for the tool
- description: human readable description of this step

Example:
[
    {{"tool": "start_browser_tool", "args": {{"headless": false}}, "description": "Start Chromium browser"}},
    {{"tool": "new_page_tool", "args": {{"url": "https://example.com"}}, "description": "Create page and navigate to example.com"}}
]"""

    # Get completion from OpenAI
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": context},
            *[{"role": m.type, "content": m.content} for m in messages]
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    try:
        # Parse the steps from the response
        result = json.loads(response.choices[0].message.content)
        return {
            "steps": result.get("steps", []),
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to parse steps: {str(e)}"
        }

async def execute_step(state: AgentState, step: Dict) -> AgentState:
    """Execute a single automation step."""
    tool_name = step["tool"]
    args = step["args"]
    description = step["description"]
    
    # Map of tool names to functions
    tools = {
        "start_browser_tool": start_browser_tool,
        "new_page_tool": new_page_tool,
        "navigate_tool": navigate_tool,
        "find_element_tool": find_element_tool,
        "click_element_tool": click_element_tool,
        "fill_element_tool": fill_element_tool,
        "type_element_tool": type_element_tool,
        "get_text_tool": get_text_tool,
        "take_screenshot_tool": take_screenshot_tool,
        "wait_for_load_tool": wait_for_load_tool
    }
    
    try:
        if tool_name not in tools:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        # Execute the tool
        result = await tools[tool_name](**args)
        
        # Update state based on tool
        if tool_name == "start_browser_tool":
            state["current_browser"] = "active"
        elif tool_name == "new_page_tool":
            state["current_page"] = "active"
            if "url" in args:
                state["current_url"] = args["url"]
        elif tool_name == "navigate_tool":
            state["current_url"] = args["url"]
            
        # Add result to messages
        state["messages"].append(
            FunctionMessage(
                content=f"Executed: {description}\nResult: {json.dumps(result)}",
                name=tool_name
            )
        )
        
        state["status"] = "success"
        state["error"] = None
        
    except Exception as e:
        state["status"] = "error"
        state["error"] = str(e)
        state["messages"].append(
            FunctionMessage(
                content=f"Error executing {description}: {str(e)}",
                name=tool_name
            )
        )
    
    return state

def should_continue(state: AgentState) -> bool:
    """Check if we should continue executing steps."""
    return state["status"] == "success"

# Create the LangGraph workflow
async def create_playwright_agent() -> Graph:
    """Create a LangGraph agent for Playwright automation."""
    
    workflow = Graph()
    
    # Add nodes for parsing and execution
    workflow.add_node("parse_input", parse_user_input)
    workflow.add_node("execute_step", execute_step)
    
    # Add edges to connect the nodes
    workflow.add_edge("parse_input", "execute_step")
    workflow.add_conditional_edges(
        "execute_step",
        should_continue,
        {
            True: "execute_step",
            False: "end"
        }
    )
    
    return workflow

# Helper to create initial state
def create_initial_state(query: str) -> AgentState:
    """Create initial state for the agent."""
    return AgentState(
        messages=[HumanMessage(content=query)],
        current_browser=None,
        current_page=None,
        current_url=None,
        last_found_elements={},
        scratchpad="",
        status="success",
        error=None
    )

# Example usage
async def run_playwright_automation(query: str):
    """Run an automation task with the Playwright agent."""
    workflow = await create_playwright_agent()
    state = create_initial_state(query)
    
    try:
        final_state = await workflow.arun(state)
        return {
            "status": final_state["status"],
            "error": final_state["error"],
            "messages": [m.content for m in final_state["messages"]]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "messages": []
        }