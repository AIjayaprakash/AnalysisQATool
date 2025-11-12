"""Playwright automation agent using LangGraph with custom OpenAI"""

import os
import re
import json
import asyncio
from typing import Dict, List, Any, Annotated, TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from ..llm import CustomOpenAILLM
from ..tools import get_playwright_tools
from ..utils import get_playwright_state
from ..prompts import get_prompt_manager


class PlaywrightAgentState(TypedDict):
    """State for the Playwright agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: int
    max_iterations: int
    is_complete: bool


class PlaywrightAgent:
    """Playwright automation agent with LangGraph and Custom OpenAI"""
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4o",
        gateway_url: str = None
    ):
        """
        Initialize Playwright Agent
        
        Args:
            api_key: Custom OpenAI API key
            model: Model name (default: gpt-4o)
            gateway_url: Custom gateway URL
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("CUSTOM_OPENAI_KEY", "placeholder-key")
        
        # Initialize Custom OpenAI LLM
        self.llm = CustomOpenAILLM(
            api_key=api_key,
            model=model,
            gateway_url=gateway_url or f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
        )
        
        # Get Playwright tools
        self.tools = get_playwright_tools()
        
        # Get Playwright state
        self.pw_state = get_playwright_state()
        
        # Get prompt manager
        self.prompt_manager = get_prompt_manager()
        
        # Build agent
        self.agent = self._build_agent()
        
        print(f"[INFO] Playwright Agent initialized with {len(self.tools)} tools")
    
    def _build_agent(self):
        """Build the LangGraph agent"""
        
        def call_model_with_tools(state: PlaywrightAgentState):
            """Call the model and request tool usage"""
            
            # Get system prompt for Playwright automation
            system_prompt = """You are an expert QA automation engineer using Playwright for web automation.

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

Begin the automation task now using the tools."""
            
            system_message = SystemMessage(content=system_prompt)
            messages = [system_message] + state["messages"]
            
            # Use our custom OpenAI LLM
            response = self.llm.invoke(messages)
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
                        for tool in self.tools:
                            if tool.name == tool_name:
                                tool_func = tool
                                break
                        
                        if tool_func:
                            try:
                                # Call the tool using ainvoke method (LangChain standard)
                                result = await tool_func.ainvoke(args)
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
        return workflow.compile()
    
    async def run(
        self,
        test_prompt: str,
        max_iterations: int = 10,
        browser_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run Playwright automation test
        
        Args:
            test_prompt: Natural language test description
            max_iterations: Maximum iterations for agent
            browser_config: Browser configuration (headless, browser_type)
        
        Returns:
            Test results dictionary
        """
        # Default browser config
        if browser_config is None:
            browser_config = {
                "headless": False,
                "browser_type": "chromium"
            }
        
        print(f"\n[🎭 PLAYWRIGHT] Starting automation test: '{test_prompt}'")
        print(f"[🎭 PLAYWRIGHT] Browser config: {browser_config}")
        print(f"[🎭 PLAYWRIGHT] Max iterations: {max_iterations}")
        
        try:
            # Run the agent
            result = await self.agent.ainvoke({
                "messages": [HumanMessage(content=test_prompt)],
                "current_step": 0,
                "max_iterations": max_iterations,
                "is_complete": False
            })
            
            print(f"\n[🎭 PLAYWRIGHT] Test completed")
            
            # Extract messages from result
            messages = result.get("messages", [])
            tool_calls = sum(1 for msg in messages if "Tool execution results" in str(getattr(msg, 'content', '')))
            
            print(f"  - Total messages: {len(messages)}")
            print(f"  - Tool calls: {tool_calls}")
            
            # Ensure browser cleanup
            try:
                await self.pw_state.cleanup()
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
                               "system",
                        "content": str(msg.content) if hasattr(msg, 'content') else str(msg)
                    } 
                    for msg in messages
                ],
                "final_response": str(messages[-1].content) if messages and hasattr(messages[-1], 'content') else "No response"
            }
            
        except Exception as e:
            print(f"[❌ PLAYWRIGHT] Agent error: {e}")
            
            # Cleanup on error
            try:
                await self.pw_state.cleanup()
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
    
    def run_sync(
        self,
        test_prompt: str,
        max_iterations: int = 10,
        headless: bool = False,
        browser_type: str = "chromium"
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for running automation
        
        Args:
            test_prompt: Natural language test description
            max_iterations: Maximum iterations
            headless: Run browser in headless mode
            browser_type: Browser type (chromium, firefox, webkit, edge)
        
        Returns:
            Test results dictionary
        """
        browser_config = {
            "headless": headless,
            "browser_type": browser_type
        }
        
        return asyncio.run(self.run(test_prompt, max_iterations, browser_config))
