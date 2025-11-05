"""
LangGraph 1.0.2 Compatible Version - No @tool decorators
This version avoids all @tool decorators to prevent model_dump issues in LangGraph 1.0.2
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Annotated, TypedDict, Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

# Playwright imports
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

print("[OK] LangGraph 1.0.2 Compatible Playwright Agent")
print("  This version avoids @tool decorators to prevent model_dump issues")

# Check versions
try:
    import pydantic
    pydantic_version = pydantic.__version__ if hasattr(pydantic, '__version__') else pydantic.VERSION
    print(f"[INFO] Pydantic version: {pydantic_version}")
    
    import langgraph
    langgraph_version = langgraph.__version__ if hasattr(langgraph, '__version__') else "unknown"
    print(f"[INFO] LangGraph version: {langgraph_version}")
    
except Exception as e:
    print(f"[WARNING] Could not detect versions: {e}")

# Global browser state management
class PlaywrightState:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_initialized = False
    
    async def initialize(self, headless: bool = False, browser_type: str = "chromium"):
        """Initialize Playwright browser"""
        if self.is_initialized:
            return
        
        self.playwright = await async_playwright().start()
        
        # Launch browser based on type
        if browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=headless)
        elif browser_type == "edge":
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                channel="msedge"
            )
        else:  # chromium (default)
            self.browser = await self.playwright.chromium.launch(headless=headless)
        
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.is_initialized = True
        
        print(f"[BROWSER] Launched {browser_type} browser (headless={headless})")
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()  
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.is_initialized = False
        print("[BROWSER] Cleaned up browser resources")

# Global playwright state
pw_state = PlaywrightState()

# Agent State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    current_step: int
    results: List[Dict[str, Any]]
    errors: List[str]
    is_complete: bool
    max_iterations: int
    browser_config: Dict[str, Any]

# Direct function implementations (NO @tool decorators)
async def pw_navigate(url: str) -> str:
    """Navigate browser to a URL"""
    try:
        if not pw_state.is_initialized:
            await pw_state.initialize(headless=False)
        
        await pw_state.page.goto(url)
        title = await pw_state.page.title()
        return f"✅ Successfully navigated to {url} - Page title: '{title}'"
    except Exception as e:
        return f"❌ Failed to navigate to {url}: {str(e)}"

async def pw_click(selector: str, element_description: str = "") -> str:
    """Click an element on the page"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        if selector.startswith("text="):
            await pw_state.page.click(selector)
        elif selector.startswith("//"):
            await pw_state.page.click(f"xpath={selector}")
        else:
            await pw_state.page.click(selector)
        
        desc = f" ({element_description})" if element_description else ""
        return f"✅ Successfully clicked element: {selector}{desc}"
    except Exception as e:
        return f"❌ Failed to click element {selector}: {str(e)}"

async def pw_type(selector: str, text: str, element_description: str = "") -> str:
    """Type text into an input field"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.fill(selector, text)
        desc = f" ({element_description})" if element_description else ""
        return f"✅ Successfully typed '{text}' into {selector}{desc}"
    except Exception as e:
        return f"❌ Failed to type into {selector}: {str(e)}"

async def pw_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current page"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        screenshot_path = os.path.join(os.getcwd(), filename)
        await pw_state.page.screenshot(path=screenshot_path)
        return f"✅ Screenshot saved to: {screenshot_path}"
    except Exception as e:
        return f"❌ Failed to take screenshot: {str(e)}"

async def pw_get_page_content() -> str:
    """Get the current page content and structure"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        title = await pw_state.page.title()
        url = pw_state.page.url
        
        content = await pw_state.page.evaluate("""
            () => {
                const headings = Array.from(document.querySelectorAll('h1, h2, h3')).slice(0, 5).map(h => h.textContent.trim());
                const links = Array.from(document.querySelectorAll('a')).slice(0, 10).map(a => ({text: a.textContent.trim(), href: a.href}));
                const inputs = Array.from(document.querySelectorAll('input, textarea')).slice(0, 5).map(i => ({type: i.type, placeholder: i.placeholder, name: i.name}));
                
                return {
                    headings,
                    links: links.filter(l => l.text),
                    inputs
                };
            }
        """)
        
        result = f"📄 Page Info:\n  Title: {title}\n  URL: {url}\n"
        if content['headings']:
            result += f"  Headings: {', '.join(content['headings'][:3])}\n"
        if content['links']:
            result += f"  Links found: {len(content['links'])}\n"
        if content['inputs']:
            result += f"  Input fields: {len(content['inputs'])}\n"
        
        return result
    except Exception as e:
        return f"❌ Failed to get page content: {str(e)}"

