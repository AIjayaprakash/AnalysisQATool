"""Playwright agent system prompts and prompt management"""


class PlaywrightAgentPrompts:
    """Centralized prompts for Playwright automation agent"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Get the system prompt for Playwright automation agent
        
        Returns:
            System prompt string with tool usage instructions
        """
        return """You are an expert QA automation engineer using Playwright for web automation.

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
- playwright_get_page_metadata(selector): Extract metadata for page or specific element
- playwright_close_browser(): Close browser when done

TOOL USAGE FORMAT:
To use a tool, respond with:
USE_TOOL: tool_name
ARGS: {"arg1": "value1", "arg2": "value2"}

Example:
USE_TOOL: playwright_navigate  
ARGS: {"url": "https://example.com"}

USE_TOOL: playwright_get_page_metadata
ARGS: {"selector": null}

USE_TOOL: playwright_get_page_metadata
ARGS: {"selector": "button#submit"}

USE_TOOL: playwright_screenshot
ARGS: {"filename": "step1.png"}

METADATA EXTRACTION REQUIREMENT:
IMPORTANT: After navigating to each page and before interacting with elements:
1. Use playwright_get_page_metadata with ARGS: {"selector": null} to get page info (note: use null, not "null")
2. Use playwright_get_page_metadata with ARGS: {"selector": "css-selector"} for specific elements
3. Extract metadata for: links, buttons, inputs, forms - anything you click or type into

EXECUTION RULES:
1. ALWAYS start with USE_TOOL: playwright_navigate
2. After navigation, IMMEDIATELY extract page metadata
3. Before interacting with an element, extract its metadata first
4. Use USE_TOOL format for ALL actions
5. Take screenshots to document progress
6. ALWAYS end with USE_TOOL: playwright_close_browser
7. Work step by step and explain your actions

Begin the automation task now using the tools."""
    
    @staticmethod
    def get_tool_usage_format() -> str:
        """
        Get the tool usage format template
        
        Returns:
            Tool usage format string
        """
        return """USE_TOOL: tool_name
ARGS: {"arg1": "value1", "arg2": "value2"}"""
    
    @staticmethod
    def get_tool_examples() -> list:
        """
        Get example tool usages
        
        Returns:
            List of example tool usage strings
        """
        return [
            'USE_TOOL: playwright_navigate\nARGS: {"url": "https://example.com"}',
            'USE_TOOL: playwright_get_page_metadata\nARGS: {"selector": null}',
            'USE_TOOL: playwright_click\nARGS: {"selector": "button#submit", "element_description": "Submit button"}',
            'USE_TOOL: playwright_type\nARGS: {"selector": "input#email", "text": "user@example.com", "element_description": "Email field"}',
            'USE_TOOL: playwright_screenshot\nARGS: {"filename": "page_loaded.png"}',
            'USE_TOOL: playwright_close_browser\nARGS: {}'
        ]
    
    @staticmethod
    def get_metadata_extraction_rules() -> str:
        """
        Get metadata extraction rules
        
        Returns:
            Metadata extraction rules string
        """
        return """METADATA EXTRACTION REQUIREMENT:
IMPORTANT: After navigating to each page and before interacting with elements:
1. Use playwright_get_page_metadata with ARGS: {"selector": null} to get page info
2. Use playwright_get_page_metadata with ARGS: {"selector": "css-selector"} for specific elements
3. Extract metadata for: links, buttons, inputs, forms - anything you click or type into"""
    
    @staticmethod
    def get_execution_rules() -> list:
        """
        Get execution rules for automation
        
        Returns:
            List of execution rules
        """
        return [
            "ALWAYS start with USE_TOOL: playwright_navigate",
            "After navigation, IMMEDIATELY extract page metadata",
            "Before interacting with an element, extract its metadata first",
            "Use USE_TOOL format for ALL actions",
            "Take screenshots to document progress",
            "ALWAYS end with USE_TOOL: playwright_close_browser",
            "Work step by step and explain your actions"
        ]
    
    @staticmethod
    def get_available_tools_description() -> dict:
        """
        Get descriptions of all available tools
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            "playwright_navigate": "Navigate to a website (opens visible browser)",
            "playwright_click": "Click elements on the page",
            "playwright_type": "Type text into input fields",
            "playwright_screenshot": "Take screenshots for documentation",
            "playwright_wait_for_selector": "Wait for elements to appear",
            "playwright_wait_for_text": "Wait for text to appear",
            "playwright_get_page_content": "Get page structure and content",
            "playwright_execute_javascript": "Run JavaScript",
            "playwright_get_page_metadata": "Extract metadata for page or specific element",
            "playwright_close_browser": "Close browser when done"
        }
    
    @staticmethod
    def format_tool_call(tool_name: str, args: dict) -> str:
        """
        Format a tool call in the expected format
        
        Args:
            tool_name: Name of the tool to call
            args: Dictionary of arguments for the tool
        
        Returns:
            Formatted tool call string
        """
        import json
        return f"USE_TOOL: {tool_name}\nARGS: {json.dumps(args)}"
    
    @staticmethod
    def get_completion_phrases() -> list:
        """
        Get phrases that indicate task completion
        
        Returns:
            List of completion indicator phrases
        """
        return [
            "browser closed",
            "task complete",
            "automation complete",
            "test completed",
            "execution finished"
        ]
