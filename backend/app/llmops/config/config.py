"""
Configuration Management for LLMOps

Centralized configuration for LLM providers, models, and settings.
"""

from typing import Optional, Dict
from pydantic import Field
from pydantic_settings import BaseSettings
from dataclasses import dataclass
from llmops.common.exceptions import ConfigurationException


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: str  # "groq" or "openai" or "custom"
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1024
    gateway_url: Optional[str] = None
    extra_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.extra_headers is None:
            self.extra_headers = {}


class LLMOpsConfig(BaseSettings):
    """Main configuration for LLMOps - loads from .env file"""
    
    # Application Environment
    app_env: str = Field(default="Test-Development", description="Application environment")
    
    # Auto-detect provider from environment
    use_groq: bool = Field(default=False, description="Use Groq provider instead of OpenAI")
    
    # API Keys
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    custom_api_key: Optional[str] = Field(default=None, alias="CUSTOM_OPENAI_KEY", description="Custom OpenAI API key")
    
    # Default models
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Default Groq model")
    openai_model: str = Field(default="gpt-4o", description="Default OpenAI model")
    browser_type: str = Field(default="chromium", description="Browser type for Playwright (chromium, firefox, webkit, edge)")
    
    # Custom gateway settings
    custom_gateway_url: Optional[str] = Field(
        default="https://gateway.ai-npe.humana.com/openai/deployments/{model}",
        description="Custom gateway URL"
    )
    custom_gateway_headers: Dict[str, str] = Field(
        default_factory=lambda: {"ai-gateway-version": "v2"},
        description="Custom gateway headers"
    )
    
    # LLM settings
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=1024, gt=0, description="Maximum tokens")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @property
    def is_groq(self) -> bool:
        """Check if using Groq provider"""
        return self.use_groq
    
    def get_llm_config(self, provider: Optional[str] = None) -> LLMConfig:
        """
        Get LLM configuration for specified provider
        
        Args:
            provider: "groq", "openai", or "custom" (auto-detect if None)
            
        Returns:
            LLMConfig object
        """
        # Auto-detect provider
        if provider is None:
            provider = "groq" if self.use_groq else "openai"
        
        if provider == "groq":
            return LLMConfig(
                provider="groq",
                api_key=self.groq_api_key,
                model=self.groq_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif provider == "openai":
            return LLMConfig(
                provider="openai",
                api_key=self.openai_api_key or self.custom_api_key,
                model=self.openai_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                gateway_url=self.custom_gateway_url if self.custom_api_key else None,
                extra_headers=self.custom_gateway_headers if self.custom_api_key else {}
            )
        elif provider == "custom":
            return LLMConfig(
                provider="custom",
                api_key=self.custom_api_key,
                model=self.openai_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                gateway_url=self.custom_gateway_url,
                extra_headers=self.custom_gateway_headers
            )
        else:
            raise ConfigurationException(f"Unknown provider: {provider}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        if self.use_groq and not self.groq_api_key:
            raise ConfigurationException("GROQ_API_KEY not set but USE_GROQ=true", config_key="GROQ_API_KEY")
        
        if not self.use_groq and not (self.openai_api_key or self.custom_api_key):
            raise ConfigurationException("No API key found for OpenAI/Custom Gateway", config_key="OPENAI_API_KEY")
        
        return True


# Singleton instance
_config_instance = None

def get_config() -> LLMOpsConfig:
    """Get singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = LLMOpsConfig()
    return _config_instance


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config_instance
    _config_instance = None
