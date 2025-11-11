"""
Example: Using Test Case Processor with Groq or OpenAI/Custom Gateway

This example shows how to switch between Groq and OpenAI/Custom Gateway
using environment variables or code configuration.
"""

import os
from backend.app.test_case_processor import TestCaseProcessor


def example_with_groq():
    """Example: Using Groq LLM"""
    
    print("\n" + "=" * 70)
    print("🚀 EXAMPLE 1: Using Groq LLM")
    print("=" * 70)
    
    # Initialize processor with Groq
    processor = TestCaseProcessor(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",  # Updated Groq model
        use_groq=True
    )
    
    # Test single conversion
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"\n📝 Input: {test_description}")
    print("\n🔄 Converting with Groq LLM...\n")
    
    try:
        prompt = processor.generate_playwright_prompt(
            short_description=test_description,
            test_id="TC_GROQ_001"
        )
        
        print("✅ Generated Prompt (using Groq):")
        print("-" * 70)
        print(prompt)
        print("-" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_with_openai():
    """Example: Using OpenAI/Custom Gateway"""
    
    print("\n" + "=" * 70)
    print("🚀 EXAMPLE 2: Using OpenAI/Custom Gateway")
    print("=" * 70)
    
    # Initialize processor with OpenAI/Custom Gateway
    processor = TestCaseProcessor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",  # OpenAI model
        use_groq=False
    )
    
    # Test single conversion
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"\n📝 Input: {test_description}")
    print("\n🔄 Converting with OpenAI/Custom Gateway...\n")
    
    try:
        prompt = processor.generate_playwright_prompt(
            short_description=test_description,
            test_id="TC_OPENAI_001"
        )
        
        print("✅ Generated Prompt (using OpenAI/Custom Gateway):")
        print("-" * 70)
        print(prompt)
        print("-" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_with_env_variable():
    """Example: Using USE_GROQ environment variable"""
    
    print("\n" + "=" * 70)
    print("🚀 EXAMPLE 3: Auto-detect using USE_GROQ environment variable")
    print("=" * 70)
    
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
    
    if use_groq:
        print("✅ USE_GROQ=true detected - Using Groq")
        model = "llama-3.1-70b-versatile"
    else:
        print("✅ USE_GROQ not set or false - Using OpenAI/Custom Gateway")
        model = "gpt-4o"
    
    # Initialize processor (will auto-detect based on USE_GROQ)
    processor = TestCaseProcessor()
    
    # Test single conversion
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"\n📝 Input: {test_description}")
    print(f"🔄 Converting with {'Groq' if use_groq else 'OpenAI/Custom Gateway'}...\n")
    
    try:
        prompt = processor.generate_playwright_prompt(
            short_description=test_description,
            test_id="TC_AUTO_001"
        )
        
        print(f"✅ Generated Prompt (using {'Groq' if use_groq else 'OpenAI/Custom Gateway'}):")
        print("-" * 70)
        print(prompt)
        print("-" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_groq_models():
    """Example: Different Groq models"""
    
    print("\n" + "=" * 70)
    print("🚀 EXAMPLE 4: Using Different Groq Models")
    print("=" * 70)
    
    groq_models = [
        "llama-3.3-70b-versatile",  # Latest Llama 3.3
        "llama-3.1-8b-instant",     # Fast Llama
        "mixtral-8x7b-32768"        # Mixtral (if still available)
    ]
    
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    for model in groq_models:
        print(f"\n📊 Testing model: {model}")
        print("-" * 70)
        
        try:
            processor = TestCaseProcessor(
                api_key=os.getenv("GROQ_API_KEY"),
                model=model,
                use_groq=True
            )
            
            prompt = processor.generate_playwright_prompt(
                short_description=test_description,
                test_id=f"TC_{model.split('-')[0].upper()}_001"
            )
            
            print(f"✅ Result: {len(prompt)} characters")
            print(f"   First line: {prompt.split(chr(10))[0]}")
            
        except Exception as e:
            print(f"❌ Error with {model}: {e}")


def main():
    """Main function to run examples"""
    
    print("\n" + "=" * 70)
    print("🎭 TEST CASE PROCESSOR - GROQ vs OPENAI EXAMPLES")
    print("=" * 70)
    
    # Check which API keys are available
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_openai = bool(os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"))
    
    print("\n📋 API Key Status:")
    print(f"   Groq API Key: {'✅ Found' if has_groq else '❌ Not set (set GROQ_API_KEY)'}")
    print(f"   OpenAI/Custom Key: {'✅ Found' if has_openai else '❌ Not set (set CUSTOM_OPENAI_KEY or OPENAI_API_KEY)'}")
    print(f"   USE_GROQ env: {os.getenv('USE_GROQ', 'not set (defaults to false)')}")
    
    if not has_groq and not has_openai:
        print("\n❌ Error: No API keys found!")
        print("\n💡 Set one of these environment variables:")
        print("   - For Groq: export GROQ_API_KEY='your-groq-key' and export USE_GROQ=true")
        print("   - For OpenAI: export OPENAI_API_KEY='your-openai-key'")
        print("   - For Custom Gateway: export CUSTOM_OPENAI_KEY='your-key'")
        return
    
    # Run examples based on available keys
    print("\n🚀 Running Examples...\n")
    
    if has_groq:
        print("\n" + "═" * 70)
        example_with_groq()
    
    if has_openai:
        print("\n" + "═" * 70)
        example_with_openai()
    
    # Always run env variable example
    print("\n" + "═" * 70)
    example_with_env_variable()
    
    # Run Groq models comparison if Groq is available
    if has_groq:
        print("\n" + "═" * 70)
        example_groq_models()
    
    print("\n\n" + "=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    
    print("\n💡 Quick Setup Guide:")
    print("\n   To use Groq:")
    print("   $ export GROQ_API_KEY='your-groq-api-key'")
    print("   $ export USE_GROQ=true")
    print("   $ python groq_openai_example.py")
    
    print("\n   To use OpenAI/Custom Gateway:")
    print("   $ export CUSTOM_OPENAI_KEY='your-key'  # or OPENAI_API_KEY")
    print("   $ export USE_GROQ=false  # or don't set it")
    print("   $ python groq_openai_example.py")
    
    print("\n📚 Recommended Groq Models:")
    print("   - llama-3.3-70b-versatile (latest, recommended)")
    print("   - llama-3.1-8b-instant (fast)")
    print("   - gemma2-9b-it (lightweight)")
    print("=" * 70)


if __name__ == "__main__":
    main()
