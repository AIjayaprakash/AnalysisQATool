"""Playwright agent system prompts and prompt management"""

from typing import Optional, Tuple
from ..prompts.prompt_validation_tool import (
    PromptValidator,
    PromptValidationConfig,
    PromptValidationReport,
    ValidationLevel,
    quick_validate,
    sanitize_prompt
)


class PlaywrightAgentPrompts:
    """Centralized prompts for Playwright automation agent with validation support"""
    
    def __init__(self, enable_validation: bool = True, validation_config: Optional[PromptValidationConfig] = None):
        """
        Initialize PlaywrightAgentPrompts with optional validation
        
        Args:
            enable_validation: Whether to enable prompt validation
            validation_config: Custom validation configuration
        """
        self._enable_validation = enable_validation
        self._validator = PromptValidator(validation_config) if enable_validation else None
    
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
- playwright_wait_for_selector(selector, timeout): Wait for elements to appear (timeout in milliseconds, default 5000)
- playwright_wait_for_text(text, timeout): Wait for text to appear (timeout in milliseconds, default 5000)
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

USE_TOOL: playwright_wait_for_selector
ARGS: {"selector": "button#submit", "timeout": 5000}

USE_TOOL: playwright_wait_for_text
ARGS: {"text": "Login successful", "timeout": 3000}

IMPORTANT - WAIT STRATEGY:
- Use short timeouts (3000-5000ms) to avoid long waits
- If element doesn't appear quickly, check if page loaded correctly
- Don't wait more than 10000ms (10 seconds) for any element
- If wait fails, take a screenshot and describe what you see

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
            'USE_TOOL: playwright_wait_for_selector\nARGS: {"selector": "button#submit", "timeout": 5000}',
            'USE_TOOL: playwright_wait_for_text\nARGS: {"text": "Welcome", "timeout": 3000}',
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
            "Use playwright_wait_for_selector with SHORT timeouts (3000-5000ms) before clicking",
            "Before interacting with an element, extract its metadata first",
            "Use USE_TOOL format for ALL actions",
            "Take screenshots to document progress",
            "If wait times out, take screenshot and check page state",
            "NEVER wait more than 10 seconds for any element",
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
            "playwright_wait_for_selector": "Wait for elements to appear (timeout in ms, use 3000-5000ms)",
            "playwright_wait_for_text": "Wait for text to appear (timeout in ms, use 3000-5000ms)",
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
    
    # ==================== Prompt Validation Methods ====================
    
    def validate_user_prompt(self, prompt: str, metadata: Optional[dict] = None) -> PromptValidationReport:
        """
        Validate a user prompt for Playwright automation
        
        Args:
            prompt: The user prompt to validate
            metadata: Optional metadata about the prompt context
            
        Returns:
            PromptValidationReport with validation results
            
        Raises:
            RuntimeError: If validation is disabled
        """
        if not self._enable_validation or not self._validator:
            raise RuntimeError("Validation is disabled. Enable it during initialization.")
        
        return self._validator.validate(prompt, metadata)
    
    def get_validated_system_prompt(self, validate: bool = True) -> Tuple[str, Optional[PromptValidationReport]]:
        """
        Get system prompt with optional validation
        
        Args:
            validate: Whether to validate the system prompt
            
        Returns:
            Tuple of (system_prompt, validation_report)
        """
        system_prompt = self.get_system_prompt()
        
        validation_report = None
        if validate and self._enable_validation and self._validator:
            validation_report = self._validator.validate(system_prompt, {"type": "system_prompt"})
            
            # Use sanitized version if available
            if validation_report.sanitized_prompt:
                system_prompt = validation_report.sanitized_prompt
        
        return system_prompt, validation_report
    
    def format_and_validate_user_prompt(self, test_description: str, validate: bool = True) -> Tuple[str, Optional[PromptValidationReport]]:
        """
        Format and validate a user prompt for Playwright automation
        
        Args:
            test_description: Description of the test case to automate
            validate: Whether to validate the prompt
            
        Returns:
            Tuple of (formatted_prompt, validation_report)
            
        Raises:
            ValueError: If validation fails with critical errors
        """
        # Format the user prompt
        user_prompt = f"""Execute the following test case using Playwright automation:

Test Case: {test_description}

Please:
1. Navigate to the appropriate website
2. Extract page metadata after each navigation
3. Perform the required actions step by step
4. Take screenshots at key steps
5. Close the browser when complete

Use the provided tools in the correct format."""
        
        validation_report = None
        if validate and self._enable_validation and self._validator:
            validation_report = self._validator.validate(user_prompt, {"type": "user_prompt", "test_description": test_description})
            
            # Check for critical errors
            critical_errors = validation_report.get_by_level(ValidationLevel.CRITICAL)
            if critical_errors:
                raise ValueError(f"Prompt validation failed with critical errors: {[e.message for e in critical_errors]}")
            
            # Use sanitized version if available
            if validation_report.sanitized_prompt:
                user_prompt = validation_report.sanitized_prompt
        
        return user_prompt, validation_report
    
    def quick_validate(self, prompt: str) -> bool:
        """
        Quick validation check for a prompt
        
        Args:
            prompt: The prompt to validate
            
        Returns:
            True if prompt is valid, False otherwise
        """
        if not self._enable_validation or not self._validator:
            return True  # If validation disabled, consider valid
        
        report = self._validator.validate(prompt)
        return report.is_valid
    
    def sanitize(self, prompt: str) -> str:
        """
        Sanitize a prompt by removing dangerous content
        
        Args:
            prompt: The prompt to sanitize
            
        Returns:
            Sanitized prompt
        """
        if not self._enable_validation or not self._validator:
            return prompt  # Return as-is if validation disabled
        
        return self._validator._sanitize_prompt(prompt)
    
    def enable_validation(self, config: Optional[PromptValidationConfig] = None):
        """
        Enable prompt validation
        
        Args:
            config: Optional custom validation configuration
        """
        self._enable_validation = True
        self._validator = PromptValidator(config)
    
    def disable_validation(self):
        """
        Disable prompt validation
        """
        self._enable_validation = False
        self._validator = None
    
    def validate_tool_call_prompt(self, tool_name: str, args: dict, validate: bool = True) -> Tuple[str, Optional[PromptValidationReport]]:
        """
        Validate and format a tool call prompt
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            validate: Whether to validate
            
        Returns:
            Tuple of (formatted_tool_call, validation_report)
            
        Raises:
            ValueError: If validation fails with critical errors
        """
        tool_call = self.format_tool_call(tool_name, args)
        
        validation_report = None
        if validate and self._enable_validation and self._validator:
            # Validate the tool call
            validation_report = self._validator.validate(
                tool_call,
                {"type": "tool_call", "tool_name": tool_name}
            )
            
            # Check for critical errors
            critical_errors = validation_report.get_by_level(ValidationLevel.CRITICAL)
            if critical_errors:
                raise ValueError(f"Tool call validation failed: {[e.message for e in critical_errors]}")
            
            # Use sanitized version if available
            if validation_report.sanitized_prompt:
                tool_call = validation_report.sanitized_prompt
        
        return tool_call, validation_report
