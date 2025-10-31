"""
Simple test runner for the Playwright LangGraph Agent
Run automation tests using natural language prompts
"""

import asyncio
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright_langgraph_agent import run_automation_test

async def main():
    print("=" * 70)
    print("Playwright LangGraph Automation Agent")
    print("=" * 70)
    
    # Example test scenarios
    test_scenarios = {
        "1": {
            "name": "Simple Navigation Test",
            "prompt": "Navigate to https://example.com, wait for the page to load, take a screenshot named 'example.png', and capture the page snapshot"
        },
        "2": {
            "name": "Form Fill Test",
            "prompt": "Go to https://acme-test.uipath.com/login, fill the email field with 'test@example.com', fill the password field with 'password123', but don't click submit"
        },
        "3": {
            "name": "Search Test",
            "prompt": "Navigate to https://www.google.com, find the search box, type 'Playwright automation testing', press Enter, and wait for results to load"
        },
        "4": {
            "name": "Multi-Step Test",
            "prompt": "Open https://github.com, click on the Sign in button, take a screenshot of the login page, then navigate back to the homepage"
        },
        "5": {
            "name": "Custom Test",
            "prompt": None  # User will enter their own prompt
        }
    }
    
    print("\nAvailable Test Scenarios:")
    for key, scenario in test_scenarios.items():
        print(f"{key}. {scenario['name']}")
    
    print("\n" + "=" * 70)
    choice = input("Select a test scenario (1-5) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("Goodbye!")
        return
    
    if choice not in test_scenarios:
        print("Invalid choice!")
        return
    
    scenario = test_scenarios[choice]
    
    if scenario["prompt"] is None:
        print("\nEnter your custom test prompt:")
        prompt = input("> ").strip()
        if not prompt:
            print("Empty prompt! Exiting.")
            return
    else:
        prompt = scenario["prompt"]
    
    print(f"\n{'='*70}")
    print(f"Running Test: {scenario['name']}")
    print(f"{'='*70}")
    print(f"Prompt: {prompt}")
    print(f"{'='*70}\n")
    
    # Run the test
    result = await run_automation_test(prompt)
    
    # Display results
    print(f"\n{'='*70}")
    print("Test Results")
    print(f"{'='*70}")
    print(f"Status: {result['status']}")
    print(f"Steps Executed: {result.get('steps_executed', 0)}")
    
    if result['status'] == 'error':
        print(f"\nError: {result.get('error')}")
    else:
        print(f"\nTest completed successfully!")
        if result.get('results'):
            print(f"\nExecution Details:")
            for i, step_result in enumerate(result['results'], 1):
                print(f"  Step {i}: {step_result['tool_calls']} tool(s) called at {step_result['timestamp']}")
    
    if result.get('errors'):
        print(f"\nErrors encountered:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)