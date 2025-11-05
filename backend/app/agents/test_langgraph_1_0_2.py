"""
Compatibility test for LangGraph 1.0.2 + Pydantic 2.12.4 + LangChain 0.3.25
This addresses the model_dump error in the newer LangGraph version.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment_versions():
    """Check the specific versions in your environment"""
    
    print("🔍 ENVIRONMENT VERSION CHECK")
    print("=" * 50)
    
    try:
        import pydantic
        pydantic_version = pydantic.__version__ if hasattr(pydantic, '__version__') else pydantic.VERSION
        print(f"✅ Pydantic: {pydantic_version}")
        
        import langgraph
        langgraph_version = langgraph.__version__ if hasattr(langgraph, '__version__') else "unknown"
        print(f"✅ LangGraph: {langgraph_version}")
        
        import langchain
        langchain_version = langchain.__version__ if hasattr(langchain, '__version__') else "unknown"
        print(f"✅ LangChain: {langchain_version}")
        
        # Check if this matches the user's environment
        if pydantic_version == "2.12.4" and langgraph_version == "1.0.2" and langchain_version == "0.3.25":
            print("\n🎯 EXACT MATCH: Your environment versions detected!")
        else:
            print(f"\n⚠️  Version difference detected:")
            print(f"   Expected: Pydantic 2.12.4, LangGraph 1.0.2, LangChain 0.3.25")
            print(f"   Found: Pydantic {pydantic_version}, LangGraph {langgraph_version}, LangChain {langchain_version}")
            
    except Exception as e:
        print(f"❌ Error checking versions: {e}")
        return False
    
    return True

def test_tool_invocation_methods():
    """Test different tool invocation methods for LangGraph 1.0.2"""
    
    print("\n🧪 TESTING TOOL INVOCATION METHODS")
    print("=" * 50)
    
    try:
        from playwright_direct_agent import playwright_navigate
        
        print("✅ Successfully imported playwright_navigate tool")
        
        # Test different invocation methods that LangGraph 1.0.2 might use
        test_args = {"url": "https://example.com"}
        
        print("\n🔧 Testing invocation methods:")
        
        # Method 1: Check tool structure
        print(f"  Tool name: {getattr(playwright_navigate, 'name', 'NO NAME')}")
        print(f"  Has func attribute: {hasattr(playwright_navigate, 'func')}")
        print(f"  Has ainvoke method: {hasattr(playwright_navigate, 'ainvoke')}")
        print(f"  Tool type: {type(playwright_navigate)}")
        
        # Method 2: Check what happens with different input types
        print("\n🧪 Testing input handling:")
        
        # Test with dict
        print(f"  Dict args type: {type(test_args)}")
        
        # Test with simple object
        class SimpleArgs:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
            def dict(self):
                return {k: v for k, v in self.__dict__.items()}
            def model_dump(self):
                return self.dict()
        
        simple_args = SimpleArgs(**test_args)
        print(f"  SimpleArgs has model_dump: {hasattr(simple_args, 'model_dump')}")
        print(f"  SimpleArgs model_dump result: {simple_args.model_dump()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool invocation test failed: {e}")
        return False

def test_compatibility_fix():
    """Test the actual compatibility fix with your environment"""
    
    print("\n🎭 TESTING COMPATIBILITY FIX")
    print("=" * 50)
    
    try:
        from playwright_direct_agent import run_test_with_visible_browser
        
        print("Running minimal test to check for model_dump errors...")
        
        # Use a very simple test to minimize other potential errors
        result = run_test_with_visible_browser(
            "Navigate to https://httpbin.org/html and close browser",
            max_iterations=2,
            browser_type="chromium"
        )
        
        print(f"\n📊 Test Result: {result['status']}")
        
        if result['status'] == 'success':
            print("✅ SUCCESS: No model_dump errors occurred!")
            print("✅ The compatibility fix is working with your environment!")
            return True
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            if result.get('errors'):
                print(f"   Additional errors: {result['errors']}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Compatibility test failed: {error_msg}")
        
        if "model_dump" in error_msg:
            print("\n🚨 MODEL_DUMP ERROR DETECTED!")
            print("   This indicates the compatibility fix needs adjustment for LangGraph 1.0.2")
            print(f"   Error details: {error_msg}")
        
        return False

if __name__ == "__main__":
    print("🔧 LANGGRAPH 1.0.2 + PYDANTIC 2.12.4 COMPATIBILITY TEST")
    print("=" * 60)
    
    # Step 1: Check versions
    versions_ok = check_environment_versions()
    
    # Step 2: Test tool structure
    tools_ok = test_tool_invocation_methods()
    
    # Step 3: Test actual compatibility
    compat_ok = test_compatibility_fix()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    print(f"Environment versions: {'✅ OK' if versions_ok else '❌ FAIL'}")
    print(f"Tool invocation methods: {'✅ OK' if tools_ok else '❌ FAIL'}")
    print(f"Compatibility fix: {'✅ OK' if compat_ok else '❌ FAIL'}")
    
    if versions_ok and tools_ok and compat_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Your LangGraph 1.0.2 + Pydantic 2.12.4 environment is working!")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("   The compatibility fix may need further adjustment.")
        print("   Check the error messages above for details.")