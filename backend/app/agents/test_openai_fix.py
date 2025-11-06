#!/usr/bin/env python3
"""
Test OpenAI version with model_dump fix
Verify that the OpenAI + LangGraph + Pydantic combination works without errors
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright_openai_agent import run_test_with_openai

def test_openai_model_dump_fix():
    """Test the OpenAI version for model_dump compatibility"""
    
    print("🔧 TESTING OPENAI + LANGGRAPH MODEL_DUMP FIX")
    print("=" * 60)
    
    # Test request
    test_request = """
    Please test this website using Playwright:
    
    1. Navigate to https://httpbin.org/forms/post
    2. Take a screenshot to document the page
    3. Get the page content to analyze the form
    4. Close the browser when done
    
    This should work with OpenAI without any model_dump errors.
    """
    
    print(f"📝 Test Request: {test_request.strip()}")
    print("\n🚀 Starting OpenAI agent...")
    
    try:
        # Run the agent with OpenAI
        result = run_test_with_openai(
            prompt=test_request,
            max_iterations=5,
            headless=False,  # Visible browser for testing
            browser_type="chromium"
        )
        
        print(f"\n✅ Test completed!")
        print(f"📊 Status: {result.get('status', 'unknown')}")
        print(f"🔄 Steps executed: {result.get('steps_executed', 0)}")
        print(f"⚠️  Errors: {len(result.get('errors', []))}")
        
        if result.get('errors'):
            print("\n❌ Errors encountered:")
            for i, error in enumerate(result.get('errors', []), 1):
                print(f"  {i}. {error}")
        
        # Check specifically for model_dump errors
        all_text = str(result)
        errors = result.get('errors', [])
        model_dump_errors = [e for e in errors if 'model_dump' in str(e).lower()]
        
        if model_dump_errors:
            print(f"\n❌ MODEL_DUMP ERRORS WITH OPENAI: {len(model_dump_errors)}")
            for error in model_dump_errors:
                print(f"  - {error}")
            return False
        elif 'model_dump' in all_text.lower():
            print(f"\n⚠️  MODEL_DUMP mentioned somewhere in results")
            print("   (but not in errors - might be debug messages)")
        else:
            print(f"\n✅ NO MODEL_DUMP ERRORS WITH OPENAI!")
        
        # Check if we got successful execution
        if result.get('status') == 'success':
            print("✅ OpenAI agent executed successfully")
            return True
        else:
            print("❌ OpenAI agent did not complete successfully")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        
        # Check if it's a model_dump related error
        if 'model_dump' in str(e).lower():
            print("❌ This IS a model_dump error with OpenAI - needs more work")
        else:
            print("ℹ️  This is a different type of error")
        
        import traceback
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🕐 OpenAI test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set in environment variables")
        print("   Please set your OpenAI API key to run this test")
        print("   Get one from: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    success = test_openai_model_dump_fix()
    
    print(f"\n🕐 OpenAI test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 OPENAI MODEL_DUMP FIX: SUCCESS!")
        print("   ✅ No model_dump errors with OpenAI + LangGraph")
        print("   ✅ Direct function calls working")
        print("   ✅ Proper message handling implemented")
    else:
        print("😞 OPENAI MODEL_DUMP FIX: Still needs work")