async def pw_close_browser() -> str:
    """Close the browser and clean up resources"""
    try:
        await pw_state.cleanup()
        return "✅ Browser closed successfully"
    except Exception as e:
        return f"❌ Failed to close browser: {str(e)}"

# Function mapping for tool execution
PLAYWRIGHT_FUNCTIONS = {
    "pw_navigate": pw_navigate,
    "pw_click": pw_click,
    "pw_type": pw_type,
    "pw_screenshot": pw_screenshot,
    "pw_get_page_content": pw_get_page_content,
    "pw_close_browser": pw_close_browser,
}

print(f"[OK] Created {len(PLAYWRIGHT_FUNCTIONS)} direct Playwright functions")

# LLM Setup - Using Groq exclusively
print("[INFO] Using Groq AI with llama-3.3-70b-versatile model")
from langchain_groq import ChatGroq

if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY not set. Please set your Groq API key in environment variables.")
    raise ValueError("GROQ_API_KEY is required")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Agent Nodes
def parse_request(state: AgentState) -> AgentState:
    """Parse user's request and create execution plan"""
    messages = state["messages"]
    
    system_prompt = """You are an expert QA automation engineer using Playwright for web automation.

CRITICAL: You MUST specify Playwright actions using the TOOL_CALL format below. The browser will be VISIBLE.

Available Playwright functions:
- pw_navigate(url) - Navigate to a website (opens visible browser)
- pw_click(selector, element_description) - Click elements  
- pw_type(selector, text, element_description) - Type into input fields
- pw_screenshot(filename) - Take screenshots
- pw_get_page_content() - Get page structure and content
- pw_close_browser() - Close browser when done

Supported browser types: chromium (default), firefox, webkit, edge

EXECUTION FORMAT:
Use this exact format to call functions:

TOOL_CALL: pw_navigate
ARGS: {"url": "https://example.com"}

TOOL_CALL: pw_screenshot
ARGS: {"filename": "step1.png"}

EXECUTION RULES:
1. ALWAYS start with TOOL_CALL: pw_navigate
2. Use the exact TOOL_CALL format shown above
3. After function results, evaluate if more steps are needed
4. Always close browser when complete: TOOL_CALL: pw_close_browser

REMEMBER: Use TOOL_CALL format for actions - browser will be visible!"""
    
    if state["current_step"] == 0:
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="""Create and execute a detailed test plan using the Playwright functions.

IMPORTANT: 
- The browser will be VISIBLE during automation
- Start by calling pw_navigate to open the target website
- Use pw_get_page_content() to understand page structure
- Take screenshots to document steps
- Close the browser when done

Execute the test now using function calls.""")
        ]
    else:
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="Based on the results above, determine next steps. If test is complete, close the browser and provide summary. Otherwise, continue with function calls.")
        ]
    
    response = llm.invoke(planning_messages)
    state["messages"].append(response)
    return state

async def execute_functions(state: AgentState) -> AgentState:
    """Execute function calls using direct function mapping (no @tool decorators)"""
    last_message = state["messages"][-1]
    content = str(last_message.content) if hasattr(last_message, 'content') else ""
    
    import re
    import json
    
    function_calls = []
    pattern = r'TOOL_CALL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]*\})'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for func_name, args_str in matches:
        func_name = func_name.strip()
        try:
            args = json.loads(args_str) if args_str.strip() else {}
            function_calls.append({"name": func_name, "args": args})
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse args for {func_name}: {args_str}")
            continue
    
    if function_calls:
        func_names = [fc["name"] for fc in function_calls]
        print(f"  -> Step {state['current_step']}: Executing {len(function_calls)} function(s): {', '.join(func_names)}")
        
        results = []
        
        for func_call in function_calls:
            func_name = func_call["name"]
            args = func_call["args"]
            
            # Get function from direct mapping (no @tool decorator issues)
            func = PLAYWRIGHT_FUNCTIONS.get(func_name)
            
            if func:
                try:
                    # Direct function call - no Pydantic model_dump issues
                    result = await func(**args)
                    results.append(f"✅ {func_name}: {result}")
                except Exception as e:
                    results.append(f"❌ {func_name}: Error - {str(e)}")
            else:
                results.append(f"❌ {func_name}: Function not found")
        
        # Create result message
        combined_result = "Function execution results:\n" + "\n".join(results)
        result_message = AIMessage(content=combined_result)
        
        state["messages"].append(result_message)
        state["results"].append({
            "step": state["current_step"],
            "function_calls": len(function_calls),
            "function_names": func_names,
            "timestamp": datetime.now().isoformat()
        })
        state["current_step"] += 1
    else:
        state["is_complete"] = True
    
    # Check iteration limit
    if state["current_step"] >= state["max_iterations"]:
        state["is_complete"] = True
        state["errors"].append(f"Max iterations ({state['max_iterations']}) reached")
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end"""
    if state.get("is_complete"):
        return END
    
    if state["current_step"] >= state["max_iterations"]:
        return END
    
    last_message = state["messages"][-1]
    
    # Check for function calls
    if hasattr(last_message, 'content'):
        content = str(last_message.content)
        if "TOOL_CALL:" in content:
            return "execute_functions"
    
    # Continue after function results
    if isinstance(last_message, AIMessage) and "Function execution results:" in str(last_message.content):
        return "parse_request"
    
    return END

def create_langgraph_1_0_2_agent():
    """Create the LangGraph 1.0.2 compatible agent"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_request", parse_request)
    workflow.add_node("execute_functions", execute_functions)
    
    # Set entry point
    workflow.set_entry_point("parse_request")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "parse_request",
        should_continue,
        {
            "execute_functions": "execute_functions",
            "parse_request": "parse_request",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "execute_functions", 
        should_continue,
        {
            "parse_request": "parse_request",
            END: END
        }
    )
    
    return workflow.compile()

