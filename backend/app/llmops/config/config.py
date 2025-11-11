"""
Configuration Management for LLMOps

Centralized configuration for LLM providers, models, and settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: str  # "groq" or "openai" or "custom"
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1024
    gateway_url: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class LLMOpsConfig:
    """Main configuration for LLMOps"""
    
    # Auto-detect provider from environment
    use_groq: bool = field(default_factory=lambda: os.getenv("USE_GROQ", "false").lower() == "true")
    
    # API Keys
    groq_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    custom_api_key: Optional[str] = field(default_factory=lambda: os.getenv("CUSTOM_OPENAI_KEY"))
    
    # Default models
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4o"
    
    # Custom gateway settings
    custom_gateway_url: Optional[str] = field(
        default_factory=lambda: os.getenv("CUSTOM_GATEWAY_URL", 
                                          "https://gateway.ai-npe.humana.com/openai/deployments/{model}")
    )
    custom_gateway_headers: Dict[str, str] = field(default_factory=lambda: {
        "ai-gateway-version": "v2"
    })
    
    # LLM settings
    temperature: float = 0.3
    max_tokens: int = 1024
    
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
            raise ValueError(f"Unknown provider: {provider}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        if self.use_groq and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set but USE_GROQ=true")
        
        if not self.use_groq and not (self.openai_api_key or self.custom_api_key):
            raise ValueError("No API key found for OpenAI/Custom Gateway")
        
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
