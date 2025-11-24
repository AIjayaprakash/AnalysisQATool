"""Playwright automation agent using LangGraph with OpenAI/Groq"""

import os
import re
import json
import asyncio
from typing import Dict, List, Any, Annotated, TypedDict, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from ..llm import get_llm_provider
from ..config import LLMOpsConfig
from ..tools import get_playwright_tools
from ..utils import get_playwright_state
from ..prompts import get_prompt_manager
from ..common.exceptions import PlaywrightException, StateException, LLMException
from ..common.logger import log_info, log_error, log_debug
from .playwright_prompts import PlaywrightAgentPrompts
from .playwright_graph_builder import PlaywrightAgentGraphBuilder


class PlaywrightAgentState(TypedDict):
    """State for the Playwright agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: int
    max_iterations: int
    is_complete: bool


class PlaywrightAgent:
    """Playwright automation agent with LangGraph using OpenAI or Groq"""
    
    def __init__(
        self,
        provider: str = None,
        api_key: str = None,
        model: str = None,
        config: LLMOpsConfig = None
    ):
        """
        Initialize Playwright Agent
        
        Args:
            provider: "openai" or "groq" (auto-detect from config/env if None)
            api_key: API key for the provider (auto-detect from config/env if None)
            model: Model name (uses provider defaults if None)
            config: LLMOpsConfig instance (creates default if None)
        """
        # Use provided config or create default
        if config is None:
            config = LLMOpsConfig()
        
        self.config = config
        
        # Get LLM provider
        llm_provider = get_llm_provider(
            provider_type=provider,
            config=config,
            api_key=api_key,
            model_name=model
        )
        
        # Get LLM instance
        self.llm = llm_provider.get_llm()
        
        log_info(
            f"Using {llm_provider.__class__.__name__} with model: {llm_provider.model_name}",
            node="playwright_agent.init",
            extra={"provider": llm_provider.__class__.__name__, "model": llm_provider.model_name}
        )
        
        # Get Playwright tools
        self.tools = get_playwright_tools()
        
        # Get Playwright state
        self.pw_state = get_playwright_state()
        
        # Get prompt manager
        self.prompt_manager = get_prompt_manager()
        
        # Build agent
        self.agent = self._build_agent()
        
        log_info(
            f"Playwright Agent initialized with {len(self.tools)} tools",
            node="playwright_agent.init",
            extra={"tool_count": len(self.tools)}
        )
    
    def _build_agent(self):
        """
        Build the LangGraph agent using graph builder
        
        Returns:
            Compiled LangGraph workflow
        """
        # Use graph builder to construct the agent workflow
        graph_builder = PlaywrightAgentGraphBuilder(
            llm=self.llm,
            tools=self.tools,
            pw_state=self.pw_state
        )
        
        return graph_builder.build_graph(PlaywrightAgentState)
    
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
        
        log_info(
            f"Starting Playwright automation test",
            node="playwright_agent.run",
            extra={
                "test_prompt": test_prompt[:100],
                "browser_config": browser_config,
                "max_iterations": max_iterations
            }
        )
        
        try:
            # Run the agent
            result = await self.agent.ainvoke({
                "messages": [HumanMessage(content=test_prompt)],
                "current_step": 0,
                "max_iterations": max_iterations,
                "is_complete": False
            })
            
            log_info(
                "Playwright test completed",
                node="playwright_agent.run"
            )
            
            # Extract messages from result
            messages = result.get("messages", [])
            tool_calls = sum(1 for msg in messages if "Tool execution results" in str(getattr(msg, 'content', '')))
            
            log_info(
                "Test execution summary",
                node="playwright_agent.run",
                extra={"total_messages": len(messages), "tool_calls": tool_calls}
            )
            
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
            
        except PlaywrightException as e:
            log_error(
                "Playwright browser error",
                error=e,
                extra={"test_prompt": test_prompt[:100]}
            )
            
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
        except LLMException as e:
            log_error(
                "LLM error during Playwright test",
                error=e,
                extra={"test_prompt": test_prompt[:100]}
            )
            
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
        except Exception as e:
            log_error(
                "Unexpected Playwright agent error",
                error=e,
                extra={"test_prompt": test_prompt[:100]}
            )
            
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
