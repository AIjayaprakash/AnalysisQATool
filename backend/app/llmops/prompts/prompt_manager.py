"""
Prompt Templates for Test Case Processing

Centralized prompt management with templates for different use cases.
Includes prompt validation for security and quality assurance.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from .prompt_validation_tool import (
    PromptValidator,
    PromptValidationConfig,
    PromptValidationReport,
    ValidationLevel,
    quick_validate,
    sanitize_prompt
)


@dataclass
class PromptTemplate:
    """Prompt template with system and user messages"""
    name: str
    system_prompt: str
    user_prompt_template: str
    description: str = ""


class PromptManager:
    """
    Manages prompt templates for test case processing.
    Includes built-in validation for security and quality.
    """
    
    def __init__(self, enable_validation: bool = True, validation_config: Optional[PromptValidationConfig] = None):
        """
        Initialize prompt manager with optional validation.
        
        Args:
            enable_validation: Enable prompt validation (default: True)
            validation_config: Custom validation configuration
        """
        self._enable_validation = enable_validation
        self._validator = PromptValidator(validation_config) if enable_validation else None
        self._init_templates()
    
    # System prompt for test case conversion
    TEST_CASE_CONVERSION_SYSTEM = """You are an expert QA automation engineer. Your task is to convert brief test case descriptions into detailed, step-by-step Playwright automation instructions.

CRITICAL REQUIREMENTS:
1. Each step should be clear and actionable
2. Number each step (1), 2), 3), etc.)
3. Use specific Playwright actions: Navigate, Wait for, Click, Type, etc.
4. Include wait conditions before actions (Wait for element to appear)
5. Be specific about what to wait for (button names, text, etc.)
6. For credentials, keep the exact values provided (don't change usernames/passwords)
7. Include verification steps (Wait for X to appear after action)

OUTPUT FORMAT:
Return ONLY the numbered steps, one per line. No explanations, no introductions, just the steps.

EXAMPLE INPUT:
"Login to qa4-www.365.com with username ABC and password 12345"

EXAMPLE OUTPUT:
1) Navigate to https://qa4-www.365.com
2) Wait for sign in to appear
3) Click Sign in
4) Wait for Username to appear
5) Type username as ABC. Please don't change username
6) Type password as 12345
7) Click Sign In
8) Wait for Home screen to appear"""
    
    TEST_CASE_CONVERSION_USER = """Convert this test case into detailed Playwright automation steps:

{short_description}"""
    
    TEST_CASE_WITH_CONTEXT_USER = """Convert this test case into detailed Playwright automation steps:

Test Case ID: {test_id}
Description: {short_description}

