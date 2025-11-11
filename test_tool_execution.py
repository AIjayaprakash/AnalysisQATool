"""
Test the tool execution fix
"""

import asyncio
from backend.app.agents.playwright_custom_openai_agent import playwright_tools

async def test_tool_execution():
    """Test that we can call tools correctly"""
    print("🧪 Testing tool execution fix...")
    
    # Test calling a tool directly
    for tool in playwright_tools:
        if tool.name == "playwright_navigate":
            print(f"Found tool: {tool.name}")
            print(f"Tool type: {type(tool)}")
            print(f"Tool attributes: {dir(tool)}")
            
            # Test calling with ainvoke
            try:
                result = await tool.ainvoke({"url": "https://example.com"})
                print(f"✅ Tool call successful: {result}")
                return True
            except Exception as e:
                print(f"❌ Tool call failed: {e}")
                return False
    
    print("❌ Tool not found")
    return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_execution())
    print(f"Test result: {'PASSED' if success else 'FAILED'}")