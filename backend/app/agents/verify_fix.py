"""
Simple verification script for the Pydantic compatibility fix
Run this in your different environment to verify the fix works
"""

def verify_compatibility():
    """Quick verification of the model_dump fix"""
    
    print("🔍 VERIFYING PYDANTIC COMPATIBILITY FIX")
    print("========================================")
    
    try:
        # Check Pydantic version
        import pydantic
        print(f"✅ Pydantic version: {pydantic.VERSION}")
        
        # Test import
        from playwright_direct_agent import run_test_with_visible_browser, safe_model_dump
        print("✅ Successfully imported playwright_direct_agent")
        
        # Test safe_model_dump with different inputs
        print("\n🧪 Testing safe_model_dump compatibility:")
        
        # Test with string (the problematic case)
        test_result = safe_model_dump("test_string")
        print(f"  String input: '{test_result}' ✅")
        
        # Test with dict
        test_result = safe_model_dump({"key": "value"})
        print(f"  Dict input: {test_result} ✅")
        
        print("\n🎭 Testing simple browser automation:")
        
        # Run minimal test
        result = run_test_with_visible_browser(
            "Navigate to https://example.com and take a screenshot named verify_test.png",
            max_iterations=2,
            browser_type="chromium"
        )
        
        if result['status'] == 'success':
            print("✅ Browser automation completed successfully!")
            print("✅ No 'model_dump' attribute errors occurred!")
            return True
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Verification failed: {error_msg}")
        
        if "'str' object has no attribute 'model_dump'" in error_msg:
            print("🚨 The original model_dump error is still occurring!")
            print("   This means the compatibility fix needs to be applied.")
        
        return False

if __name__ == "__main__":
    print("Playwright Direct Agent - Compatibility Verification")
    print("=" * 55)
    
    success = verify_compatibility()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 VERIFICATION PASSED!")
        print("   The compatibility fix is working in this environment.")
        print("   You can now use the agent without model_dump errors.")
    else:
        print("⚠️  VERIFICATION FAILED!")
        print("   The compatibility fix may need adjustment for this environment.")
        print("   Please check the error messages above.")
    
    print("=" * 55)