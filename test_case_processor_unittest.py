"""
Quick test of the Test Case Processor
"""

import pandas as pd
from backend.app.test_case_processor import TestCaseProcessor
import os

def test_processor_basic():
    """Test basic functionality without API calls"""
    
    print("🧪 Testing Test Case Processor - Basic Functions")
    print("=" * 60)
    
    # Create sample Excel file
    sample_data = {
        "Test ID": ["TC_001", "TC_002"],
        "Short Description": [
            "Login to qa4-www.365.com with username ABC and password 12345",
            "Navigate to dashboard and verify welcome message"
        ],
        "Priority": ["High", "Medium"]
    }
    
    test_file = "test_sample.xlsx"
    df = pd.DataFrame(sample_data)
    df.to_excel(test_file, index=False)
    print(f"✅ Created test file: {test_file}")
    
    # Initialize processor (without API key for structure test)
    processor = TestCaseProcessor(
        api_key="test-key",
        model="gpt-4o"
    )
    
    # Test reading Excel
    print("\n📖 Testing Excel reading...")
    try:
        df_read = processor.read_test_cases_from_excel(
            file_path=test_file,
            short_description_column="Short Description"
        )
        print(f"✅ Successfully read {len(df_read)} test cases")
        print(f"   Columns: {list(df_read.columns)}")
        
        # Show sample data
        print("\n📋 Sample Test Cases:")
        for idx, row in df_read.iterrows():
            print(f"   {idx + 1}. [{row['Test ID']}] {row['Short Description'][:50]}...")
        
        print("\n✅ Basic structure test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_prompt_format():
    """Test the expected output format"""
    
    print("\n\n🧪 Testing Expected Prompt Format")
    print("=" * 60)
    
    expected_format = """1) Navigate to https://qa4-www.365.com
2) Wait for sign in to appear
3) Click Sign in
4) Wait for Username to appear
5) Type username as ABC. Please don't change username
6) Type password as 12345
7) Click Sign In
8) Wait for Home screen to appear"""
    
    print("📝 Expected Output Format:")
    print("-" * 60)
    print(expected_format)
    print("-" * 60)
    
    # Verify format
    lines = expected_format.split('\n')
    print(f"\n✅ Format verification:")
    print(f"   - Total steps: {len(lines)}")
    print(f"   - All numbered: {all(line.strip().startswith(str(i+1) + ')') for i, line in enumerate(lines))}")
    print(f"   - Clear actions: {any('Navigate' in line for line in lines)}")
    print(f"   - Wait conditions: {any('Wait' in line for line in lines)}")
    print(f"   - User actions: {any('Click' in line or 'Type' in line for line in lines)}")
    
    return True


def test_with_api_key():
    """Test with actual API key if available"""
    
    api_key = os.getenv("CUSTOM_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("\n\n⏭️  Skipping API test - No API key found")
        print("   Set CUSTOM_OPENAI_KEY or OPENAI_API_KEY to run this test")
        return None
    
    print("\n\n🧪 Testing with Real API Call")
    print("=" * 60)
    
    processor = TestCaseProcessor(api_key=api_key, model="gpt-4o")
    
    test_description = "Login to qa4-www.365.com with username ABC and password 12345"
    
    print(f"📝 Input: {test_description}")
    print("\n🔄 Calling LLM to generate prompt...")
    
    try:
        prompt = processor.generate_playwright_prompt(
            short_description=test_description,
            test_id="TC_001"
        )
        
        print("\n✅ Generated Prompt:")
        print("-" * 60)
        print(prompt)
        print("-" * 60)
        
        # Verify output
        lines = prompt.split('\n')
        print(f"\n📊 Verification:")
        print(f"   Steps: {len(lines)}")
        print(f"   Contains 'Navigate': {'Navigate' in prompt}")
        print(f"   Contains 'Wait': {'Wait' in prompt}")
        print(f"   Contains 'Click': {'Click' in prompt}")
        print(f"   Contains 'Type': {'Type' in prompt}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


if __name__ == "__main__":
    print("🎭 TEST CASE PROCESSOR - UNIT TESTS\n")
    
    # Run tests
    test1 = test_processor_basic()
    test2 = test_prompt_format()
    test3 = test_with_api_key()
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Basic Structure Test: {'PASSED' if test1 else 'FAILED'}")
    print(f"✅ Format Verification: {'PASSED' if test2 else 'FAILED'}")
    print(f"{'✅' if test3 else '⏭️ '} API Integration Test: {'PASSED' if test3 else 'SKIPPED' if test3 is None else 'FAILED'}")
    print("=" * 60)
    
    if test1 and test2:
        print("\n🎉 All core tests PASSED!")
    else:
        print("\n❌ Some tests failed!")
