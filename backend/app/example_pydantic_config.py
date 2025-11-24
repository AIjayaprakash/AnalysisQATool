"""
Example: Using Pydantic BaseSettings for Configuration

This example demonstrates all the features of the new config system:
- Automatic .env file loading
- Type validation
- Field validation
- Default values
- Environment variable mapping
"""

from llmops.config.config import get_config, LLMOpsConfig

# Example 1: Basic usage - Get config instance
print("=" * 80)
print("Example 1: Basic Configuration Access")
print("=" * 80)

config = get_config()
print(f"Application Environment: {config.app_env}")
print(f"Using Groq: {config.use_groq}")
print(f"Browser Type: {config.browser_type}")

# Example 2: Using config properties
print("\n" + "=" * 80)
print("Example 2: Config Properties")
print("=" * 80)

if config.is_groq:
    print(f"Provider: Groq")
    print(f"Model: {config.groq_model}")
else:
    print(f"Provider: OpenAI")
    print(f"Model: {config.openai_model}")

# Example 3: Environment-based logic
print("\n" + "=" * 80)
print("Example 3: Environment-Based Logic")
print("=" * 80)

if config.app_env == "Production":
    print("🚀 Running in PRODUCTION mode")
    print("   - Debug logging: OFF")
    print("   - Error reporting: ON")
    print("   - Performance monitoring: ON")
elif config.app_env == "Staging":
    print("🧪 Running in STAGING mode")
    print("   - Debug logging: ON")
    print("   - Error reporting: ON")
    print("   - Performance monitoring: ON")
elif config.app_env == "Test-Development":
    print("🔧 Running in TEST-DEVELOPMENT mode")
    print("   - Debug logging: ON")
    print("   - Error reporting: OFF")
    print("   - Performance monitoring: OFF")
else:
    print(f"📋 Running in {config.app_env} mode")

# Example 4: Get LLM config
print("\n" + "=" * 80)
print("Example 4: Get LLM Configuration")
print("=" * 80)

try:
    llm_config = config.get_llm_config()
    print(f"Provider: {llm_config.provider}")
    print(f"Model: {llm_config.model}")
    print(f"Temperature: {llm_config.temperature}")
    print(f"Max Tokens: {llm_config.max_tokens}")
except Exception as e:
    print(f"⚠️  Could not get LLM config: {e}")

# Example 5: Export config as dictionary
print("\n" + "=" * 80)
print("Example 5: Export Configuration")
print("=" * 80)

config_dict = config.model_dump()
print(f"Total config fields: {len(config_dict)}")
print(f"Config keys: {', '.join(config_dict.keys())}")

# Example 6: Validation features
print("\n" + "=" * 80)
print("Example 6: Pydantic Validation Features")
print("=" * 80)

print("✅ Field validations:")
print(f"   - Temperature range: 0.0 to 2.0 (current: {config.temperature})")
print(f"   - Max tokens: must be > 0 (current: {config.max_tokens})")
print(f"   - Case-insensitive: APP_ENV, app_env, App_Env all work")
print(f"   - Type coercion: '0.3' from .env becomes float 0.3")

# Example 7: Create custom config instance
print("\n" + "=" * 80)
print("Example 7: Create Custom Config Instance")
print("=" * 80)

# You can create a new instance with custom values
custom_config = LLMOpsConfig(
    app_env="Production",
    use_groq=True,
    temperature=0.7,
    max_tokens=2048
)

print(f"Custom APP_ENV: {custom_config.app_env}")
print(f"Custom temperature: {custom_config.temperature}")
print(f"Custom max_tokens: {custom_config.max_tokens}")

print("\n" + "=" * 80)
print("✅ All Examples Complete!")
print("=" * 80)
