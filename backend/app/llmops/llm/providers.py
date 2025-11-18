"""LLM Provider implementations for Groq and OpenAI"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def get_llm(self, **kwargs):
        """Get LLM instance"""
        pass
    
    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke LLM with prompt"""
        pass


class GroqProvider(LLMProvider):
    """Groq LLM provider using ChatGroq"""
    
    def __init__(self, 
                 api_key: str,
                 model_name: str = "llama-3.3-70b-versatile",
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 **kwargs):
        """
        Initialize Groq provider
        
        Args:
            api_key: Groq API key
            model_name: Model name (default: llama-3.3-70b-versatile)
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self._llm = None
    
    def get_llm(self, **override_kwargs):
        """Get ChatGroq instance"""
        kwargs = {
            "groq_api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
            **self.kwargs,
            **override_kwargs
        }
        
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens
            
        return ChatGroq(**kwargs)
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Invoke Groq LLM with prompt
        
        Args:
            prompt: Input prompt string
            **kwargs: Additional arguments for LLM
            
        Returns:
            Generated text response
        """
        if not self._llm:
            self._llm = self.get_llm(**kwargs)
        
        response = self._llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider using ChatOpenAI"""
    
    def __init__(self,
                 api_key: str,
                 model_name: str = "gpt-4",
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 **kwargs):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model_name: Model name (default: gpt-4)
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self._llm = None
    
    def get_llm(self, **override_kwargs):
        """Get ChatOpenAI instance"""
        kwargs = {
            "openai_api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
            **self.kwargs,
            **override_kwargs
        }
        
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens
            
        return ChatOpenAI(**kwargs)
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Invoke OpenAI LLM with prompt
        
        Args:
            prompt: Input prompt string
            **kwargs: Additional arguments for LLM
            
        Returns:
            Generated text response
        """
        if not self._llm:
            self._llm = self.get_llm(**kwargs)
        
        response = self._llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


def get_llm_provider(provider_type: Optional[str] = None, 
                     config: Any = None,
                     api_key: Optional[str] = None,
                     model_name: Optional[str] = None,
                     **kwargs) -> LLMProvider:
    """
    Factory function to get LLM provider
    
    Args:
        provider_type: Type of provider ('groq' or 'openai'). Auto-detects from config if None.
        config: LLMOpsConfig instance (alternative to api_key)
        api_key: API key for the provider (alternative to config)
        model_name: Model name (optional, uses defaults)
        **kwargs: Additional arguments for provider
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider_type is not supported or cannot be determined
    """
    # Extract API key and provider from config if provided
    if config is not None:
        llm_config = config.get_llm_config(provider_type)
        if provider_type is None:
            # Auto-detect provider from config
            provider_type = llm_config.provider
        if api_key is None:
            api_key = llm_config.api_key
        if model_name is None:
            model_name = llm_config.model
    
    # Validate provider_type
    if provider_type is None:
        raise ValueError("provider_type must be specified or provided via config")
    
    provider_type = provider_type.lower()
    
    # Validate API key
    if not api_key:
        raise ValueError("api_key must be specified either directly or via config")
    
    if provider_type == "groq":
        return GroqProvider(
            api_key=api_key,
            model_name=model_name or "llama-3.3-70b-versatile",
            **kwargs
        )
    elif provider_type == "openai":
        return OpenAIProvider(
            api_key=api_key,
            model_name=model_name or "gpt-4",
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}. Use 'groq' or 'openai'")
