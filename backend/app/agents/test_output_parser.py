#!/usr/bin/env python3
"""
Test Output Parser Approach - Complete elimination of model_dump errors
This test verifies the new output parser system works without Pydantic serialization issues
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright_direct_agent import run_test_with_visible_browser

def test_output_parser_agent():
    """Test the output parser approach with a simple automation task"""
    
    print("=" * 80)
    print("🧪 TESTING OUTPUT PARSER APPROACH")
    print("🎯 Goal: Eliminate all model_dump serialization issues") 
    print("🔧 Method: Direct function calls without @tool decorators")
    print("=" * 80)
    
    # Test request that will trigger multiple tool calls
    test_request = """
    Please automate a simple web test using Playwright:
    
    1. Navigate to https://httpbin.org/forms/post
    2. Take a screenshot to show the page loaded
    3. Get the page content to analyze the form structure
    4. Close the browser when done
    
    This test should work without any Pydantic model_dump errors.
    """
    
    print(f"📝 Test Request: {test_request.strip()}")
    print("\n🚀 Starting agent with OUTPUT PARSER approach...")
    
    try:
        # Run the agent with the new output parser system
        result = run_test_with_visible_browser(
            prompt=test_request,
            browser_type="chromium",  # Use chromium for this test
            max_iterations=5,
            headless=False
        )
        
        print(f"\n✅ Test completed successfully!")
        print(f"📊 Status: {result.get('status', 'unknown')}")
        print(f"🔄 Steps executed: {result.get('steps_executed', 0)}")
        print(f"⚠️  Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print("\n❌ Errors encountered:")
            for i, error in enumerate(result.get('errors', []), 1):
                print(f"  {i}. {error}")
        
        # Check if model_dump errors occurred
        errors = result.get('errors', [])
        model_dump_errors = [e for e in errors if 'model_dump' in str(e).lower()]
        
        if model_dump_errors:
            print(f"\n❌ MODEL_DUMP ERRORS STILL PRESENT: {len(model_dump_errors)}")
            for error in model_dump_errors:
                print(f"  - {error}")
            return False
        else:
            print(f"\n✅ NO MODEL_DUMP ERRORS - OUTPUT PARSER APPROACH SUCCESSFUL!")
            return True
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        
        # Check if it's a model_dump related error
        if 'model_dump' in str(e).lower():
            print("❌ This is a model_dump error - OUTPUT PARSER APPROACH NEEDS MORE WORK")
        else:
            print("ℹ️  This is a different type of error")
        
        import traceback
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_output_parser_agent()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 OUTPUT PARSER APPROACH: SUCCESS - No model_dump errors!")
        sys.exit(0) 
    else:
        print("😞 OUTPUT PARSER APPROACH: FAILED - Still has issues")
        sys.exit(1)