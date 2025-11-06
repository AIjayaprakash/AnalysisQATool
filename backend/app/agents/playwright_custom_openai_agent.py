"""
Complete LangGraph Playwright Automation Agent - Custom OpenAI Gateway Version
Uses your specific OpenAI client setup with gateway URL and custom headers.

This version handles model_dump issues while using your custom OpenAI configuration.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Annotated, TypedDict, Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# LangGraph and LangChain imports - with model_dump compatibility fixes
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

# Custom OpenAI imports
from openai import OpenAI

# Playwright imports
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

print("[OK] Playwright Agent with Custom OpenAI Gateway - OUTPUT PARSER approach")
print("  This version uses your custom OpenAI client with gateway URL")

# Version info
try:
    import pydantic
    import openai
    pydantic_version = pydantic.__version__ if hasattr(pydantic, '__version__') else pydantic.VERSION
    print(f"[INFO] Pydantic version: {pydantic_version}")
    print(f"[INFO] OpenAI version: {openai.__version__}")
    print("[INFO] Using OUTPUT PARSER approach to eliminate model_dump errors")
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
            # Microsoft Edge support
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                channel="msedge"  # Use Microsoft Edge channel
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

# Agent State with model_dump compatibility fixes
class AgentState(TypedDict):
    messages: List[BaseMessage]
    test_plan: str
    current_step: int
    total_steps: int
    results: List[Dict[str, Any]]
    errors: List[str]
    is_complete: bool
    max_iterations: int
    browser_config: Dict[str, Any]

# OUTPUT PARSER APPROACH - Direct Functions (NO @tool decorators)
# This completely eliminates model_dump serialization issues

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

async def pw_wait_for_selector(selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on the page"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(selector, timeout=timeout)
        return f"✅ Element {selector} appeared on page"
    except Exception as e:
        return f"❌ Element {selector} did not appear within {timeout}ms: {str(e)}"

async def pw_wait_for_text(text: str, timeout: int = 5000) -> str:
    """Wait for specific text to appear on the page"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(f"text={text}", timeout=timeout)
        return f"✅ Text '{text}' appeared on page"
    except Exception as e:
        return f"❌ Text '{text}' did not appear within {timeout}ms: {str(e)}"

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

async def pw_execute_javascript(script: str) -> str:
    """Execute JavaScript code in the browser context"""
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        result = await pw_state.page.evaluate(script)
        return f"✅ JavaScript executed. Result: {result}"
    except Exception as e:
        return f"❌ Failed to execute JavaScript: {str(e)}"

async def pw_close_browser() -> str:
    """Close the browser and clean up resources"""
    try:
        await pw_state.cleanup()
        return "✅ Browser closed successfully"
    except Exception as e:
        return f"❌ Failed to close browser: {str(e)}"

# Function mapping for output parser
PLAYWRIGHT_FUNCTIONS = {
    "pw_navigate": pw_navigate,
    "pw_click": pw_click,
    "pw_type": pw_type,
    "pw_screenshot": pw_screenshot,
    "pw_wait_for_selector": pw_wait_for_selector,
    "pw_wait_for_text": pw_wait_for_text,
    "pw_get_page_content": pw_get_page_content,
    "pw_execute_javascript": pw_execute_javascript,
    "pw_close_browser": pw_close_browser,
}

# Add function aliases for compatibility
async def playwright_navigate(url: str) -> str:
    """Navigate to a URL - compatibility wrapper for pw_navigate"""
    return await pw_navigate(url)

# Add to function mapping with both names
PLAYWRIGHT_FUNCTIONS["playwright_navigate"] = playwright_navigate

print(f"[OK] Created {len(PLAYWRIGHT_FUNCTIONS)} Playwright automation tools")

