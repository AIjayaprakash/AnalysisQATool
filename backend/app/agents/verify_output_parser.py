#!/usr/bin/env python3
"""
Verify the OUTPUT PARSER approach is working correctly
"""

from playwright_direct_agent import run_test_with_visible_browser

def test_simple_navigation():
    print("Testing simple navigation with OUTPUT PARSER approach...")
    
    result = run_test_with_visible_browser(
        prompt="Navigate to https://httpbin.org/forms/post and take a screenshot", 
        max_iterations=3, 
        headless=False
    )
    
    print("=== RESULTS ===")
    print(f"Status: {result['status']}")
    print(f"Steps: {result['steps_executed']}")
    print(f"Messages: {len(result['messages'])}")
    print(f"Errors: {len(result['errors'])}")
    
    print("\n=== MESSAGE SUMMARY ===")
    for i, msg in enumerate(result['messages']):
        msg_type = type(msg).__name__
        content = str(msg.content)[:300] + "..." if len(str(msg.content)) > 300 else str(msg.content)
        print(f"Message {i} ({msg_type}): {content}")
        print("-" * 50)
    
    # Check for model_dump errors
    all_content = ' '.join([str(msg.content) for msg in result['messages']])
    if 'model_dump' in all_content.lower():
        print("❌ FOUND model_dump references in messages!")
        return False
    else:
        print("✅ NO model_dump errors found!")
        return True

if __name__ == "__main__":
    success = test_simple_navigation()
    print(f"\n🎯 OUTPUT PARSER SUCCESS: {success}")
