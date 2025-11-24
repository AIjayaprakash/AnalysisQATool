# Pydantic BaseSettings Configuration - Implementation Guide

## Overview
Converted the configuration system from Python dataclasses to **Pydantic BaseSettings** for better environment variable management and validation.

## Key Changes

### 1. **Imports**
```python
from pydantic import Field
from pydantic_settings import BaseSettings
```

### 2. **LLMOpsConfig Class**
Changed from `@dataclass` to `BaseSettings`:

```python
class LLMOpsConfig(BaseSettings):
    """Main configuration for LLMOps - loads from .env file"""
    
    # Application Environment
    app_env: str = Field(default="Test-Development", description="Application environment")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
```

## Features

### ✅ Automatic .env Loading
- No need for `load_dotenv()` - Pydantic handles it automatically
- Set `env_file = ".env"` in the `Config` class

### ✅ Type Validation
```python
temperature: float = Field(default=0.3, ge=0.0, le=2.0)  # Must be between 0-2
max_tokens: int = Field(default=1024, gt=0)  # Must be > 0
```

### ✅ Field Descriptions
```python
app_env: str = Field(default="Test-Development", description="Application environment")
```

### ✅ Case-Insensitive
All these work the same:
- `APP_ENV=Production`
- `app_env=Production`
- `App_Env=Production`

### ✅ Field Aliases
```python
custom_api_key: Optional[str] = Field(default=None, alias="CUSTOM_OPENAI_KEY")
```

### ✅ Extra Fields Ignored
Unknown fields in .env are automatically ignored with `extra = "ignore"`

## Usage

### Basic Usage
```python
from llmops.config.config import get_config

config = get_config()
print(config.app_env)  # Access fields directly
```

### Environment-Based Logic
```python
if config.app_env == "Production":
    # Production settings
    enable_debug = False
elif config.app_env == "Test-Development":
    # Development settings
    enable_debug = True
```

### Export Configuration
```python
config_dict = config.model_dump()  # Convert to dictionary
print(config_dict)
```

### Create Custom Instance
```python
custom_config = LLMOpsConfig(
    app_env="Production",
    temperature=0.7
)
```

## Environment Variables (.env file)

```bash
# Application Environment
APP_ENV=Test-Development

# Provider Selection
USE_GROQ=false

# API Keys
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key

# Models
GROQ_MODEL=llama-3.3-70b-versatile
OPENAI_MODEL=gpt-4o

# Browser
BROWSER_TYPE=edge

# LLM Settings
TEMPERATURE=0.3
MAX_TOKENS=1024
```

## Validation Rules

| Field | Type | Validation | Default |
|-------|------|------------|---------|
| `app_env` | str | - | Test-Development |
| `use_groq` | bool | - | False |
| `temperature` | float | 0.0 ≤ x ≤ 2.0 | 0.3 |
| `max_tokens` | int | x > 0 | 1024 |
| `groq_model` | str | - | llama-3.3-70b-versatile |
| `openai_model` | str | - | gpt-4o |
| `browser_type` | str | - | edge |

## Migration from Dataclass

### Before (Dataclass)
```python
@dataclass
class LLMOpsConfig:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "Test-Development"))
```

### After (Pydantic)
```python
class LLMOpsConfig(BaseSettings):
    app_env: str = Field(default="Test-Development", description="Application environment")
    
    class Config:
        env_file = ".env"
```

## Benefits

1. **Automatic Validation**: Pydantic validates types and constraints automatically
2. **Better Error Messages**: Clear validation errors with field names
3. **Documentation**: Field descriptions serve as inline documentation
4. **Type Safety**: Full type hints support
5. **Easier Testing**: Can create instances with custom values easily
6. **IDE Support**: Better autocomplete and type checking

## Testing

Run the test script:
```bash
python backend/app/test_app_env.py
```

Or the examples:
```bash
python backend/app/example_pydantic_config.py
```

## Files Modified

1. `backend/app/llmops/config/config.py` - Main configuration file
2. `.env.example` - Added APP_ENV example
3. `backend/app/test_app_env.py` - Test script
4. `backend/app/example_pydantic_config.py` - Usage examples