# Main execution function
async def run_langgraph_1_0_2_automation(test_prompt: str, max_iterations: int = 10, browser_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run Playwright automation test compatible with LangGraph 1.0.2"""
    
    if browser_config is None:
        browser_config = {
            "headless": False,
            "browser_type": "chromium"
        }
    
    # Initialize state
    initial_state = AgentState(
        messages=[HumanMessage(content=test_prompt)],
        current_step=0,
        results=[],
        errors=[],
        is_complete=False,
        max_iterations=max_iterations,
        browser_config=browser_config
    )
    
    print(f"\n[🎭 LANGGRAPH 1.0.2] Starting automation test: '{test_prompt}'")
    print(f"[🎭 LANGGRAPH 1.0.2] Browser config: {browser_config}")
    
    # Create and run agent
    agent = create_langgraph_1_0_2_agent()
    
    try:
        final_state = await agent.ainvoke(initial_state)
        
        print(f"\n[🎭 LANGGRAPH 1.0.2] Test completed:")
        print(f"  - Steps executed: {final_state['current_step']}")
        print(f"  - Is complete: {final_state.get('is_complete', False)}")
        
        # Ensure browser cleanup
        try:
            await pw_state.cleanup()
        except:
            pass
        
        return {
            "status": "success",
            "test_prompt": test_prompt,
            "steps_executed": final_state["current_step"],
            "results": final_state["results"],
            "errors": final_state["errors"],
            "browser_config": browser_config
        }
        
    except Exception as e:
        print(f"[❌ LANGGRAPH 1.0.2] Agent error: {e}")
        
        # Cleanup on error
        try:
            await pw_state.cleanup()
        except:
            pass
            
        return {
            "status": "error", 
            "test_prompt": test_prompt,
            "error": str(e),
            "steps_executed": initial_state["current_step"],
            "results": initial_state["results"]
        }

# Synchronous wrapper
def run_test_langgraph_1_0_2(prompt: str, max_iterations: int = 10, headless: bool = False, browser_type: str = "chromium") -> Dict[str, Any]:
    """Synchronous wrapper for LangGraph 1.0.2 compatible automation"""
    browser_config = {
        "headless": headless,
        "browser_type": browser_type
    }
    
    return asyncio.run(run_langgraph_1_0_2_automation(prompt, max_iterations, browser_config))

if __name__ == "__main__":
    print("🚀 LANGGRAPH 1.0.2 COMPATIBLE PLAYWRIGHT AGENT")
    print("===============================================")
    print("This version avoids @tool decorators to prevent model_dump issues")
    print()
    
    # Test with your environment
    result = run_test_langgraph_1_0_2(
        "Navigate to https://example.com, get page content, take a screenshot named langgraph_1_0_2_test.png, and close browser",
        max_iterations=5,
        browser_type="chromium"
    )
    
    print(f"\n📊 Results:")
    print(f"  Status: {result['status']}")
    print(f"  Steps executed: {result.get('steps_executed', 0)}")
    if result.get('errors'):
        print(f"  Errors: {result['errors']}")
    else:
        print("✅ No model_dump errors with LangGraph 1.0.2!")