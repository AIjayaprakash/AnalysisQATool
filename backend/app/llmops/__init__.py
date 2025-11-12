"""
LLMOps Package - Organized LLM Operations for Test Case Processing

This package provides a structured approach to LLM operations including:
- LLM providers (Groq, OpenAI, Custom Gateway)
- Prompt templates and management
- Data models and schemas
- Tools and utilities
- Generators for test case conversion
- Configuration management
- Playwright automation tools
"""

__version__ = "1.0.0"

from .config import LLMOpsConfig, LLMConfig, get_config
from .prompts import PromptManager, get_prompt_manager
from .llm import LLMProvider, GroqProvider, OpenAIProvider, get_llm_provider, CustomOpenAILLM
from .models import TestCase, TestCasePrompt, ExecutionResult, TestCaseStatus
from .utils import ExcelReader, ExcelWriter, PlaywrightState, get_playwright_state
from .generators import TestCaseGenerator, PlaywrightAgent
from .tools import get_playwright_tools, PLAYWRIGHT_TOOLS

__all__ = [
    # Config
    "LLMOpsConfig",
    "LLMConfig", 
    "get_config",
    # Prompts
    "PromptManager",
    "get_prompt_manager",
    # LLM Providers
    "LLMProvider",
    "GroqProvider",
    "OpenAIProvider",
    "get_llm_provider",
    "CustomOpenAILLM",
    # Models
    "TestCase",
    "TestCasePrompt",
    "ExecutionResult",
    "TestCaseStatus",
    # Utils
    "ExcelReader",
    "ExcelWriter",
    "PlaywrightState",
    "get_playwright_state",
    # Generators
    "TestCaseGenerator",
    "PlaywrightAgent",
    # Tools
    "get_playwright_tools",
    "PLAYWRIGHT_TOOLS"
]

