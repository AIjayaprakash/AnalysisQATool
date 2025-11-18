"""
Test Playwright API with Metadata Extraction

This script demonstrates the new metadata extraction feature that returns
structured page and element metadata in the specified JSON format.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_metadata_extraction():
    """Test metadata extraction from Playwright automation"""
    
    print("=" * 80)
    print("Testing Playwright API with Metadata Extraction")
    print("=" * 80)
    
    # Test case that will navigate and extract metadata
    test_case = {
        "test_id": "TC_METADATA_001",
        "module": "Web Navigation",
        "functionality": "Page Metadata Extraction",
        "description": "Navigate to example.com and extract all page and element metadata",
        "steps": """
            1. Navigate to https://example.com
            2. Extract page metadata (URL and title)
            3. Extract metadata for all key elements (links, buttons, etc.)
            4. Take screenshot for documentation
        """,
        "expected_result": "Complete metadata extracted in structured JSON format",
        "priority": "High"
    }
    
    print("\n📤 Sending request to /execute-playwright-from-testcase...")
    print(f"Test ID: {test_case['test_id']}")
    print(f"Target URL: https://example.com")
    
    try:
        response = requests.post(
            f"{BASE_URL}/execute-playwright-from-testcase",
            json=test_case,
            timeout=120  # 2 minute timeout for execution
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n" + "=" * 80)
        print("📊 Execution Results")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Execution Time: {result['execution_time']}s")
        print(f"Steps Executed: {result['steps_executed']}")
        
        if result.get('screenshots'):
            print(f"Screenshots: {', '.join(result['screenshots'])}")
        
        # Display extracted metadata
        if result.get('pages'):
            print("\n" + "=" * 80)
            print("🗂️  Extracted Metadata")
            print("=" * 80)
            
            for page in result['pages']:
                print(f"\n📄 {page['label']}")
                print(f"   ID: {page['id']}")
                print(f"   Position: ({page['x']}, {page['y']})")
                print(f"   URL: {page['metadata']['url']}")
                print(f"   Title: {page['metadata']['title']}")
                print(f"   Key Elements: {len(page['metadata']['key_elements'])}")
                
                if page['metadata']['key_elements']:
                    print("\n   Elements:")
                    for elem in page['metadata']['key_elements']:
                        print(f"   • {elem['id']}: {elem['type']} ({elem['tag']})")
                        if elem.get('text'):
                            print(f"     Text: {elem['text'][:50]}...")
                        if elem.get('href'):
                            print(f"     Href: {elem['href']}")
                        if elem.get('element_id'):
                            print(f"     HTML ID: {elem['element_id']}")
                        if elem.get('class_name'):
                            print(f"     Class: {elem['class_name']}")
        
        # Save full response to file for inspection
        output_file = "playwright_metadata_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full response saved to: {output_file}")
        
        # Display formatted JSON structure
        print("\n" + "=" * 80)
        print("📋 Sample Page Metadata Structure")
        print("=" * 80)
        
        if result.get('pages'):
            # Show first page in pretty format
            sample_page = result['pages'][0]
            print(json.dumps(sample_page, indent=2))
        
        print("\n" + "=" * 80)
        print("✅ Test Completed Successfully!")
        print("=" * 80)
        
        return result
        
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out. The automation may be taking longer than expected.")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    return None


def test_with_custom_prompt():
    """Test with custom prompt that explicitly requests metadata extraction"""
    
    print("\n\n" + "=" * 80)
    print("Testing with Custom Prompt (Two-Step Workflow)")
    print("=" * 80)
    
    # Step 1: Generate prompt
    test_case = {
        "test_id": "TC_CUSTOM_001",
        "module": "Login Page",
        "functionality": "Login Form Analysis",
        "description": "Analyze login form and extract all input field metadata",
        "steps": """
            1. Navigate to https://example.com
            2. Extract page metadata
            3. Find and extract metadata for all form inputs
            4. Document button elements
        """
    }
    
    print("\n📝 Step 1: Generating prompt...")
    try:
        prompt_response = requests.post(
            f"{BASE_URL}/generate-prompt",
            json=test_case
        )
        prompt_response.raise_for_status()
        generated_prompt = prompt_response.json()["generated_prompt"]
        
        print("✅ Prompt generated")
        print(f"Preview: {generated_prompt[:200]}...")
        
        # Step 2: Execute with explicit metadata instruction
        print("\n🤖 Step 2: Executing automation with metadata extraction...")
        
        # Add metadata extraction instruction to the prompt
        enhanced_prompt = f"""{generated_prompt}

IMPORTANT: Use playwright_get_page_metadata tool extensively:
1. After navigation, extract page metadata (URL, title)
2. Before any interaction, extract element metadata
3. Use selector=null for page metadata
4. Use specific selectors for elements (a, button, input, form)
"""
        
        exec_response = requests.post(
            f"{BASE_URL}/execute-playwright",
            json={
                "test_id": test_case["test_id"],
                "generated_prompt": enhanced_prompt,
                "browser_type": "chromium",
                "headless": False,
                "max_iterations": 15
            },
            timeout=120
        )
        
        exec_response.raise_for_status()
        result = exec_response.json()
        
        print(f"\n✅ Status: {result['status']}")
        print(f"⏱️  Time: {result['execution_time']}s")
        print(f"📊 Steps: {result['steps_executed']}")
        print(f"🗂️  Pages with Metadata: {len(result.get('pages', []))}")
        
        if result.get('pages'):
            total_elements = sum(len(p['metadata']['key_elements']) for p in result['pages'])
            print(f"📦 Total Elements Extracted: {total_elements}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def display_metadata_schema():
    """Display the expected metadata schema"""
    
    print("\n\n" + "=" * 80)
    print("📐 Expected Metadata Schema")
    print("=" * 80)
    
    schema = {
        "id": "page_1",
        "label": "Example Domain (example.com)",
        "x": 200,
        "y": 100,
        "metadata": {
            "url": "https://example.com/",
            "title": "Example Domain",
            "key_elements": [
                {
                    "id": "element_1",
                    "type": "link",
                    "tag": "a",
                    "text": "More information...",
                    "element_id": None,
                    "name": None,
                    "class_name": None,
                    "href": "https://www.iana.org/domains/example",
                    "input_type": None,
                    "depends_on": []
                }
            ]
        }
    }
    
    print(json.dumps(schema, indent=2))
    print("\n✅ This is the structure returned in the 'pages' array")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎭 Playwright Metadata Extraction Test Suite")
    print("=" * 80)
    
    # Check API health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("⚠️  API health check returned unexpected status")
            exit(1)
    except Exception as e:
        print("❌ API is not running. Please start it first:")
        print("   python backend/app/llmops_api.py")
        exit(1)
    
    # Display expected schema
    display_metadata_schema()
    
    # Run tests
    print("\n" + "=" * 80)
    print("Running Tests...")
    print("=" * 80)
    
    # Test 1: End-to-end with metadata
    result1 = test_metadata_extraction()
    
    # Test 2: Custom prompt with explicit metadata request
    result2 = test_with_custom_prompt()
    
    # Summary
    print("\n\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    if result1:
        print(f"✅ Test 1: Completed - {len(result1.get('pages', []))} pages extracted")
    else:
        print("❌ Test 1: Failed")
    
    if result2:
        print(f"✅ Test 2: Completed - {len(result2.get('pages', []))} pages extracted")
    else:
        print("❌ Test 2: Failed")
    
    print("\n" + "=" * 80)
    print("🎉 Testing Complete!")
    print("=" * 80)
    print("\n💡 Tip: Check 'playwright_metadata_output.json' for full details")