# Custom OpenAI Client Setup (YOUR CONFIGURATION)
class CustomOpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o", gateway_url: str = None):
        self.api_key = api_key
        self.model = model
        
        if gateway_url:
            self.gateway_url = gateway_url
        else:
            # Use your gateway URL pattern
            self.gateway_url = f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.gateway_url,
        )
        
        print(f"[INFO] Custom OpenAI Client initialized:")
        print(f"  Model: {self.model}")
        print(f"  Gateway URL: {self.gateway_url}")
    
    def invoke(self, messages: List[BaseMessage]) -> str:
        """Invoke the custom OpenAI client with LangChain messages"""
        
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": str(msg.content)})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": str(msg.content)})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": str(msg.content)})
            else:
                # Fallback for any other message type
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        print(f"[DEBUG] Sending {len(openai_messages)} messages to custom OpenAI gateway")
        
        try:
            # Use your exact client completion call with custom headers
            chat_completion = self.client.chat.completions.create(
                messages=openai_messages,
                model=self.model,
                extra_headers={
                    "api-key": self.api_key, 
                    "ai-gateway-version": "v2"
                },
            )
            
            # Extract content from response
            response_content = chat_completion.choices[0].message.content
            print(f"[DEBUG] Received response from custom OpenAI gateway: {len(response_content)} chars")
            
            return response_content
            
        except Exception as e:
            print(f"[ERROR] Custom OpenAI client error: {e}")
            return f"Error calling custom OpenAI client: {str(e)}"

# Initialize your custom OpenAI client
# You'll need to set these values
CUSTOM_API_KEY = os.getenv("CUSTOM_OPENAI_KEY", "Your Key Here")
CUSTOM_MODEL = "gpt-4o"
CUSTOM_GATEWAY_URL = f"https://gateway.ai-npe.humana.com/openai/deployments/{CUSTOM_MODEL}"

# Global custom client
custom_llm = CustomOpenAIClient(
    api_key=CUSTOM_API_KEY,
    model=CUSTOM_MODEL,
    gateway_url=CUSTOM_GATEWAY_URL
)

# Agent Nodes
def parse_test_request(state: AgentState) -> AgentState:
    """Parse user's test request and create execution plan"""
    messages = state["messages"]
    
    # Using Custom OpenAI with TOOL_CALL format
    system_prompt = """You are an expert QA automation engineer using Playwright for web automation.

CRITICAL: You MUST specify Playwright actions using the TOOL_CALL format below. The browser will be VISIBLE.

Available Playwright tools (using OUTPUT PARSER approach):
- playwright_navigate(url) - Navigate to a website (opens visible browser - supports Chromium, Firefox, WebKit, Edge)
- playwright_click(selector, element_description) - Click elements  
- playwright_type(selector, text, element_description) - Type into input fields
- playwright_screenshot(filename) - Take screenshots
- playwright_wait_for_selector(selector, timeout) - Wait for elements
- playwright_wait_for_text(text, timeout) - Wait for text to appear
- playwright_get_page_content() - Get page structure and content
- playwright_execute_javascript(script) - Run JavaScript
- playwright_close_browser() - Close browser when done

Supported browser types: chromium (default), firefox, webkit, edge

EXECUTION FORMAT:
Use this exact format to call tools:

TOOL_CALL: playwright_navigate
ARGS: {"url": "https://example.com"}

TOOL_CALL: playwright_screenshot
ARGS: {"filename": "step1.png"}

EXECUTION RULES:
1. ALWAYS start with TOOL_CALL: playwright_navigate
2. Use the exact TOOL_CALL format shown above
3. After tool results, evaluate if more steps are needed
4. Always close browser when complete: TOOL_CALL: playwright_close_browser

REMEMBER: Use TOOL_CALL format for actions - browser will be visible!"""
    
    # Build messages based on current step
    if state["current_step"] == 0:
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="""Create and execute a detailed test plan using the Playwright tools.

IMPORTANT: 
- The browser will be VISIBLE during automation so you can see what's happening
- Start by calling playwright_navigate to open the target website
- Use playwright_get_page_content() to understand page structure
- Take screenshots to document steps
- Close the browser when done

Execute the test now using tool calls.""")
        ]
    else:
        planning_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content="Based on the results above, determine next steps. If test is complete, close the browser and provide summary. Otherwise, continue with tool calls.")
        ]
    
    # Use your custom OpenAI client
    response_content = custom_llm.invoke(planning_messages)
    
    # CRITICAL FIX for Custom OpenAI model_dump issue: Ensure proper AIMessage
    print(f"[DEBUG] Custom OpenAI response type: {type(response_content)}")
    
    # Since our custom client returns a string, wrap it in AIMessage
    if isinstance(response_content, str):
        state["messages"].append(AIMessage(content=response_content))
    else:
        # Fallback
        state["messages"].append(AIMessage(content=str(response_content)))
    
    return state

