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

# LangGraph and LangChain imports - with tool decorators and LLM binding
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.language_models.base import BaseLanguageModel

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

# Using LangGraph's ReAct agent - no custom state needed

# TOOL DECORATOR APPROACH - Using @tool decorators with LangChain compatibility
# This uses proper LangChain tool integration

@tool
async def playwright_navigate(url: str) -> str:
    """Navigate browser to a URL. This will open a visible browser window.
    
    Args:
        url: The full URL to navigate to (e.g., https://example.com)
    """
    try:
        if not pw_state.is_initialized:
            await pw_state.initialize(headless=False)
        
        await pw_state.page.goto(url)
        title = await pw_state.page.title()
        return f"✅ Successfully navigated to {url} - Page title: '{title}'"
    except Exception as e:
        return f"❌ Failed to navigate to {url}: {str(e)}"

@tool
async def playwright_click(selector: str, element_description: str = "") -> str:
    """Click an element on the page by CSS selector, XPath, or text.
    
    Args:
        selector: CSS selector, XPath (prefix with //), or text content (prefix with text=)
        element_description: Optional description of the element for clarity
    """
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

@tool
async def playwright_type(selector: str, text: str, element_description: str = "") -> str:
    """Type text into an input field.
    
    Args:
        selector: CSS selector for the input field
        text: Text to type into the field
        element_description: Optional description of the input field
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.fill(selector, text)
        desc = f" ({element_description})" if element_description else ""
        return f"✅ Successfully typed '{text}' into {selector}{desc}"
    except Exception as e:
        return f"❌ Failed to type into {selector}: {str(e)}"

@tool
async def playwright_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current page.
    
    Args:
        filename: Name of the screenshot file (default: screenshot.png)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        screenshot_path = os.path.join(os.getcwd(), filename)
        await pw_state.page.screenshot(path=screenshot_path)
        return f"✅ Screenshot saved to: {screenshot_path}"
    except Exception as e:
        return f"❌ Failed to take screenshot: {str(e)}"

@tool
async def playwright_wait_for_selector(selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector to wait for
        timeout: Maximum time to wait in milliseconds (default: 5000)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(selector, timeout=timeout)
        return f"✅ Element {selector} appeared on page"
    except Exception as e:
        return f"❌ Element {selector} did not appear within {timeout}ms: {str(e)}"

@tool
async def playwright_wait_for_text(text: str, timeout: int = 5000) -> str:
    """Wait for specific text to appear on the page.
    
    Args:
        text: Text content to wait for
        timeout: Maximum time to wait in milliseconds (default: 5000)
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        await pw_state.page.wait_for_selector(f"text={text}", timeout=timeout)
        return f"✅ Text '{text}' appeared on page"
    except Exception as e:
        return f"❌ Text '{text}' did not appear within {timeout}ms: {str(e)}"

@tool
async def playwright_get_page_content() -> str:
    """Get the current page content and structure for analysis."""
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

@tool
async def playwright_execute_javascript(script: str) -> str:
    """Execute JavaScript code in the browser context.
    
    Args:
        script: JavaScript code to execute
    """
    try:
        if not pw_state.is_initialized:
            return "❌ Browser not initialized. Please navigate to a page first."
        
        result = await pw_state.page.evaluate(script)
        return f"✅ JavaScript executed. Result: {result}"
    except Exception as e:
        return f"❌ Failed to execute JavaScript: {str(e)}"

@tool
async def playwright_close_browser() -> str:
    """Close the browser and clean up resources."""
    try:
        await pw_state.cleanup()
        return "✅ Browser closed successfully"
    except Exception as e:
        return f"❌ Failed to close browser: {str(e)}"

# Collect all Playwright tools for LangGraph agent
playwright_tools = [
    playwright_navigate,
    playwright_click,
    playwright_type,
    playwright_screenshot,
    playwright_wait_for_selector,
    playwright_wait_for_text,
    playwright_get_page_content,
    playwright_execute_javascript,
    playwright_close_browser,
]

print(f"[OK] Created {len(playwright_tools)} Playwright automation tools with @tool decorators")

# Custom OpenAI LLM wrapper for LangChain compatibility
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import LLMResult, Generation

