"""LLM Provider implementations for Groq and OpenAI"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from ..config import LLMOpsConfig, get_config


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def get_llm(self, **kwargs) -> Any:
        """Get the LLM instance"""
        pass
    
    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke the LLM with a prompt"""
        pass


class GroqProvider(LLMProvider):
    """Groq LLM Provider implementation"""
    
    def __init__(self, config: LLMOpsConfig):
        self.config = config
        self.llm_config = config.get_llm_config("groq")
        self._llm = None
    
    def get_llm(self, **kwargs) -> ChatGroq:
        """Get ChatGroq instance with configuration"""
        if self._llm is None:
            llm_kwargs = {
                "groq_api_key": self.llm_config.api_key,
                "model_name": self.llm_config.model,
                "temperature": self.llm_config.temperature,
            }
            llm_kwargs.update(kwargs)
            self._llm = ChatGroq(**llm_kwargs)
        return self._llm
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke Groq LLM with a prompt"""
        llm = self.get_llm(**kwargs)
        response = llm.invoke(prompt)
        return response.content


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider implementation (supports custom gateway)"""
    
    def __init__(self, config: LLMOpsConfig):
        self.config = config
        self.llm_config = config.get_llm_config("openai")
        self._llm = None
    
    def get_llm(self, **kwargs) -> ChatOpenAI:
        """Get ChatOpenAI instance with configuration"""
        if self._llm is None:
            llm_kwargs = {
                "model": self.llm_config.model,
                "temperature": self.llm_config.temperature,
            }
            
            # Support custom OpenAI gateway
            if self.llm_config.base_url:
                llm_kwargs["openai_api_base"] = self.llm_config.base_url
                llm_kwargs["openai_api_key"] = self.llm_config.api_key
                if self.llm_config.headers:
                    llm_kwargs["default_headers"] = self.llm_config.headers
            else:
                llm_kwargs["openai_api_key"] = self.llm_config.api_key
            
            llm_kwargs.update(kwargs)
            self._llm = ChatOpenAI(**llm_kwargs)
        return self._llm
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke OpenAI LLM with a prompt"""
        llm = self.get_llm(**kwargs)
        response = llm.invoke(prompt)
        return response.content


def get_llm_provider(provider_name: Optional[str] = None, config: Optional[LLMOpsConfig] = None) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider
    
    Args:
        provider_name: Name of provider ("groq" or "openai"). If None, auto-detects from config.
        config: LLMOpsConfig instance. If None, creates from environment.
    
    Returns:
        LLMProvider instance
    """
    if config is None:
        config = get_config()
    
    if provider_name is None:
        provider_name = "groq" if config.use_groq else "openai"
    
    if provider_name.lower() == "groq":
        return GroqProvider(config)
    elif provider_name.lower() == "openai":
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: 'groq', 'openai'")
