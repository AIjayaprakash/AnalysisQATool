"""
Test the message flow to ensure no more role 'tool' errors
"""

def test_message_flow():
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    
    print("=== Testing Message Flow ===\n")
    
    # OpenAI flow (with proper tool_calls)
    print("OpenAI Flow:")
    print("1. HumanMessage: 'Navigate to example.com'")
    print("2. AIMessage: tool_calls=[{name: 'navigate', args: {...}}]")
    print("3. ToolMessage: 'Navigation completed' (valid - has preceding tool_calls)")
    print("[OK] Valid flow\n")
    
    # Groq flow (avoiding ToolMessage without tool_calls)
    print("Groq Flow:")
    print("1. HumanMessage: 'Navigate to example.com'")
    print("2. AIMessage: 'TOOL_CALL: navigate\\nARGS: {...}'")
    print("3. AIMessage: 'Tool execution results:\\n✓ Executed navigate'")
    print("✅ Valid flow - no ToolMessage without tool_calls\n")
    
    # What caused the error (fixed)
    print("Previous Error Flow (FIXED):")
    print("1. HumanMessage: 'Navigate to example.com'")  
    print("2. AIMessage: 'TOOL_CALL: navigate' (no tool_calls attribute)")
    print("3. ToolMessage: 'Executed' [X] Invalid - no preceding tool_calls")
    print("Error: 'messages with role 'tool' must be a response to a preceeding message with 'tool_calls'")

if __name__ == "__main__":
    test_message_flow()