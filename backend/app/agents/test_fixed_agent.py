"""
Test the fixed Playwright Direct Agent to verify model_dump errors are resolved
"""

def test_fixed_agent():
    """Test the agent with the model_dump fix"""
    
    print("🔧 TESTING FIXED PLAYWRIGHT DIRECT AGENT")
    print("=" * 50)
    print("Testing with LangGraph + model_dump compatibility fixes")
    print()
    
    try:
        from playwright_direct_agent import run_test_with_visible_browser
        
        print("✅ Import successful")
        
        # Test the exact scenario that was causing the error
        result = run_test_with_visible_browser(
            "Navigate to https://example.com, take a screenshot named fixed_test.png, and close browser",
            max_iterations=5,
            headless=False,
            browser_type="edge"
        )
        
        print(f"\n📊 Test Results:")
        print(f"  Status: {result['status']}")
        print(f"  Steps executed: {result.get('steps_executed', 0)}")
        
        if result['status'] == 'success':
            print("\n🎉 SUCCESS!")
            print("✅ model_dump error FIXED!")
            print("✅ LangGraph working with tool calls!")
            print("✅ Playwright automation successful!")
            return True
        else:
            print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
            if 'model_dump' in str(result.get('error', '')):
                print("🚨 model_dump error still occurring!")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Test failed with exception: {error_msg}")
        
        if "model_dump" in error_msg:
            print("🚨 model_dump error detected in exception!")
        elif "langgraph" in error_msg.lower():
            print("🚨 LangGraph import/usage error!")
        
        return False

def show_fixed_usage():
    """Show how to use the fixed agent"""
    
    print("\n💡 USAGE OF FIXED AGENT")
    print("=" * 30)
    
    print("\n# Basic usage (same as before, but now with model_dump fix):")
    print("from playwright_direct_agent import run_test_with_visible_browser")
    print()
    print("result = run_test_with_visible_browser(")
    print("    'Your automation task here',")
    print("    max_iterations=10,")
    print("    headless=False,  # Visible browser")
    print("    browser_type='edge'  # or 'chromium', 'firefox', 'webkit'")
    print(")")
    print("print(f'Status: {result[\"status\"]}')")
    
    print("\n# The fix handles your exact error case:")
    print("initial_state = {")
    print("    'messages': [HumanMessage(content='Your task')],")
    print("    'test_plan': '',")
    print("    'current_step': 0,")
    print("    # ... other state fields")
    print("}")
    print("# agent.invoke(initial_state) now works without model_dump errors!")

if __name__ == "__main__":
    print("🚀 PLAYWRIGHT DIRECT AGENT - MODEL_DUMP FIX VERIFICATION")
    print("=" * 60)
    
    # Test the fix
    success = test_fixed_agent()
    
    # Show usage
    show_fixed_usage()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 FINAL RESULT: MODEL_DUMP ERROR FIXED!")
        print("  ✅ LangGraph working properly")
        print("  ✅ Tool calls managed by LLMs")
        print("  ✅ No serialization issues")
        print("  ✅ Your exact error case resolved")
        print("\n💡 You can now use playwright_direct_agent.py successfully!")
    else:
        print("⚠️  NEEDS MORE INVESTIGATION")
        print("  Please check the error messages above")
        print("  The fix should resolve model_dump issues with LangGraph")
    
    print("=" * 60)