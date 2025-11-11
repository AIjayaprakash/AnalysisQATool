"""
Test the USE_TOOL pattern matching and execution
"""

import asyncio
import re
import json
from backend.app.agents.playwright_custom_openai_agent import playwright_tools

async def test_tool_pattern_matching():
    """Test that our tool pattern matching works correctly"""
    
    print("🧪 Testing USE_TOOL Pattern Matching and Execution")
    print("=" * 55)
    
    # Test content that mimics what the LLM would generate
    test_content = """I'll help you navigate to the website and take a screenshot.

USE_TOOL: playwright_navigate
ARGS: {"url": "https://httpbin.org"}

Now let me take a screenshot to document this step:

USE_TOOL: playwright_screenshot  
ARGS: {"filename": "httpbin_page.png"}

The navigation and screenshot have been completed successfully."""
    
    print("📝 Test content:")
    print(test_content)
    print("\n🔍 Parsing USE_TOOL patterns...")
    
    # Parse USE_TOOL format (same as in the agent)
    tool_pattern = r'USE_TOOL:\s*([^\n]+)\s*\nARGS:\s*(\{[^}]*\})'
    tool_matches = re.findall(tool_pattern, test_content, re.MULTILINE | re.DOTALL)
    
    print(f"Found {len(tool_matches)} tool calls:")
    
    for i, (tool_name, args_str) in enumerate(tool_matches, 1):
        tool_name = tool_name.strip()
        print(f"  {i}. Tool: {tool_name}")
        print(f"     Args: {args_str}")
        
        try:
            args = json.loads(args_str) if args_str.strip() else {}
            print(f"     Parsed args: {args}")
            
            # Find the tool
            tool_func = None
            for tool in playwright_tools:
                if tool.name == tool_name:
                    tool_func = tool
                    break
            
            if tool_func:
                try:
                    print(f"     🔧 Executing tool...")
                    result = await tool_func.ainvoke(args)
                    print(f"     ✅ Result: {result}")
                except Exception as e:
                    print(f"     ❌ Execution error: {e}")
            else:
                print(f"     ❌ Tool not found")
                
        except json.JSONDecodeError as e:
            print(f"     ❌ JSON parse error: {e}")
        
        print()
    
    return len(tool_matches) > 0

if __name__ == "__main__":
    success = asyncio.run(test_tool_pattern_matching())
    print(f"🎯 Pattern matching test: {'PASSED' if success else 'FAILED'}")