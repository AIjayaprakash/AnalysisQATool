#!/usr/bin/env python3
"""
Test the Custom OpenAI Gateway integration with LangGraph
This validates that your OpenAI setup works without model_dump errors
"""

import sys
import os

# Test the custom OpenAI client directly first
def test_custom_openai_client():
    """Test your custom OpenAI client configuration"""
    print("🔧 Testing Custom OpenAI Client Configuration")
    print("=" * 50)
    
    # Your exact configuration
    from openai import OpenAI
    
    key = "Your Key Here"  # You need to replace this with your actual key
    model = "gpt-4o"
    gateway_url = f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
    
    if key == "Your Key Here":
        print("❌ Please replace 'Your Key Here' with your actual API key")
        return False
    
    print(f"Model: {model}")
    print(f"Gateway URL: {gateway_url}")
    print(f"API Key: {'*' * (len(key) - 4) + key[-4:] if len(key) > 4 else '****'}")
    
    try:
        client = OpenAI(
            api_key=key,
            base_url=gateway_url,
        )
        
        # Test a simple completion
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from custom OpenAI gateway!' in exactly those words.",
                },
            ],
            model=model,
            extra_headers={"api-key": key, "ai-gateway-version": "v2"},
        )
        
        response = chat_completion.choices[0].message.content
        print(f"✅ OpenAI Response: {response}")
        
        if "Hello from custom OpenAI gateway!" in response:
            print("✅ Custom OpenAI client is working correctly!")
            return True
        else:
            print("⚠️ Custom OpenAI client responded but with unexpected content")
            return True  # Still working, just different response
            
    except Exception as e:
        print(f"❌ Custom OpenAI client failed: {e}")
        
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("   This appears to be an authentication error - check your API key")
        elif "404" in str(e) or "not found" in str(e).lower():
            print("   This appears to be a URL/deployment error - check the gateway URL")
        else:
            print("   This is a different error - check your configuration")
        
        return False

def test_langgraph_integration():
    """Test LangGraph integration with custom OpenAI"""
    print("\n🔧 Testing LangGraph Integration")
    print("=" * 50)
    
    try:
        from playwright_custom_openai_agent import CustomOpenAIClient, AgentState
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        # Test the custom client wrapper
        key = "Your Key Here"  # Replace with actual key
        if key == "Your Key Here":
            print("❌ Please set your actual API key for this test")
            return False
        
        # Create custom client
        custom_client = CustomOpenAIClient(
            api_key=key,
            model="gpt-4o"
        )
        
        # Test with LangChain messages
        test_messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Say 'LangGraph integration working!' exactly.")
        ]
        
        response = custom_client.invoke(test_messages)
        print(f"✅ LangGraph Integration Response: {response}")
        
        if isinstance(response, str):
            print("✅ Response is string type (good for model_dump fix)")
            return True
        else:
            print(f"⚠️ Response is {type(response)} - may need adjustment")
            return False
            
    except Exception as e:
        print(f"❌ LangGraph integration test failed: {e}")
        
        if 'model_dump' in str(e):
            print("   This is a model_dump error - the fix needs adjustment")
        
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 CUSTOM OPENAI + LANGGRAPH INTEGRATION TESTS")
    print("=" * 60)
    print("Testing your custom OpenAI gateway configuration with LangGraph")
    print()
    
    # Test 1: Basic OpenAI client
    client_works = test_custom_openai_client()
    
    if not client_works:
        print("\n❌ Basic OpenAI client test failed - fix configuration before proceeding")
        return False
    
    # Test 2: LangGraph integration
    integration_works = test_langgraph_integration()
    
    if not integration_works:
        print("\n❌ LangGraph integration test failed")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Your custom OpenAI gateway configuration is working")
    print("✅ LangGraph integration is working")
    print("✅ Ready for Playwright automation")
    print()
    print("Next steps:")
    print("1. Update your API key in the configuration")
    print("2. Run: python example_custom_openai.py")
    print("3. Watch your browser automate with visible Playwright!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)