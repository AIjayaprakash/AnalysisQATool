"""Playwright agent graph builder - constructs LangGraph workflow"""

import re
import json
from typing import List, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from .playwright_prompts import PlaywrightAgentPrompts
from ..common.exceptions import PlaywrightException
from ..common.logger import log_info, log_error, log_debug


class PlaywrightAgentGraphBuilder:
    """Builds the LangGraph agent workflow for Playwright automation"""
    
    def __init__(self, llm, tools, pw_state):
        """
        Initialize graph builder
        
        Args:
            llm: Language model instance
            tools: List of available Playwright tools
            pw_state: Playwright state manager
        """
        self.llm = llm
        self.tools = tools
        self.pw_state = pw_state
        self.prompts = PlaywrightAgentPrompts()
    
    def build_graph(self, state_class):
        """
        Build the complete LangGraph workflow
        
        Args:
            state_class: State TypedDict class for the agent
        
        Returns:
            Compiled LangGraph workflow
        """
        workflow = StateGraph(state_class)
        
        # Add nodes
        workflow.add_node("call_model", self._create_model_node())
        workflow.add_node("execute_tools", self._create_tool_execution_node())
        
        # Set entry point
        workflow.set_entry_point("call_model")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "call_model",
            self._create_continuation_decider(),
            {
                "execute_tools": "execute_tools",
                "call_model": "call_model",
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "execute_tools",
            self._create_continuation_decider(),
            {
                "call_model": "call_model",
                END: END
            }
        )
        
        return workflow.compile()
    
    def _create_model_node(self):
        """
        Create the model invocation node
        
        Returns:
            Function that calls the model with tools
        """
        def call_model_with_tools(state):
            """Call the model and request tool usage"""
            # Get system prompt from centralized prompts module
            system_prompt = self.prompts.get_system_prompt()
            system_message = SystemMessage(content=system_prompt)
            messages = [system_message] + state["messages"]
            
            # Use LLM to generate response
            response = self.llm.invoke(messages)
            return {"messages": [response], "current_step": state["current_step"] + 1}
        
        return call_model_with_tools
    
    def _create_tool_execution_node(self):
        """
        Create the tool execution node
        
        Returns:
            Async function that parses and executes tool calls
        """
        async def execute_tool_calls(state):
            """Parse and execute tool calls from model response"""
            last_message = state["messages"][-1]
            content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
            
            # Parse USE_TOOL format
            tool_pattern = r'USE_TOOL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]*\})'
            tool_matches = re.findall(tool_pattern, content, re.MULTILINE | re.DOTALL)
            
            if tool_matches:
                tool_results = []
                
                for tool_name, args_str in tool_matches:
                    result = await self._execute_single_tool(tool_name.strip(), args_str)
                    tool_results.append(result)
                
                # Return tool results
                result_content = "Tool execution results:\n" + "\n".join(tool_results)
                return {"messages": [AIMessage(content=result_content)]}
            
            # No tools found, mark as complete
            return {"messages": [], "is_complete": True}
        
        return execute_tool_calls
    
    async def _execute_single_tool(self, tool_name: str, args_str: str) -> str:
        """
        Execute a single tool with error handling
        
        Args:
            tool_name: Name of the tool to execute
            args_str: JSON string of arguments
        
        Returns:
            Result message string
        """
        try:
            args = json.loads(args_str) if args_str.strip() else {}
            
            # Find the tool
            tool_func = self._find_tool(tool_name)
            
            if tool_func:
                return await self._invoke_tool(tool_func, tool_name, args)
            else:
                error_msg = f"❌ Tool '{tool_name}' not found"
                log_error(f"Tool not found: {tool_name}", extra={"tool": tool_name})
                return error_msg
                
        except json.JSONDecodeError as e:
            error_msg = f"❌ Failed to parse args for {tool_name}: {args_str}"
            log_error(f"Failed to parse tool args", error=e, extra={"tool": tool_name, "args": args_str})
            return error_msg
    
    def _find_tool(self, tool_name: str):
        """
        Find a tool by name
        
        Args:
            tool_name: Name of the tool to find
        
        Returns:
            Tool function or None
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    async def _invoke_tool(self, tool_func, tool_name: str, args: dict) -> str:
        """
        Invoke a tool with error handling
        
        Args:
            tool_func: Tool function to invoke
            tool_name: Name of the tool
            args: Arguments dictionary
        
        Returns:
            Result message string
        """
        try:
            result = await tool_func.ainvoke(args)
            log_debug(
                f"Tool executed: {tool_name}",
                extra={"tool": tool_name, "result": str(result)[:100]}
            )
            return f"✅ {tool_name}: {result}"
            
        except PlaywrightException as e:
            error_msg = f"❌ {tool_name} playwright error: {str(e)}"
            log_error(f"Playwright tool error: {tool_name}", error=e, extra={"tool": tool_name})
            return error_msg
            
        except Exception as e:
            error_msg = f"❌ {tool_name} error: {str(e)}"
            log_error(f"Tool execution error: {tool_name}", error=e, extra={"tool": tool_name})
            return error_msg
    
    def _create_continuation_decider(self):
        """
        Create the continuation decision function
        
        Returns:
            Function that decides whether to continue or end
        """
        def should_continue(state) -> str:
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
            
            # Check for completion indicators using centralized prompts
            completion_phrases = self.prompts.get_completion_phrases()
            if any(phrase in content.lower() for phrase in completion_phrases):
                return END
            
            # Continue with model
            return "call_model"
        
        return should_continue
