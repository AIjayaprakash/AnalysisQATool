"""Quick import test for LLMOps package"""

from llmops import (
    TestCaseGenerator,
    get_config,
    ExcelReader,
    ExcelWriter,
    TestCase,
    TestCasePrompt,
    ExecutionResult,
    TestCaseStatus,
    LLMProvider,
    GroqProvider,
    OpenAIProvider
)

print("=" * 70)
print("LLMOps Import Verification")
print("=" * 70)

print("\n✅ All imports successful!")
print("\nImported components:")
print("  - TestCaseGenerator")
print("  - get_config")
print("  - ExcelReader")
print("  - ExcelWriter")
print("  - TestCase")
print("  - TestCasePrompt")
print("  - ExecutionResult")
print("  - TestCaseStatus")
print("  - LLMProvider")
print("  - GroqProvider")
print("  - OpenAIProvider")

config = get_config()
print(f"\n✅ Config loaded successfully")
print(f"  - Provider: {'Groq' if config.use_groq else 'OpenAI'}")
print(f"  - Model: {config.get_llm_config('groq' if config.use_groq else 'openai').model}")

print("\n" + "=" * 70)
print("✅ LLMOps Package is ready to use!")
print("=" * 70)