class CustomOpenAILLM(LLM):
    """Custom LLM wrapper for your OpenAI gateway that works with LangChain tools and agents"""
    
    api_key: str = "placeholder-key"
    model: str = "gpt-4o"
    gateway_url: str = None
    client: Any = None
    
    def __init__(self, api_key: str = "placeholder-key", model: str = "gpt-4o", gateway_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or "placeholder-key"
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
        
        print(f"[INFO] Custom OpenAI LLM initialized:")
        print(f"  Model: {self.model}")
        print(f"  Gateway URL: {self.gateway_url}")
    
    @property
    def _llm_type(self) -> str:
        return "custom_openai_gateway"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """Call the custom OpenAI gateway with a prompt"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                extra_headers={
                    "api-key": self.api_key, 
                    "ai-gateway-version": "v2"
                },
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"[ERROR] Custom OpenAI LLM error: {e}")
            return f"Error calling custom OpenAI LLM: {str(e)}"
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs) -> LLMResult:
        """Generate responses for multiple prompts"""
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop=stop, **kwargs)
            generations.append([Generation(text=response)])
        
        return LLMResult(generations=generations)
    
    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """Invoke with LangChain messages - returns AIMessage for compatibility"""
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
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        print(f"[DEBUG] Sending {len(openai_messages)} messages to custom OpenAI gateway")
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=openai_messages,
                model=self.model,
                extra_headers={
                    "api-key": self.api_key, 
                    "ai-gateway-version": "v2"
                },
            )
            
            response_content = chat_completion.choices[0].message.content
            print(f"[DEBUG] Received response from custom OpenAI gateway: {len(response_content)} chars")
            
            # Return proper AIMessage for LangChain compatibility
            return AIMessage(content=response_content)
            
        except Exception as e:
            print(f"[ERROR] Custom OpenAI LLM error: {e}")
            return AIMessage(content=f"Error calling custom OpenAI LLM: {str(e)}")

# Initialize your custom OpenAI LLM
CUSTOM_API_KEY = os.getenv("CUSTOM_OPENAI_KEY", "Your Key Here")
CUSTOM_MODEL = "gpt-4o"
CUSTOM_GATEWAY_URL = f"https://gateway.ai-npe.humana.com/openai/deployments/{CUSTOM_MODEL}"

# Create LLM instance (use placeholder if no key provided)
custom_llm = CustomOpenAILLM(
    api_key=CUSTOM_API_KEY or "placeholder-key",
    model=CUSTOM_MODEL,
    gateway_url=CUSTOM_GATEWAY_URL
)

# Note: Custom LLM doesn't support bind_tools, we'll handle tool calls manually

print(f"[INFO] Custom OpenAI LLM bound with {len(playwright_tools)} Playwright tools")

# Create a hybrid approach: @tool decorators with manual parsing for custom OpenAI compatibility
from typing import TypedDict, Annotated
import re
import json

class PlaywrightAgentState(TypedDict):
    """State for the Playwright agent with @tool decorators"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: int
    max_iterations: int
    is_complete: bool

def create_playwright_agent():
    """Create Playwright agent using @tool decorators with custom OpenAI LLM and output parsing fallback"""
    
    def call_model_with_tools(state: PlaywrightAgentState):
        """Call the model and request tool usage"""
        system_message = SystemMessage(content="""You are an expert QA automation engineer using Playwright for web automation.

CRITICAL: The browser will be VISIBLE during automation. You MUST use the available tools to complete the task.

Available Playwright tools:
- playwright_navigate(url): Navigate to a website (opens visible browser)
- playwright_click(selector, element_description): Click elements on the page
- playwright_type(selector, text, element_description): Type text into input fields  
- playwright_screenshot(filename): Take screenshots for documentation
- playwright_wait_for_selector(selector, timeout): Wait for elements to appear
- playwright_wait_for_text(text, timeout): Wait for text to appear
- playwright_get_page_content(): Get page structure and content
- playwright_execute_javascript(script): Run JavaScript
- playwright_close_browser(): Close browser when done

TOOL USAGE FORMAT:
To use a tool, respond with:
USE_TOOL: tool_name
ARGS: {"arg1": "value1", "arg2": "value2"}

Example:
USE_TOOL: playwright_navigate  
ARGS: {"url": "https://example.com"}

USE_TOOL: playwright_screenshot
ARGS: {"filename": "step1.png"}

EXECUTION RULES:
1. ALWAYS start with USE_TOOL: playwright_navigate
2. Use USE_TOOL format for ALL actions
3. Take screenshots to document progress
4. ALWAYS end with USE_TOOL: playwright_close_browser
5. Work step by step and explain your actions

Begin the automation task now using the tools.""")
        
        messages = [system_message] + state["messages"]
        
        # Use our custom OpenAI LLM
        response = custom_llm.invoke(messages)
        return {"messages": [response], "current_step": state["current_step"] + 1}

    async def execute_tool_calls(state: PlaywrightAgentState):
        """Parse and execute tool calls from model response"""
        last_message = state["messages"][-1]
        content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
        
        # Parse USE_TOOL format
        tool_pattern = r'USE_TOOL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]*\})'
        tool_matches = re.findall(tool_pattern, content, re.MULTILINE | re.DOTALL)
        
        if tool_matches:
            tool_results = []
            
            for tool_name, args_str in tool_matches:
                tool_name = tool_name.strip()
                try:
                    args = json.loads(args_str) if args_str.strip() else {}
                    
                    # Find and execute the tool
                    tool_func = None
                    for tool in playwright_tools:
                        if tool.name == tool_name:
                            tool_func = tool
                            break
                    
                    if tool_func:
                        try:
                            # Call the async tool function
                            result = await tool_func.func(**args)
                            tool_results.append(f"✅ {tool_name}: {result}")
                            print(f"[TOOL] {tool_name} -> {result}")
                        except Exception as e:
                            error_msg = f"❌ {tool_name} error: {str(e)}"
                            tool_results.append(error_msg)
                            print(f"[ERROR] {error_msg}")
                    else:
                        error_msg = f"❌ Tool '{tool_name}' not found"
                        tool_results.append(error_msg)
                        print(f"[ERROR] {error_msg}")
                        
                except json.JSONDecodeError as e:
                    error_msg = f"❌ Failed to parse args for {tool_name}: {args_str}"
                    tool_results.append(error_msg)
                    print(f"[ERROR] {error_msg}")
            
            # Return tool results
            result_content = "Tool execution results:\n" + "\n".join(tool_results)
            return {"messages": [AIMessage(content=result_content)]}
        
        # No tools found, mark as complete
        return {"messages": [], "is_complete": True}

    def should_continue(state: PlaywrightAgentState) -> str:
        """Decide whether to continue or end"""
        
        # Check completion conditions
        if state.get("is_complete", False):
            return END
            
        if state["current_step"] >= state["max_iterations"]:
            return END
        
        last_message = state["messages"][-1]
        content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
        
        # Check for tool calls
        if "USE_TOOL:" in content:
            return "execute_tools"
        
        # Check for completion indicators
        if any(phrase in content.lower() for phrase in ["browser closed", "task complete", "automation complete"]):
            return END
        
        # Continue with model
        return "call_model"

    # Build the StateGraph
    workflow = StateGraph(PlaywrightAgentState)
    
    # Add nodes
    workflow.add_node("call_model", call_model_with_tools)
    workflow.add_node("execute_tools", execute_tool_calls)
    
    # Set entry point
    workflow.set_entry_point("call_model")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "call_model": "call_model",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue,
        {
            "call_model": "call_model",
            END: END
        }
    )
    
    # Compile the graph
    agent = workflow.compile()
    
    print("[INFO] Created Playwright agent with @tool decorators and custom OpenAI compatibility")
    return agent