Additional Context:
{context}"""
    
    def _init_templates(self):
        """Initialize prompt templates"""
        self.templates: Dict[str, PromptTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all prompt templates"""
        # Basic test case conversion
        self.templates["test_case_conversion"] = PromptTemplate(
            name="test_case_conversion",
            system_prompt=self.TEST_CASE_CONVERSION_SYSTEM,
            user_prompt_template=self.TEST_CASE_CONVERSION_USER,
            description="Convert short test case description to detailed Playwright steps"
        )
        
        # Test case with additional context
        self.templates["test_case_with_context"] = PromptTemplate(
            name="test_case_with_context",
            system_prompt=self.TEST_CASE_CONVERSION_SYSTEM,
            user_prompt_template=self.TEST_CASE_WITH_CONTEXT_USER,
            description="Convert test case with additional context information"
        )
    
    def get_template(self, template_name: str) -> PromptTemplate:
        """Get a prompt template by name"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")
        return self.templates[template_name]
    
    def format_prompt(self, template_name: str, validate: bool = True, **kwargs) -> tuple[str, str]:
        """
        Format a prompt template with provided variables and automatic validation.
        
        This method now calls format_and_validate_prompt internally to ensure
        all prompts are validated by default.
        
        Args:
            template_name: Name of the template
            validate: Whether to validate the prompts (default: True)
            **kwargs: Variables to format the template
            
        Returns:
            Tuple of (system_prompt, user_prompt)
            
        Raises:
            ValueError: If validation fails with critical errors
        """
        # Call format_and_validate_prompt which handles both formatting and validation
        system_prompt, user_prompt, validation_report = self.format_and_validate_prompt(
            template_name=template_name,
            validate=validate,
            **kwargs
        )
        
        # Return only the prompts (validation_report is handled internally)
        return system_prompt, user_prompt
    
    def get_test_case_conversion_prompts(
        self, 
        short_description: str,
        test_id: Optional[str] = None,
        additional_context: Optional[Dict] = None,
        validate: bool = True
    ) -> tuple[str, str]:
        """
        Get prompts for test case conversion with automatic validation.
        
        Args:
            short_description: Brief test case description
            test_id: Optional test case ID
            additional_context: Optional additional context
            validate: Whether to validate the prompts (default: True)
            
        Returns:
            Tuple of (system_prompt, user_prompt)
            
        Raises:
            ValueError: If validation fails with critical errors
        """
        if test_id or additional_context:
            # Use template with context
            context_str = ""
            if additional_context:
                for key, value in additional_context.items():
                    context_str += f"- {key}: {value}\n"
            
            return self.format_prompt(
                "test_case_with_context",
                validate=validate,
                test_id=test_id or "N/A",
                short_description=short_description,
                context=context_str if context_str else "None"
            )
        else:
            # Use basic template
            return self.format_prompt(
                "test_case_conversion",
                validate=validate,
                short_description=short_description
            )
    
    def add_custom_template(self, template: PromptTemplate):
        """Add a custom prompt template"""
        self.templates[template.name] = template
    
    def list_templates(self) -> list[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def validate_prompt(self, prompt: str, metadata: Optional[Dict] = None) -> PromptValidationReport:
        """
        Validate a prompt for security and quality.
        
        Args:
            prompt: The prompt text to validate
            metadata: Optional metadata about the prompt
        
        Returns:
            PromptValidationReport with validation results
        
        Raises:
            RuntimeError: If validation is disabled
        """
        if not self._enable_validation or not self._validator:
            raise RuntimeError("Validation is disabled. Enable it during initialization.")
        
        return self._validator.validate(prompt, metadata)
    
    def format_and_validate_prompt(
        self, 
        template_name: str, 
        validate: bool = True,
        **kwargs
    ) -> Tuple[str, str, Optional[PromptValidationReport]]:
        """
        Format a prompt from template and optionally validate it.
        This is the core implementation that format_prompt calls internally.
        
        Args:
            template_name: Name of the template to use
            validate: Whether to validate the prompts (default: True)
            **kwargs: Variables to fill in the template
        
        Returns:
            Tuple of (system_prompt, user_prompt, validation_report)
            validation_report is None if validation is disabled or not requested
        
        Raises:
            ValueError: If validation fails with critical errors
        """
        # Get template and format prompts directly (avoid circular call)
        template = self.get_template(template_name)
        user_prompt = template.user_prompt_template.format(**kwargs)
        system_prompt = template.system_prompt
        
        validation_report = None
        
        # Validate if enabled and requested
        if validate and self._enable_validation and self._validator:
            # Validate user prompt (system prompt is pre-validated template)
            validation_report = self._validator.validate(user_prompt)
            
            # Check for critical errors
            critical_errors = validation_report.get_by_level(ValidationLevel.CRITICAL)
            if critical_errors:
                error_messages = [e.message for e in critical_errors]
                raise ValueError(f"Prompt validation failed with critical errors: {error_messages}")
            
            # Use sanitized prompt if available
            if validation_report.sanitized_prompt:
                user_prompt = validation_report.sanitized_prompt
        
        return system_prompt, user_prompt, validation_report
    
    def quick_validate(self, prompt: str) -> bool:
        """
        Quick validation check for a prompt.
        
        Args:
            prompt: The prompt text to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not self._enable_validation:
            return True
        
        return quick_validate(prompt, strict=False)
    
    def sanitize(self, prompt: str) -> str:
        """
        Sanitize a prompt by removing dangerous content.
        
        Args:
            prompt: The prompt text to sanitize
        
        Returns:
            Sanitized prompt text
        """
        return sanitize_prompt(prompt)
    
    def enable_validation(self, config: Optional[PromptValidationConfig] = None):
        """Enable prompt validation with optional custom config"""
        self._enable_validation = True
        self._validator = PromptValidator(config)
    
    def disable_validation(self):
        """Disable prompt validation"""
        self._enable_validation = False
        self._validator = None


# Singleton instance
_prompt_manager_instance = None

def get_prompt_manager() -> PromptManager:
    """Get singleton prompt manager instance"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
