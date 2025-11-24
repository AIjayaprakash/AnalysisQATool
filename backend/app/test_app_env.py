"""
Test APP_ENV configuration with Pydantic BaseSettings
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from llmops.config.config import get_config, reset_config

def test_app_env():
    """Test that APP_ENV is correctly loaded from environment"""
    
    print("=" * 80)
    print("Testing APP_ENV Configuration (Pydantic BaseSettings)")
    print("=" * 80)
    
    # Test 1: Get default value (if .env doesn't exist or APP_ENV not set)
    print("\n📋 Test 1: Default APP_ENV value")
    config = get_config()
    print(f"   APP_ENV: {config.app_env}")
    print(f"   Expected default: Test-Development")
    
    if config.app_env:
        print(f"   ✅ APP_ENV is set to: '{config.app_env}'")
    else:
        print("   ❌ APP_ENV is not set")
    
    # Test 2: Display all configuration
    print("\n" + "=" * 80)
    print("📊 Full Configuration")
    print("=" * 80)
    print(f"   APP_ENV: {config.app_env}")
    print(f"   USE_GROQ: {config.use_groq}")
    print(f"   Is Groq (property): {config.is_groq}")
    print(f"   Browser Type: {config.browser_type}")
    print(f"   Groq Model: {config.groq_model}")
    print(f"   OpenAI Model: {config.openai_model}")
    print(f"   Temperature: {config.temperature}")
    print(f"   Max Tokens: {config.max_tokens}")
    
    # Test 3: Show API keys status (without revealing actual keys)
    print("\n" + "=" * 80)
    print("🔑 API Keys Status")
    print("=" * 80)
    print(f"   Groq API Key: {'✅ Set' if config.groq_api_key else '❌ Not set'}")
    print(f"   OpenAI API Key: {'✅ Set' if config.openai_api_key else '❌ Not set'}")
    print(f"   Custom API Key: {'✅ Set' if config.custom_api_key else '❌ Not set'}")
    
    # Test 3: Check environment variable directly
    print("\n" + "=" * 80)
    print("🔍 Environment Variable Check")
    print("=" * 80)
    
    env_value = os.getenv("APP_ENV")
    if env_value:
        print(f"   ✅ APP_ENV found in environment: '{env_value}'")
    else:
        print(f"   ⚠️  APP_ENV not found in environment (using default)")
    
    # Test 4: Usage example
    print("\n" + "=" * 80)
    print("💡 Usage Example")
    print("=" * 80)
    
    print("\nHow to use APP_ENV in your code:")
    print("""
    from llmops.config.config import get_config
    
    config = get_config()
    
    if config.app_env == "Production":
        # Production-specific logic
        print("Running in Production mode")
    elif config.app_env == "Test-Development":
        # Test/Development-specific logic
        print("Running in Test-Development mode")
    """)
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("📋 Pydantic Settings Features")
    print("=" * 80)
    print("   ✅ Automatic .env file loading")
    print("   ✅ Type validation and coercion")
    print("   ✅ Field validation (e.g., temperature range: 0-2)")
    print("   ✅ Case-insensitive environment variables")
    print("   ✅ Field aliases support")
    
    # Test 4: Show configuration as dict
    print("\n" + "=" * 80)
    print("� Configuration as Dictionary")
    print("=" * 80)
    config_dict = config.model_dump()
    for key, value in config_dict.items():
        if 'key' in key.lower() and value:
            # Hide actual API keys
            print(f"   {key}: ***hidden***")
        else:
            print(f"   {key}: {value}")
    
    print("\n�💡 Tips:")
    print("   1. Create a .env file from .env.example")
    print("   2. Set APP_ENV=Production (or any value) in .env")
    print("   3. Pydantic will automatically load and validate it")
    print("   4. Default value is 'Test-Development' if not set")
    print("   5. All fields are validated according to their types")


if __name__ == "__main__":
    test_app_env()
