"""
Prompt Templates for Test Case Processing

Centralized prompt management with templates for different use cases.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Prompt template with system and user messages"""
    name: str
    system_prompt: str
    user_prompt_template: str
    description: str = ""


class PromptManager:
    """Manages prompt templates for test case processing"""
    
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
    
    def __init__(self):
        """Initialize prompt manager with predefined templates"""
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
    
    def format_prompt(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        Format a prompt template with provided variables
        
        Args:
            template_name: Name of the template
            **kwargs: Variables to format the template
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        template = self.get_template(template_name)
        user_prompt = template.user_prompt_template.format(**kwargs)
        return template.system_prompt, user_prompt
    
    def get_test_case_conversion_prompts(
        self, 
        short_description: str,
        test_id: Optional[str] = None,
        additional_context: Optional[Dict] = None
    ) -> tuple[str, str]:
        """
        Get prompts for test case conversion
        
        Args:
            short_description: Brief test case description
            test_id: Optional test case ID
            additional_context: Optional additional context
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        if test_id or additional_context:
            # Use template with context
            context_str = ""
            if additional_context:
                for key, value in additional_context.items():
                    context_str += f"- {key}: {value}\n"
            
            return self.format_prompt(
                "test_case_with_context",
                test_id=test_id or "N/A",
                short_description=short_description,
                context=context_str if context_str else "None"
            )
        else:
            # Use basic template
            return self.format_prompt(
                "test_case_conversion",
                short_description=short_description
            )
    
    def add_custom_template(self, template: PromptTemplate):
        """Add a custom prompt template"""
        self.templates[template.name] = template
    
    def list_templates(self) -> list[str]:
        """List all available template names"""
        return list(self.templates.keys())


# Singleton instance
_prompt_manager_instance = None

def get_prompt_manager() -> PromptManager:
    """Get singleton prompt manager instance"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
