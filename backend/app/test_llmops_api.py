"""
Test script for LLMOps API
Tests all endpoints with sample data
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)

def test_health():
    """Test health endpoint"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Health check passed")

def test_config():
    """Test configuration endpoint"""
    print_section("TEST 2: Get Configuration")
    
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Configuration retrieval passed")

def test_single_prompt():
    """Test single prompt generation"""
    print_section("TEST 3: Generate Single Prompt")
    
    test_case = {
        "test_id": "TC001",
        "module": "Login",
        "functionality": "User Authentication",
        "description": "Verify user can login with valid credentials",
        "steps": "1. Navigate to login page\n2. Enter username\n3. Enter password\n4. Click login",
        "expected_result": "User should be logged in successfully",
        "priority": "High"
    }
    
    response = requests.post(f"{BASE_URL}/generate-prompt", json=test_case)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Test ID: {result['test_id']}")
        print(f"Module: {result['module']}")
        print(f"Generated Prompt Preview: {result['generated_prompt'][:200]}...")
        print("✓ Single prompt generation passed")
    else:
        print(f"Error: {response.text}")

def test_batch_prompts():
    """Test batch prompt generation"""
    print_section("TEST 4: Generate Batch Prompts")
    
    test_cases = {
        "test_cases": [
            {
                "test_id": "TC001",
                "module": "Login",
                "functionality": "User Authentication",
                "description": "Verify user can login with valid credentials",
                "priority": "High"
            },
            {
                "test_id": "TC002",
                "module": "Login",
                "functionality": "Invalid Login",
                "description": "Verify system shows error for invalid credentials",
                "priority": "High"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/generate-prompts-batch", json=test_cases)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Prompts Generated: {result['total']}")
        for i, prompt in enumerate(result['prompts'], 1):
            print(f"\n[{i}] {prompt['test_id']}: {prompt['module']}")
            print(f"    Prompt Preview: {prompt['generated_prompt'][:150]}...")
        print("\n✓ Batch prompt generation passed")
    else:
        print(f"Error: {response.text}")

def test_upload_excel():
    """Test Excel upload and processing"""
    print_section("TEST 5: Upload Excel File")
    
    # Check if sample Excel exists
    excel_path = Path("test_cases.xlsx")
    
    if not excel_path.exists():
        print("⚠ test_cases.xlsx not found. Skipping Excel upload test.")
        print("  Create a test_cases.xlsx file to test this endpoint.")
        return
    
    with open(excel_path, 'rb') as f:
        files = {'file': ('test_cases.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(f"{BASE_URL}/upload-excel?sheet_name=Sheet1", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Filename: {result['filename']}")
        print(f"Sheet: {result['sheet_name']}")
        print(f"Total Test Cases: {result['total_test_cases']}")
        print("\n✓ Excel upload and processing passed")
    else:
        print(f"Error: {response.text}")

def test_providers():
    """Test list providers endpoint"""
    print_section("TEST 6: List Available Providers")
    
    response = requests.get(f"{BASE_URL}/providers")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Providers listing passed")

def test_root():
    """Test root endpoint"""
    print_section("TEST 7: Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Root endpoint passed")

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LLMOps API Test Suite")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")
    print("\nMake sure the API server is running:")
    print("  python llmops_api.py")
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print("\n✓ Server is running")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("Please start the server first:")
        print("  python llmops_api.py")
        return
    
    # Run tests
    try:
        test_root()
        test_health()
        test_config()
        test_providers()
        test_single_prompt()
        test_batch_prompts()
        test_upload_excel()
        
        print("\n" + "=" * 70)
        print("✅ All API Tests Completed!")
        print("=" * 70)
        print("\nAPI Documentation available at:")
        print(f"  {BASE_URL}/docs")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
