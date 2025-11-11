"""Test case generator - orchestrates LLM, prompts, and models"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..config import LLMOpsConfig, get_config
from ..llm import LLMProvider, get_llm_provider
from ..prompts import PromptManager, get_prompt_manager
from ..models import TestCase, TestCasePrompt
from ..utils import ExcelReader


class TestCaseGenerator:
    """
    Main orchestrator for test case generation
    Reads test cases from Excel, generates Playwright prompts using LLM
    """
    
    def __init__(self, 
                 provider: Optional[str] = None,
                 config: Optional[LLMOpsConfig] = None,
                 prompt_manager: Optional[PromptManager] = None):
        """
        Initialize test case generator
        
        Args:
            provider: LLM provider name ("groq" or "openai"). Auto-detects if None.
            config: LLMOpsConfig instance. Creates from environment if None.
            prompt_manager: PromptManager instance. Uses default if None.
        """
        self.config = config or get_config()
        self.llm_provider = get_llm_provider(provider, self.config)
        self.prompt_manager = prompt_manager or get_prompt_manager()
    
    def read_test_cases(self, 
                       excel_path: str, 
                       sheet_name: str = "Sheet1",
                       **column_mappings) -> List[TestCase]:
        """
        Read test cases from Excel file
        
        Args:
            excel_path: Path to Excel file
            sheet_name: Name of sheet to read
            **column_mappings: Column name mappings (test_id_col, module_col, etc.)
        
        Returns:
            List of TestCase objects
        """
        reader = ExcelReader(excel_path, sheet_name)
        return reader.get_test_cases(**column_mappings)
    
    def generate_playwright_prompt(self, test_case: TestCase) -> TestCasePrompt:
        """
        Generate Playwright automation prompt for a test case using LLM
        
        Args:
            test_case: TestCase object
        
        Returns:
            TestCasePrompt with generated prompt
        """
        # Get prompts from manager
        system_prompt, user_prompt = self.prompt_manager.get_test_case_conversion_prompts(test_case)
        
        # Combine for LLM
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate with LLM
        generated_prompt = self.llm_provider.invoke(full_prompt)
        
        return TestCasePrompt(
            test_case=test_case,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            generated_prompt=generated_prompt,
            generated_at=datetime.now()
        )
    
    def generate_batch(self, test_cases: List[TestCase]) -> List[TestCasePrompt]:
        """
        Generate prompts for multiple test cases
        
        Args:
            test_cases: List of TestCase objects
        
        Returns:
            List of TestCasePrompt objects
        """
        prompts = []
        for test_case in test_cases:
            try:
                prompt = self.generate_playwright_prompt(test_case)
                prompts.append(prompt)
            except Exception as e:
                print(f"Error generating prompt for {test_case.test_id}: {str(e)}")
                # Create error prompt
                error_prompt = TestCasePrompt(
                    test_case=test_case,
                    system_prompt="Error",
                    user_prompt="Error",
                    generated_prompt=f"Error: {str(e)}",
                    generated_at=datetime.now()
                )
                prompts.append(error_prompt)
        return prompts
    
    def process_excel(self, 
                     excel_path: str, 
                     sheet_name: str = "Sheet1",
                     **column_mappings) -> List[TestCasePrompt]:
        """
        End-to-end: Read Excel and generate prompts
        
        Args:
            excel_path: Path to Excel file
            sheet_name: Sheet name to read
            **column_mappings: Column name mappings
        
        Returns:
            List of TestCasePrompt objects
        """
        # Read test cases
        test_cases = self.read_test_cases(excel_path, sheet_name, **column_mappings)
        
        # Generate prompts
        prompts = self.generate_batch(test_cases)
        
        return prompts
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current LLM provider"""
        llm_config = self.config.get_llm_config("groq" if self.config.use_groq else "openai")
        return {
            "provider": "groq" if self.config.use_groq else "openai",
            "model": llm_config.model,
            "temperature": llm_config.temperature
        }
