"""
Example usage of Playwright Automation API endpoints

This script demonstrates how to:
1. Generate a Playwright prompt from a test case
2. Execute the automation using the generated prompt
3. Use the combined endpoint for end-to-end automation
"""

import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"


def generate_prompt(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1: Generate Playwright prompt from test case
    
    Args:
        test_case: Test case details
    
    Returns:
        Response with generated_prompt
    """
    url = f"{BASE_URL}/generate-prompt"
    
    response = requests.post(url, json=test_case)
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Prompt Generated for Test ID: {result['test_id']}")
    print(f"Generated Prompt Preview: {result['generated_prompt'][:200]}...")
    
    return result


def execute_playwright(test_id: str, generated_prompt: str, browser_type: str = "chromium") -> Dict[str, Any]:
    """
    Step 2: Execute Playwright automation with generated prompt
    
    Args:
        test_id: Test case ID
        generated_prompt: The prompt from generate_prompt()
        browser_type: Browser to use (chromium, firefox, webkit)
    
    Returns:
        Execution results
    """
    url = f"{BASE_URL}/execute-playwright"
    
    payload = {
        "test_id": test_id,
        "generated_prompt": generated_prompt,
        "browser_type": browser_type,
        "headless": False,  # Set to True for headless mode
        "max_iterations": 10
    }
    
    print(f"\n🤖 Executing Playwright automation for Test ID: {test_id}...")
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Execution Status: {result['status']}")
    print(f"⏱️  Execution Time: {result['execution_time']} seconds")
    print(f"📊 Steps Executed: {result['steps_executed']}")
    
    if result['screenshots']:
        print(f"📸 Screenshots: {', '.join(result['screenshots'])}")
    
    if result['error_message']:
        print(f"⚠️  Error: {result['error_message']}")
    
    return result


def execute_end_to_end(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combined: Generate prompt AND execute automation in one call
    
    Args:
        test_case: Test case details
    
    Returns:
        Execution results
    """
    url = f"{BASE_URL}/execute-playwright-from-testcase"
    
    print(f"\n🚀 Running end-to-end automation for Test ID: {test_case['test_id']}...")
    response = requests.post(url, json=test_case)
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Execution Status: {result['status']}")
    print(f"⏱️  Execution Time: {result['execution_time']} seconds")
    print(f"📊 Steps Executed: {result['steps_executed']}")
    
    return result


# Example Test Cases
def example_1_two_step_workflow():
    """Example 1: Two-step workflow (Generate -> Execute)"""
    print("=" * 80)
    print("Example 1: Two-Step Workflow (Generate Prompt -> Execute)")
    print("=" * 80)
    
    # Test case for login functionality
    test_case = {
        "test_id": "TC_001",
        "module": "Authentication",
        "functionality": "User Login",
        "description": "Verify user can login with valid credentials",
        "steps": "1. Navigate to login page\n2. Enter username\n3. Enter password\n4. Click login button",
        "expected_result": "User should be logged in and redirected to dashboard",
        "priority": "High"
    }
    
    # Step 1: Generate prompt
    prompt_result = generate_prompt(test_case)
    
    # Step 2: Execute automation
    execution_result = execute_playwright(
        test_id=prompt_result['test_id'],
        generated_prompt=prompt_result['generated_prompt'],
        browser_type="chromium"
    )
    
    print(f"\n📋 Final Result:")
    print(f"  Status: {execution_result['status']}")
    print(f"  Time: {execution_result['execution_time']}s")
    print(f"  Steps: {execution_result['steps_executed']}")


def example_2_single_step_workflow():
    """Example 2: Single-step workflow (Combined endpoint)"""
    print("\n" + "=" * 80)
    print("Example 2: Single-Step Workflow (Combined Endpoint)")
    print("=" * 80)
    
    # Test case for form submission
    test_case = {
        "test_id": "TC_002",
        "module": "Contact Form",
        "functionality": "Form Submission",
        "description": "Verify contact form can be submitted successfully",
        "steps": "1. Open contact page\n2. Fill name field\n3. Fill email field\n4. Fill message\n5. Submit form",
        "expected_result": "Success message should be displayed",
        "priority": "Medium"
    }
    
    # Execute end-to-end (generates prompt + runs automation)
    execution_result = execute_end_to_end(test_case)
    
    print(f"\n📋 Final Result:")
    print(f"  Status: {execution_result['status']}")
    print(f"  Time: {execution_result['execution_time']}s")
    print(f"  Steps: {execution_result['steps_executed']}")


def example_3_batch_automation():
    """Example 3: Batch automation for multiple test cases"""
    print("\n" + "=" * 80)
    print("Example 3: Batch Automation")
    print("=" * 80)
    
    test_cases = [
        {
            "test_id": "TC_003",
            "module": "Search",
            "functionality": "Product Search",
            "description": "Verify product search functionality",
            "steps": "1. Go to homepage\n2. Enter search term\n3. Click search\n4. Verify results",
            "expected_result": "Relevant products should be displayed"
        },
        {
            "test_id": "TC_004",
            "module": "Navigation",
            "functionality": "Menu Navigation",
            "description": "Verify main menu navigation",
            "steps": "1. Open website\n2. Click menu items\n3. Verify page loads",
            "expected_result": "All menu items should work correctly"
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            result = execute_end_to_end(test_case)
            results.append(result)
        except Exception as e:
            print(f"❌ Failed {test_case['test_id']}: {str(e)}")
    
    # Summary
    print(f"\n📊 Batch Execution Summary:")
    print(f"  Total Tests: {len(test_cases)}")
    print(f"  Executed: {len(results)}")
    print(f"  Success: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"  Failed: {sum(1 for r in results if r['status'] in ['failed', 'error'])}")


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy and ready")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the server first:")
        print("   python backend/app/llmops_api.py")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Playwright Automation API - Example Usage")
    print("=" * 80 + "\n")
    
    # Check if API is running
    if not check_api_health():
        exit(1)
    
    # Run examples
    try:
        # Example 1: Two-step workflow
        example_1_two_step_workflow()
        
        # Example 2: Single-step workflow
        example_2_single_step_workflow()
        
        # Example 3: Batch automation
        example_3_batch_automation()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {str(e)}")
        print("Make sure the API server is running and environment variables are set.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
