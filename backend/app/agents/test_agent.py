"""
Test script to demonstrate the Selenium LangGraph agent.
"""

import asyncio
import os
from selenium_agent import run_selenium_automation

async def main():
    # Set your OpenAI API key
    os.environ["OPENAI_API_KEY"] = "your-key-here"
    
    # Example automation tasks
    tasks = [
        "Open Chrome and navigate to https://example.com",
        "Go to Google, search for 'selenium automation', and click the first result",
        "Visit https://github.com/login, enter username 'test' in the login field, and click Sign in"
    ]
    
    for task in tasks:
        print(f"\nExecuting task: {task}")
        print("-" * 50)
        
        result = await run_selenium_automation(task)
        
        print("Status:", result["status"])
        if result["error"]:
            print("Error:", result["error"])
        
        print("\nExecution log:")
        for msg in result["messages"]:
            print(f"- {msg}")
        
        print("-" * 50)
        
if __name__ == "__main__":
    asyncio.run(main())