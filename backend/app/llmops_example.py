"""
Example: Using the new LLMOps structure to process test cases
"""

import os
from llmops import TestCaseGenerator, get_config


def main():
    """Main example showing LLMOps usage"""
    
    # Set up environment (example - adjust based on your setup)
    # For Groq:
    os.environ["USE_GROQ"] = "true"
    os.environ["GROQ_API_KEY"] = "your-groq-api-key"
    
    # For OpenAI/Custom Gateway:
    # os.environ["USE_GROQ"] = "false"
    # os.environ["CUSTOM_OPENAI_KEY"] = "your-key"
    # os.environ["CUSTOM_OPENAI_BASE_URL"] = "https://gateway.ai-npe.humana.com/openai/deployments/gpt-4o"
    
    print("=" * 70)
    print("LLMOps Test Case Generator Example")
    print("=" * 70)
    
    # Initialize generator (auto-detects provider from environment)
    generator = TestCaseGenerator()
    
    # Show provider info
    provider_info = generator.get_provider_info()
    print(f"\n✓ Using Provider: {provider_info['provider']}")
    print(f"✓ Model: {provider_info['model']}")
    print(f"✓ Temperature: {provider_info['temperature']}")
    
    # Path to your Excel file
    excel_path = "test_cases.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"\n❌ Excel file not found: {excel_path}")
        print("Please create an Excel file with test cases first.")
        return
    
    print(f"\n📖 Reading test cases from: {excel_path}")
    
    # Read test cases
    test_cases = generator.read_test_cases(
        excel_path=excel_path,
        sheet_name="Sheet1",
        # Optional: customize column mappings
        # test_id_col="Test ID",
        # module_col="Module",
        # description_col="Description"
    )
    
    print(f"✓ Found {len(test_cases)} test cases")
    
    # Generate prompts for all test cases
    print("\n🤖 Generating Playwright prompts using LLM...")
    prompts = generator.generate_batch(test_cases)
    
    print(f"✓ Generated {len(prompts)} prompts")
    
    # Display results
    print("\n" + "=" * 70)
    print("Generated Prompts:")
    print("=" * 70)
    
    for i, prompt in enumerate(prompts, 1):
        tc = prompt.test_case
        print(f"\n[{i}] Test Case: {tc.test_id}")
        print(f"    Module: {tc.module}")
        print(f"    Description: {tc.description[:80]}...")
        print(f"\n    Generated Prompt:")
        print(f"    {'-' * 66}")
        if prompt.generated_prompt:
            # Show first 300 chars of generated prompt
            preview = prompt.generated_prompt[:300]
            print(f"    {preview}...")
        else:
            print(f"    Error: {prompt.generated_prompt}")
        print(f"    {'-' * 66}")
    
    print("\n" + "=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
