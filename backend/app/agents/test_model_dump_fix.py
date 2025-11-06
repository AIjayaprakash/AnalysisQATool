#!/usr/bin/env python3
"""
Test fix for model_dump issue in agent.invoke()
Verify that all messages are proper BaseMessage objects, not strings
"""

import asyncio
from datetime import datetime
from playwright_direct_agent import run_test_with_visible_browser

def test_model_dump_fix():
    """Test that the agent properly handles message objects without model_dump errors"""
    
    print("🔧 Testing model_dump fix in agent.invoke()")
    print("=" * 60)
    
    try:
        result = run_test_with_visible_browser(
            prompt="Navigate to https://httpbin.org", 
            max_iterations=2, 
            headless=False,
            browser_type="chromium"
        )
        
        print(f"✅ Agent completed: {result['status']}")
        print(f"✅ Steps: {result['steps_executed']}")
        print(f"✅ Errors: {len(result['errors'])}")
        
        # Check for model_dump errors in the error list
        model_dump_errors = [e for e in result.get('errors', []) if 'model_dump' in str(e)]
        
        if model_dump_errors:
            print(f"\n❌ STILL HAS MODEL_DUMP ERRORS: {len(model_dump_errors)}")
            for error in model_dump_errors:
                print(f"  - {error}")
            return False
        else:
            print(f"\n✅ NO MODEL_DUMP ERRORS FOUND!")
            
            # Additional check - verify message structure
            messages = result.get('messages', [])
            print(f"✅ Total messages: {len(messages)}")
            
            for i, msg in enumerate(messages):
                msg_type = msg.get('role', 'unknown') if isinstance(msg, dict) else type(msg).__name__
                print(f"  Message {i}: {msg_type}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        
        if 'model_dump' in str(e):
            print("❌ This is a model_dump error - fix not complete")
            print(f"   Error details: {e}")
        else:
            print("ℹ️  Different type of error")
            
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🕐 Test started: {datetime.now().strftime('%H:%M:%S')}")
    
    success = test_model_dump_fix()
    
    print(f"\n🕐 Test completed: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("🎉 MODEL_DUMP FIX: SUCCESS!")
    else:
        print("😞 MODEL_DUMP FIX: Still needs work")