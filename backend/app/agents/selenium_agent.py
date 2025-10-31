"""
LangGraph-based Selenium automation agent that wraps the MCP server tools
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

# Import MCP server tools
from .. import server
from ..selenium_request_types import (
    BrowserType,
    BrowserOptions,
    StartBrowserRequest,
    NavigateRequest,
    ElementLocator,
    SendKeysRequest,
)

# Load OpenAI key from environment
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-key-here"),
)

class AgentState(TypedDict):
    """Tracks the agent's memory and state between steps."""
    messages: List[BaseMessage]
    current_browser: str | None  # Track browser session ID
    current_url: str | None      # Track current page URL
    last_found_elements: Dict[str, str]  # Map readable names to selectors
    scratchpad: str  # Working memory for complex tasks
    status: str
    error: str | None

# Tool definitions that map to server.py MCP functions
async def start_browser_tool(headless: bool = False) -> Dict:
    """Start a new browser session."""
    try:
        start_req = StartBrowserRequest(
            browser=BrowserType.CHROME,
            options=BrowserOptions(headless=headless)
        )
        result = await server.start_browser(start_req)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def navigate_tool(url: str) -> Dict:
    """Navigate browser to a URL."""
    try:
        nav_req = NavigateRequest(url=url)
        result = await server.navigate(nav_req)
        # Wait for page load
        await server.wait_for_page_load()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def find_element_tool(selector: str, by: str = "css", timeout: int = 5000) -> Dict:
    """Find an element on the page."""
    try:
        loc_req = ElementLocator(by=by, value=selector, timeout=timeout)
        result = await server.find_element(loc_req)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def click_element_tool(selector: str, by: str = "css", timeout: int = 5000) -> Dict:
    """Click an element on the page."""
    try:
        loc_req = ElementLocator(by=by, value=selector, timeout=timeout)
        result = await server.click_element(loc_req)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def send_keys_tool(selector: str, text: str, by: str = "css", timeout: int = 5000) -> Dict:
    """Type text into an element."""
    try:
        send_req = SendKeysRequest(by=by, value=selector, timeout=timeout, text=text)
        result = await server.send_keys(send_req)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_element_text_tool(selector: str, by: str = "css", timeout: int = 5000) -> Dict:
    """Get text content of an element."""
    try:
        loc_req = ElementLocator(by=by, value=selector, timeout=timeout)
        result = await server.get_element_text(loc_req)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_page_content_tool() -> Dict:
    """Get the current page's HTML content."""
    try:
        result = await server.get_page_content()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Agent function definitions for LangGraph
async def parse_user_input(state: AgentState) -> Dict:
    """Parse the user's request and plan actions."""
    messages = state["messages"]
    
    # Build prompt with available tools and current state
    tools_desc = """Available tools:
- start_browser_tool(headless: bool = False) -> Start Chrome browser
- navigate_tool(url: str) -> Navigate to URL
- find_element_tool(selector: str, by: str = "css") -> Find element
- click_element_tool(selector: str, by: str = "css") -> Click element
- send_keys_tool(selector: str, text: str, by: str = "css") -> Type text
- get_element_text_tool(selector: str, by: str = "css") -> Get element text
- get_page_content_tool() -> Get page HTML
"""

    context = f"""Current state:
- Browser: {"Active" if state["current_browser"] else "Not started"}
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
    {{"tool": "start_browser_tool", "args": {{"headless": false}}, "description": "Start Chrome browser"}},
    {{"tool": "navigate_tool", "args": {{"url": "https://example.com"}}, "description": "Navigate to example.com"}}
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
        "navigate_tool": navigate_tool,
        "find_element_tool": find_element_tool,
        "click_element_tool": click_element_tool,
        "send_keys_tool": send_keys_tool,
        "get_element_text_tool": get_element_text_tool,
        "get_page_content_tool": get_page_content_tool
    }
    
    try:
        if tool_name not in tools:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        # Execute the tool
        result = await tools[tool_name](**args)
        
        # Update state based on tool
        if tool_name == "start_browser_tool":
            state["current_browser"] = "active"
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
async def create_selenium_agent() -> Graph:
    """Create a LangGraph agent for Selenium automation."""
    
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
        current_url=None,
        last_found_elements={},
        scratchpad="",
        status="success",
        error=None
    )

# Example usage
async def run_selenium_automation(query: str):
    """Run an automation task with the Selenium agent."""
    workflow = await create_selenium_agent()
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