async def execute_tools(state: AgentState) -> AgentState:
    """OUTPUT PARSER APPROACH: Execute tool calls using direct function calls (no @tool decorators)
    This completely eliminates model_dump serialization issues by bypassing Pydantic altogether"""
    last_message = state["messages"][-1]
    
    # Parse TOOL_CALL format (works with Custom OpenAI)
    content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
    
    import re
    import json
    
    tool_calls = []
    pattern = r'TOOL_CALL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]*\})'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for tool_name, args_str in matches:
        tool_name = tool_name.strip()
        try:
            args = json.loads(args_str) if args_str.strip() else {}
            tool_calls.append({"name": tool_name, "args": args})
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse args for {tool_name}: {args_str}")
            continue
    
    if tool_calls:
        tool_call_names = [tc["name"] for tc in tool_calls]
        print(f"  -> Step {state['current_step']}: Executing {len(tool_calls)} Playwright tool(s): {', '.join(tool_call_names)}")
        
        tool_results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            
            # OUTPUT PARSER: Map tool names to direct functions  
            tool_name_mapping = {
                "playwright_navigate": "pw_navigate",
                "playwright_click": "pw_click", 
                "playwright_type": "pw_type",
                "playwright_screenshot": "pw_screenshot",
                "playwright_wait_for_selector": "pw_wait_for_selector",
                "playwright_wait_for_text": "pw_wait_for_text",
                "playwright_get_page_content": "pw_get_page_content",
                "playwright_execute_javascript": "pw_execute_javascript",
                "playwright_close_browser": "pw_close_browser",
            }
            
            # Get the actual function name
            actual_func_name = tool_name_mapping.get(tool_name, tool_name)
            tool_func = PLAYWRIGHT_FUNCTIONS.get(actual_func_name)
            
            if tool_func:
                try:
                    # DIRECT FUNCTION CALL - No Pydantic, no model_dump, no serialization issues
                    result = await tool_func(**args)
                    tool_results.append(f"✅ {tool_name}: {result}")
                    
                except Exception as e:
                    error_msg = f"❌ Error executing {tool_name}: {str(e)}"
                    tool_results.append(f"Tool: {tool_name}\nResult: {error_msg}")
                    print(f"[ERROR] {error_msg}")
            else:
                error_msg = f"❌ Tool '{tool_name}' not found"
                tool_results.append(f"Tool: {tool_name}\nResult: {error_msg}")
                print(f"[ERROR] {error_msg}")
        
        # Create result message with proper AIMessage object
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
        state["is_complete"] = True
    
    # Check iteration limit
    if state["current_step"] >= state["max_iterations"]:
        state["is_complete"] = True
        state["errors"].append(f"Max iterations ({state['max_iterations']}) reached")
    
    return state

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end"""
    
    print(f"\n[DEBUG] should_continue - Step {state['current_step']}, Complete: {state.get('is_complete')}")
    
    if state.get("is_complete"):
        print("[DEBUG] -> END (marked complete)")
        return END
    
    if state["current_step"] >= state["max_iterations"]:
        print("[DEBUG] -> END (max iterations)")
        return END
    
    last_message = state["messages"][-1]
    print(f"[DEBUG] Last message type: {type(last_message).__name__}")
    
    # Check for TOOL_CALL format
    if hasattr(last_message, 'content'):
        content = str(last_message.content)
        if "TOOL_CALL:" in content:
            print("[DEBUG] -> execute_tools (TOOL_CALL format)")
            return "execute_tools"
    
    # Continue after tool results
    if isinstance(last_message, AIMessage) and "Tool execution results:" in str(last_message.content):
        print("[DEBUG] -> parse_request (after tool results)")
        return "parse_request"
    
    print("[DEBUG] -> END (no tool calls)")
    return END

def create_playwright_agent():
    """Create the LangGraph Playwright automation agent"""
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
async def run_playwright_automation(test_prompt: str, max_iterations: int = 1, browser_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run Playwright automation test with visible browser using Custom OpenAI Gateway.
    
    Args:
        test_prompt: Natural language test description
        max_iterations: Max plan-execute cycles
        browser_config: Browser configuration (headless, browser_type, etc.)
        
    Returns:
        Test results dictionary
    """
    
    # Default browser config
    if browser_config is None:
        browser_config = {
            "headless": False,  # Visible browser by default
            "browser_type": "chromium"
        }
    
    # Initialize state with proper message objects (fix model_dump issue)
    # CRITICAL: Ensure initial message is proper HumanMessage object
    initial_message = HumanMessage(content=str(test_prompt))
    
    initial_state = AgentState(
        messages=[initial_message],
        test_plan="",
        current_step=0,
        total_steps=0,
        results=[],
        errors=[],
        is_complete=False,
        max_iterations=max_iterations,
        browser_config=browser_config
    )
    
    print(f"\n[🎭 PLAYWRIGHT Custom OpenAI] Starting automation test: '{test_prompt}'")
    print(f"[🎭 PLAYWRIGHT Custom OpenAI] Browser config: {browser_config}")
    print(f"[🎭 PLAYWRIGHT Custom OpenAI] Max iterations: {max_iterations}")
    print(f"[DEBUG] Initial state message type: {type(initial_state['messages'][0])}")
    
    # Create and run agent
    agent = create_playwright_agent()
    
    try:
        final_state = await agent.ainvoke(initial_state)
        
        print(f"\n[🎭 PLAYWRIGHT Custom OpenAI] Test completed:")
        print(f"  - Steps executed: {final_state['current_step']}")
        print(f"  - Is complete: {final_state.get('is_complete', False)}")
        print(f"  - Total messages: {len(final_state['messages'])}")
        print(f"  - Errors: {final_state.get('errors', [])}")
        
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
            "browser_config": browser_config,
            "messages": [
                {"role": getattr(m, 'type', 'unknown'), "content": str(getattr(m, 'content', m))}
                for m in final_state["messages"]
            ]
        }
        
    except Exception as e:
        print(f"[❌ PLAYWRIGHT Custom OpenAI] Agent error: {e}")
        
        # Check if it's a model_dump error
        if 'model_dump' in str(e):
            print("[❌ CRITICAL] This is a model_dump error with Custom OpenAI!")
            print(f"   Full error: {e}")
            
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
def run_test_with_custom_openai(prompt: str, max_iterations: int = 10, headless: bool = False, browser_type: str = "chromium", api_key: str = None, model: str = "gpt-4o") -> Dict[str, Any]:
    """Synchronous wrapper for Playwright automation with Custom OpenAI Gateway
    
    Args:
        prompt: Test description in natural language
        max_iterations: Maximum plan-execute cycles
        headless: Whether to run browser in headless mode (default: False for visible)
        browser_type: Browser type to use (chromium, firefox, webkit, edge)
        api_key: Your custom OpenAI API key
        model: Model to use (default: gpt-4o)
    """
    
    # Update global client if new credentials provided
    if api_key:
        global custom_llm
        gateway_url = f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
        custom_llm = CustomOpenAIClient(
            api_key=api_key,
            model=model,
            gateway_url=gateway_url
        )
    
    browser_config = {
        "headless": headless,
        "browser_type": browser_type
    }
    
    return asyncio.run(run_playwright_automation(prompt, max_iterations, browser_config))

if __name__ == "__main__":
    # Test with Custom OpenAI Gateway
    print("🎭 PLAYWRIGHT AUTOMATION AGENT - CUSTOM OPENAI GATEWAY VERSION")
    print("=============================================================")
    print("This version uses your custom OpenAI gateway with special headers")
    print()
    
    # You need to set your actual API key here
    if CUSTOM_API_KEY == "Your Key Here":
        print("❌ Please set CUSTOM_OPENAI_KEY environment variable or update CUSTOM_API_KEY")
        print("   This should be your actual API key for the gateway")
    else:
        test_prompt = "Navigate to https://httpbin.org, take a screenshot, get page content, and close browser"
        
        result = run_test_with_custom_openai(
            prompt=test_prompt,
            max_iterations=3,
            headless=False,
            browser_type="chromium",
            api_key=CUSTOM_API_KEY,
            model="gpt-4o"
        )
        
        print(f"\n📊 Final Results:")
        print(f"  Status: {result['status']}")
        print(f"  Steps executed: {result.get('steps_executed', 0)}")
        if result.get('errors'):
            print(f"  Errors: {result['errors']}")
        else:
            print("  ✅ No errors!")
            
        print(f"\n✅ Custom OpenAI Gateway test completed!")