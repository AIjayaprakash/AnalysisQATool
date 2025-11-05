"""
Test script to verify Pydantic compatibility fix
This tests the model_dump error fix across different environments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pydantic_compatibility():
    """Test the Pydantic compatibility fix"""
    
    print("🧪 TESTING PYDANTIC COMPATIBILITY FIX")
    print("=====================================")
    
    try:
        # Import the agent module
        from playwright_direct_agent import run_test_with_visible_browser, safe_model_dump
        
        print("✅ Successfully imported playwright_direct_agent")
        
        # Test the safe_model_dump function
        print("\n🔧 Testing safe_model_dump function:")
        
        # Test with regular dict
        test_dict = {"test": "value"}
        result = safe_model_dump(test_dict)
        print(f"  Dict test: {result}")
        
        # Test with string (should not cause error)
        test_str = "test_string"
        result = safe_model_dump(test_str)
        print(f"  String test: {result}")
        
        print("\n🌐 Testing basic automation (will open browser):")
        
        # Run a simple test to verify tool execution works
        result = run_test_with_visible_browser(
            "Navigate to https://httpbin.org/html and take a screenshot named compatibility_test.png",
            max_iterations=3,
            browser_type="chromium"
        )
        
        print(f"✅ Test Result: {result['status']}")
        if result.get('errors'):
            print(f"❌ Errors: {result['errors']}")
        else:
            print("✅ No model_dump errors occurred!")
            
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        if "model_dump" in str(e):
            print("🚨 This is the model_dump error we're trying to fix!")
        return False

def test_multiple_environments():
    """Test compatibility across different scenarios"""
    
    print("\n🔄 TESTING MULTIPLE SCENARIOS")
    print("==============================")
    
    test_cases = [
        {
            "name": "Basic Navigation",
            "prompt": "Navigate to https://example.com and get page content",
            "max_iter": 3
        },
        {
            "name": "Screenshot Test", 
            "prompt": "Go to https://httpbin.org/html and take a screenshot",
            "max_iter": 3
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            from playwright_direct_agent import run_test_with_visible_browser
            
            result = run_test_with_visible_browser(
                test_case['prompt'],
                max_iterations=test_case['max_iter'],
                browser_type="chromium"
            )
            
            if result['status'] == 'success':
                print(f"✅ {test_case['name']}: SUCCESS")
                success_count += 1
            else:
                print(f"❌ {test_case['name']}: FAILED")
                if result.get('errors'):
                    print(f"   Errors: {result['errors']}")
                    
        except Exception as e:
            print(f"❌ {test_case['name']}: EXCEPTION - {e}")
            if "model_dump" in str(e):
                print("   🚨 This is a model_dump compatibility issue!")
    
    print(f"\n📊 FINAL RESULTS: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("Testing Playwright Direct Agent Pydantic Compatibility Fix")
    print("=" * 60)
    
    # Test basic compatibility
    basic_success = test_pydantic_compatibility()
    
    # Test multiple scenarios
    multi_success = test_multiple_environments()
    
    print("\n" + "=" * 60)
    print("COMPATIBILITY TEST SUMMARY")
    print("=" * 60)
    print(f"Basic compatibility: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Multiple scenarios: {'✅ PASS' if multi_success else '❌ FAIL'}")
    
    if basic_success and multi_success:
        print("\n🎉 ALL TESTS PASSED! The model_dump compatibility fix is working!")
    else:
        print("\n⚠️  Some tests failed. The compatibility fix may need more work.")