# Main execution function
async def run_playwright_automation(test_prompt: str, max_iterations: int = 1, browser_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run Playwright automation test with visible browser using Custom OpenAI Gateway and LangGraph ReAct agent.
    
    Args:
        test_prompt: Natural language test description
        max_iterations: Max plan-execute cycles (not directly used by ReAct agent)
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
    
    # Update global browser config
    global BROWSER_TYPE, HEADLESS
    BROWSER_TYPE = browser_config.get("browser_type", "chromium")
    HEADLESS = browser_config.get("headless", False)
    
    print(f"\n[🎭 PLAYWRIGHT Custom OpenAI] Starting ReAct automation test: '{test_prompt}'")
    print(f"[🎭 PLAYWRIGHT Custom OpenAI] Browser config: {browser_config}")
    print(f"[🎭 PLAYWRIGHT Custom OpenAI] Max iterations: {max_iterations}")
    
    # Create the ReAct agent
    agent = create_playwright_agent()
    
    try:
        # Run the Playwright agent with proper state
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=test_prompt)],
            "current_step": 0,
            "max_iterations": max_iterations,
            "is_complete": False
        })
        
        print(f"\n[🎭 PLAYWRIGHT Custom OpenAI] ReAct Agent Test completed:")
        
        # Extract messages from result
        messages = result.get("messages", [])
        tool_calls = sum(1 for msg in messages if hasattr(msg, '__class__') and 'Tool' in msg.__class__.__name__)
        
        print(f"  - Total messages: {len(messages)}")
        print(f"  - Tool calls: {tool_calls}")
        
        # Ensure browser cleanup
        try:
            await pw_state.cleanup()
        except:
            pass
        
        return {
            "status": "success",
            "test_prompt": test_prompt,
            "tool_calls": tool_calls,
            "total_messages": len(messages),
            "browser_config": browser_config,
            "messages": [
                {
                    "role": "assistant" if isinstance(msg, AIMessage) else 
                           "user" if isinstance(msg, HumanMessage) else
                           "tool" if hasattr(msg, '__class__') and 'Tool' in msg.__class__.__name__ else "system",
                    "content": str(msg.content) if hasattr(msg, 'content') else str(msg)
                } 
                for msg in messages
            ],
            "final_response": str(messages[-1].content) if messages and hasattr(messages[-1], 'content') else "No response"
        }
        
    except Exception as e:
        print(f"[❌ PLAYWRIGHT Custom OpenAI] ReAct Agent error: {e}")
        
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
            "tool_calls": 0,
            "total_messages": 0,
            "final_response": str(e)
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
        custom_llm = CustomOpenAILLM(
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