"""
Example: Using Test Case Processor to convert Excel test cases to Playwright prompts
"""

import os
from backend.app.test_case_processor import TestCaseProcessor

def example_basic_usage():
    """Basic example: Process test cases from Excel"""
    
    print("🚀 Test Case Processor - Basic Usage Example")
    print("=" * 60)
    
    # Initialize processor
    processor = TestCaseProcessor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Process test cases from Excel file
    # Make sure your Excel file has a "Short Description" column
    excel_file = "your_test_cases.xlsx"  # Replace with your file
    
    try:
        processed_cases = processor.process_test_cases(
            excel_file=excel_file,
            short_description_column="Short Description",  # Your column name
            test_id_column="Test ID",  # Optional: column with test IDs
            output_file="processed_playwright_prompts.xlsx"  # Save results
        )
        
        # Print the generated prompts
        processor.print_test_case_prompts(processed_cases)
        
        # Example: Get a specific test case prompt
        if processed_cases:
            first_case = processed_cases[0]
            print("\n🎯 Example - First Test Case Prompt:")
            print(first_case['detailed_prompt'])
        
    except FileNotFoundError:
        print(f"❌ File not found: {excel_file}")
        print("💡 Creating a demo example instead...")
        example_with_demo_data(processor)


def example_with_demo_data(processor: TestCaseProcessor = None):
    """Example with demo data - creates sample Excel file"""
    
    import pandas as pd
    
    if processor is None:
        processor = TestCaseProcessor(
            api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
            model="gpt-4o"
        )
    
    # Create sample test cases
    sample_data = {
        "Test ID": ["TC_001"],
        "Short Description": [
            "Login to qa4-www.365.com with username ABC and password 12345"
        ],
        "Priority": ["High"],
        "Module": ["Authentication"]
    }
    
    # Save to Excel
    sample_file = "demo_test_cases.xlsx"
    df = pd.DataFrame(sample_data)
    df.to_excel(sample_file, index=False)
    print(f"\n✅ Created demo file: {sample_file}")
    
    # Process the demo file
    processed_cases = processor.process_test_cases(
        excel_file=sample_file,
        short_description_column="Short Description",
        test_id_column="Test ID",
        output_file="demo_processed_prompts.xlsx"
    )
    
    # Print results
    processor.print_test_case_prompts(processed_cases)
    
    return processed_cases


def example_single_test_case():
    """Example: Convert a single test case description to Playwright prompt"""
    
    print("\n🎯 Single Test Case Conversion Example")
    print("=" * 60)
    
    processor = TestCaseProcessor(
        api_key=os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Single test case
    short_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"📝 Input: {short_description}")
    print("\n🤖 Generating detailed Playwright prompt...\n")
    
    detailed_prompt = processor.generate_playwright_prompt(
        short_description=short_description,
        test_id="TC_001"
    )
    
    print("✅ Generated Prompt:")
    print("-" * 60)
    print(detailed_prompt)
    print("-" * 60)
    
    return detailed_prompt


def example_with_custom_columns():
    """Example: Process Excel with custom column names"""
    
    import pandas as pd
    
    processor = TestCaseProcessor()
    
    # Create Excel with custom column names
    data = {
        "ID": ["001", "002"],
        "Test Scenario": [
            "User login with valid credentials",
            "User logout successfully"
        ],
        "URL": [
            "https://qa4-www.365.com",
            "https://qa4-www.365.com"
        ]
    }
    
    custom_file = "custom_columns_test_cases.xlsx"
    pd.DataFrame(data).to_excel(custom_file, index=False)
    
    # Process with custom column names
    processed = processor.process_test_cases(
        excel_file=custom_file,
        short_description_column="Test Scenario",  # Custom column name
        test_id_column="ID",  # Custom ID column
        output_file="custom_processed.xlsx"
    )
    
    processor.print_test_case_prompts(processed)


if __name__ == "__main__":
    import sys
    
    # Check if API key is set
    if not (os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")):
        print("❌ Error: No API key found!")
        print("💡 Please set CUSTOM_OPENAI_KEY or OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    print("🎭 Test Case Processor Examples\n")
    
    # Run examples
    print("\n" + "=" * 60)
    print("Example 1: Single Test Case Conversion")
    print("=" * 60)
    example_single_test_case()
    
    print("\n\n" + "=" * 60)
    print("Example 2: Process Demo Excel File")
    print("=" * 60)
    example_with_demo_data()
    
    print("\n\n✅ All examples completed!")
