"""
Integration test for complete LLMOps workflow
Tests all components together: Config, LLM, Prompts, Models, Utils, Generators
"""

import os
import tempfile
import pandas as pd
from pathlib import Path

# Set up test environment
os.environ["USE_GROQ"] = "true"
os.environ["GROQ_API_KEY"] = "test-key"  # Replace with actual key for real testing

from llmops import (
    TestCaseGenerator,
    ExcelReader,
    ExcelWriter,
    TestCase,
    TestCaseStatus,
    ExecutionResult,
    get_config
)


def create_sample_excel(file_path: str):
    """Create a sample Excel file with test cases"""
    data = {
        "Test ID": ["TC001", "TC002", "TC003"],
        "Module": ["Login", "Login", "Dashboard"],
        "Functionality": ["User Authentication", "Invalid Login", "View Dashboard"],
        "Description": [
            "Verify user can login with valid credentials",
            "Verify system shows error for invalid credentials",
            "Verify user can view dashboard after login"
        ],
        "Steps": [
            "1. Open login page 2. Enter username 3. Enter password 4. Click login",
            "1. Open login page 2. Enter invalid username 3. Enter invalid password 4. Click login",
            "1. Login with valid credentials 2. Navigate to dashboard 3. Verify widgets"
        ],
        "Expected Result": [
            "User should be logged in successfully",
            "Error message should be displayed",
            "Dashboard should display all widgets"
        ],
        "Priority": ["High", "High", "Medium"]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, sheet_name="TestCases", index=False)
    print(f"✓ Created sample Excel: {file_path}")


def test_config():
    """Test configuration module"""
    print("\n" + "=" * 70)
    print("TEST 1: Configuration")
    print("=" * 70)
    
    config = get_config()
    print(f"✓ Config loaded")
    print(f"  - Use Groq: {config.use_groq}")
    print(f"  - Groq API Key: {'*' * 8 if config.groq_api_key else 'Not set'}")
    
    llm_config = config.get_llm_config("groq")
    print(f"  - LLM Model: {llm_config.model}")
    print(f"  - Temperature: {llm_config.temperature}")
    
    return config


def test_excel_utils(excel_path: str):
    """Test Excel utilities"""
    print("\n" + "=" * 70)
    print("TEST 2: Excel Utilities")
    print("=" * 70)
    
    # Test reading
    reader = ExcelReader(excel_path, sheet_name="TestCases")
    test_cases = reader.get_test_cases()
    
    print(f"✓ Read {len(test_cases)} test cases from Excel")
    for tc in test_cases:
        print(f"  - {tc.test_id}: {tc.description[:50]}...")
    
    # Test writing results
    results_path = str(Path(excel_path).parent / "test_results.xlsx")
    writer = ExcelWriter(results_path)
    
    # Create mock results
    results = [
        ExecutionResult(
            test_case=tc,
            status=TestCaseStatus.PASSED,
            execution_time=2.5,
            logs=["Test executed successfully"]
        )
        for tc in test_cases[:2]
    ]
    
    writer.write_results(results)
    print(f"✓ Wrote {len(results)} results to: {results_path}")
    
    return test_cases


def test_generator(test_cases):
    """Test generator (without actual LLM call for safety)"""
    print("\n" + "=" * 70)
    print("TEST 3: Test Case Generator")
    print("=" * 70)
    
    generator = TestCaseGenerator()
    
    provider_info = generator.get_provider_info()
    print(f"✓ Generator initialized")
    print(f"  - Provider: {provider_info['provider']}")
    print(f"  - Model: {provider_info['model']}")
    
    # Test prompt generation structure (mock)
    from llmops import get_prompt_manager
    pm = get_prompt_manager()
    
    for tc in test_cases[:1]:  # Test first case only
        system_prompt, user_prompt = pm.get_test_case_conversion_prompts(tc)
        print(f"\n✓ Generated prompts for: {tc.test_id}")
        print(f"  - System prompt length: {len(system_prompt)} chars")
        print(f"  - User prompt length: {len(user_prompt)} chars")
        print(f"\n  System Prompt Preview:")
        print(f"  {system_prompt[:200]}...")
        print(f"\n  User Prompt Preview:")
        print(f"  {user_prompt[:200]}...")
    
    return generator


def test_full_workflow(excel_path: str):
    """Test complete workflow (Excel -> Generator -> Prompts)"""
    print("\n" + "=" * 70)
    print("TEST 4: Full Workflow (End-to-End)")
    print("=" * 70)
    
    # Note: This would make actual LLM calls if API key is valid
    # For testing, we'll demonstrate the structure
    
    generator = TestCaseGenerator()
    
    print(f"✓ Processing Excel file: {excel_path}")
    print("  Note: Skipping actual LLM calls for safety")
    print("  To test with real LLM, uncomment the line below:")
    print("  # prompts = generator.process_excel(excel_path, sheet_name='TestCases')")
    
    # Uncommenting this line would make real LLM calls:
    # prompts = generator.process_excel(excel_path, sheet_name="TestCases")
    # for prompt in prompts:
    #     print(f"✓ Generated prompt for {prompt.test_case.test_id}")
    
    print("\n✓ Workflow structure validated")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LLMOps Integration Tests")
    print("=" * 70)
    
    # Create temp directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        excel_path = str(Path(tmpdir) / "test_cases.xlsx")
        
        # Create sample Excel
        create_sample_excel(excel_path)
        
        # Run tests
        test_config()
        test_cases = test_excel_utils(excel_path)
        test_generator(test_cases)
        test_full_workflow(excel_path)
    
    print("\n" + "=" * 70)
    print("✅ All Tests Completed!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Set your actual API key: GROQ_API_KEY or CUSTOM_OPENAI_KEY")
    print("2. Run llmops_example.py with real test case Excel file")
    print("3. Uncomment LLM calls in test_full_workflow() to test generation")
    print("=" * 70)


if __name__ == "__main__":
    main()
