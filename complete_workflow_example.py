"""
Complete Workflow Example: Excel → LLM → Playwright Agent

This example demonstrates the full pipeline:
1. Read test cases from Excel
2. Convert to Playwright prompts using LLM
3. Execute with Playwright agent (optional)
"""

import os
import pandas as pd
import asyncio
from backend.app.test_case_processor import TestCaseProcessor
from backend.app.test_case_executor import TestCaseExecutor


def create_sample_test_cases():
    """Create a sample Excel file with test cases"""
    
    print("📝 Creating Sample Test Cases Excel File")
    print("=" * 70)
    
    # Sample test cases matching your requirements
    test_cases = {
        "Test ID": [
            "TC_001",
            "TC_002", 
            "TC_003"
        ],
        "Short Description": [
            "Login to qa4-www.365.com with username ABC and password 12345",
            "Navigate to user profile and update email address to test@example.com",
            "Search for product 'laptop' and add first result to shopping cart"
        ],
        "Priority": ["High", "Medium", "Low"],
        "Module": ["Authentication", "Profile Management", "Shopping"],
        "Expected Result": [
            "User successfully logged in and home screen displayed",
            "Email address updated successfully",
            "Product added to cart with confirmation message"
        ]
    }
    
    df = pd.DataFrame(test_cases)
    excel_file = "sample_qa_test_cases.xlsx"
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Created: {excel_file}")
    print(f"📊 Test Cases: {len(df)}")
    print("\n📋 Sample Test Cases:")
    for idx, row in df.iterrows():
        print(f"   {idx + 1}. [{row['Test ID']}] {row['Short Description'][:60]}...")
    
    return excel_file


def step1_process_test_cases(excel_file: str):
    """Step 1: Process test cases and generate Playwright prompts"""
    
    print("\n\n" + "=" * 70)
    print("STEP 1: Convert Excel Test Cases to Playwright Prompts")
    print("=" * 70)
    
    # Initialize processor
    processor = TestCaseProcessor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Process test cases
    processed_cases = processor.process_test_cases(
        excel_file=excel_file,
        short_description_column="Short Description",
        test_id_column="Test ID",
        output_file="playwright_prompts.xlsx"
    )
    
    # Display generated prompts
    processor.print_test_case_prompts(processed_cases)
    
    return processed_cases


async def step2_execute_test_cases(excel_file: str, headless: bool = False):
    """Step 2: Execute test cases with Playwright agent"""
    
    print("\n\n" + "=" * 70)
    print("STEP 2: Execute Test Cases with Playwright Agent")
    print("=" * 70)
    
    # Initialize executor
    executor = TestCaseExecutor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Browser configuration
    browser_config = {
        "headless": headless,      # Set to True for headless execution
        "browser_type": "chromium"  # chromium, firefox, webkit, or edge
    }
    
    # Execute all test cases
    results = await executor.execute_all_from_excel(
        excel_file=excel_file,
        short_description_column="Short Description",
        test_id_column="Test ID",
        browser_config=browser_config,
        save_results=True
    )
    
    return results


def step1_only_example():
    """Example: Only generate prompts without execution"""
    
    print("\n\n🎯 EXAMPLE: Generate Prompts Only (No Execution)")
    print("=" * 70)
    
    # Create sample file
    excel_file = create_sample_test_cases()
    
    # Process test cases
    processed = step1_process_test_cases(excel_file)
    
    print(f"\n✅ Generated {len(processed)} Playwright prompts")
    print(f"💾 Saved to: playwright_prompts.xlsx")
    print("\n💡 You can now review the prompts before execution")
    
    return processed


async def full_workflow_example():
    """Example: Complete workflow from Excel to execution"""
    
    print("\n\n🎯 EXAMPLE: Full Workflow (Generate + Execute)")
    print("=" * 70)
    
    # Create sample file
    excel_file = create_sample_test_cases()
    
    # Step 1: Generate prompts
    processed = step1_process_test_cases(excel_file)
    
    # Ask user confirmation
    print("\n" + "=" * 70)
    print("⚠️  EXECUTION CONFIRMATION")
    print("=" * 70)
    print("Generated prompts will now be executed with Playwright agent.")
    print("Browser will open and perform automated actions.")
    print("\nNote: Set headless=True in code for headless execution")
    
    # Step 2: Execute (uncomment to enable)
    # results = await step2_execute_test_cases(excel_file, headless=False)
    # return results
    
    print("\n💡 Execution skipped - uncomment code above to enable")
    return None


def quick_test_single_case():
    """Quick test: Single test case conversion"""
    
    print("\n\n🎯 QUICK TEST: Single Test Case")
    print("=" * 70)
    
    processor = TestCaseProcessor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"📝 Input Test Case:")
    print(f"   {test_description}")
    print(f"\n🔄 Converting to Playwright prompt...\n")
    
    prompt = processor.generate_playwright_prompt(
        short_description=test_description,
        test_id="TC_QUICK_001"
    )
    
    print("✅ Generated Playwright Prompt:")
    print("=" * 70)
    print(prompt)
    print("=" * 70)
    
    # Verify expected format
    expected_steps = [
        "Navigate to https://qa4-www.365.com",
        "Wait for sign in to appear",
        "Click Sign in",
        "Wait for Username to appear",
        "Type username as ABC",
        "Type password as 12345",
        "Click Sign In",
        "Wait for Home screen to appear"
    ]
    
    print("\n📊 Verification:")
    for step in expected_steps:
        if any(key_phrase in prompt for key_phrase in step.split()[:3]):
            print(f"   ✅ Contains: {step[:50]}...")
    
    return prompt


def main():
    """Main entry point with menu"""
    
    print("\n" + "=" * 70)
    print("🎭 TEST CASE PROCESSOR - COMPLETE WORKFLOW EXAMPLES")
    print("=" * 70)
    
    # Check API key
    if not (os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")):
        print("\n❌ Error: No API key found!")
        print("💡 Set CUSTOM_OPENAI_KEY or OPENAI_API_KEY environment variable")
        print("\nExample:")
        print("   export CUSTOM_OPENAI_KEY='your-key-here'")
        return
    
    # Run examples
    print("\n📚 Running Examples:\n")
    
    # Example 1: Quick single test
    quick_test_single_case()
    
    # Example 2: Generate prompts only
    step1_only_example()
    
    # Example 3: Full workflow (generation + execution)
    # Uncomment to run full automation
    # asyncio.run(full_workflow_example())
    
    print("\n\n" + "=" * 70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print("\n📋 Generated Files:")
    print("   - sample_qa_test_cases.xlsx (Input)")
    print("   - playwright_prompts.xlsx (Processed prompts)")
    print("   - sample_qa_test_cases_execution_results.xlsx (Results - if executed)")
    print("\n💡 Next Steps:")
    print("   1. Review generated prompts in playwright_prompts.xlsx")
    print("   2. Uncomment execution code to run with Playwright agent")
    print("   3. Check execution results in *_execution_results.xlsx")
    print("=" * 70)


if __name__ == "__main__":
    main()
