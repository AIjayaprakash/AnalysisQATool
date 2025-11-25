"""
Example: Using the /execute-from-excel endpoint
Complete end-to-end automation from Excel file
"""

import requests
import json
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/execute-from-excel"

def example_1_basic_usage():
    """
    Example 1: Basic usage - Execute first test case with default settings
    """
    print("=" * 70)
    print("Example 1: Basic Usage (First Test Case, Chromium Browser)")
    print("=" * 70)
    
    # Path to your Excel file
    excel_file_path = "test_cases.xlsx"
    
    # Open and upload the file
    with open(excel_file_path, "rb") as f:
        files = {
            "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        
        # Make the request
        response = requests.post(API_URL, files=files)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"📄 Pages extracted: {len(result['pages'])}")
        print(f"🔗 Edges extracted: {len(result['edges'])}")
        
        # Print page details
        for page in result['pages']:
            print(f"\n  Page: {page['label']}")
            print(f"  URL: {page['metadata']['url']}")
            print(f"  Elements: {len(page['metadata']['key_elements'])}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def example_2_specific_test_case():
    """
    Example 2: Execute specific test case by ID with Edge browser
    """
    print("\n" + "=" * 70)
    print("Example 2: Specific Test Case with Edge Browser")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    
    with open(excel_file_path, "rb") as f:
        files = {
            "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        
        data = {
            "sheet_name": "Sheet1",
            "test_id": "TC_LOGIN_001",  # Specific test case ID
            "browser_type": "edge",      # Use Edge browser
            "headless": False,           # Show browser window
            "max_iterations": 10         # Maximum automation steps
        }
        
        response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"📄 Pages extracted: {len(result['pages'])}")
        print(f"🔗 Edges extracted: {len(result['edges'])}")
        
        # Print detailed page information
        for i, page in enumerate(result['pages'], 1):
            print(f"\n  Page {i}: {page['label']}")
            print(f"  ID: {page['id']}")
            print(f"  URL: {page['metadata']['url']}")
            print(f"  Title: {page['metadata']['title']}")
            print(f"  Elements found: {len(page['metadata']['key_elements'])}")
            
            # Print key elements
            for elem in page['metadata']['key_elements'][:3]:  # First 3 elements
                print(f"    - {elem['type']}: {elem['text'] or elem['tag']}")
        
        # Print edges
        if result['edges']:
            print(f"\n  Navigation Flow:")
            for edge in result['edges']:
                print(f"    {edge['source']} → {edge['target']}: {edge['label']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def example_3_firefox_headless():
    """
    Example 3: Firefox browser in headless mode
    """
    print("\n" + "=" * 70)
    print("Example 3: Firefox Headless Mode")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    
    with open(excel_file_path, "rb") as f:
        files = {
            "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        
        data = {
            "sheet_name": "Sheet1",
            "test_id": "TC_SEARCH_001",
            "browser_type": "firefox",   # Firefox browser
            "headless": True,            # Headless mode (no window)
            "max_iterations": 15
        }
        
        response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"📄 Pages: {len(result['pages'])}")
        print(f"🔗 Edges: {len(result['edges'])}")
        
        # Save results to JSON file
        output_file = "automation_results.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 Results saved to: {output_file}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def example_4_all_browsers():
    """
    Example 4: Test with all supported browsers
    """
    print("\n" + "=" * 70)
    print("Example 4: Test with All Browsers")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    browsers = ["chromium", "firefox", "webkit", "edge"]
    
    results_summary = {}
    
    for browser in browsers:
        print(f"\n🔍 Testing with {browser.upper()} browser...")
        
        with open(excel_file_path, "rb") as f:
            files = {
                "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }
            
            data = {
                "sheet_name": "Sheet1",
                "browser_type": browser,
                "headless": True,
                "max_iterations": 10
            }
            
            response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            results_summary[browser] = {
                "status": "✅ Success",
                "pages": len(result['pages']),
                "edges": len(result['edges'])
            }
            print(f"  ✅ {browser}: {len(result['pages'])} pages, {len(result['edges'])} edges")
        else:
            results_summary[browser] = {
                "status": f"❌ Failed ({response.status_code})",
                "error": response.text[:100]
            }
            print(f"  ❌ {browser}: Failed - {response.status_code}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Browser Test Summary:")
    print("=" * 70)
    for browser, result in results_summary.items():
        print(f"{browser.upper():10} - {result['status']}")
        if 'pages' in result:
            print(f"           Pages: {result['pages']}, Edges: {result['edges']}")


def example_5_detailed_extraction():
    """
    Example 5: Detailed metadata extraction and analysis
    """
    print("\n" + "=" * 70)
    print("Example 5: Detailed Metadata Extraction")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    
    with open(excel_file_path, "rb") as f:
        files = {
            "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        
        data = {
            "sheet_name": "Sheet1",
            "test_id": "TC_001",
            "browser_type": "edge",
            "headless": False,
            "max_iterations": 10
        }
        
        response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!\n")
        
        # Analyze pages
        print(f"📄 Total Pages Visited: {len(result['pages'])}\n")
        
        for page in result['pages']:
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Page ID: {page['id']}")
            print(f"Label: {page['label']}")
            print(f"URL: {page['metadata']['url']}")
            print(f"Title: {page['metadata']['title']}")
            print(f"Position: (x={page['x']}, y={page['y']})")
            print(f"\n🎯 Key Elements ({len(page['metadata']['key_elements'])}):")
            
            # Group elements by type
            element_types = {}
            for elem in page['metadata']['key_elements']:
                elem_type = elem['type']
                if elem_type not in element_types:
                    element_types[elem_type] = []
                element_types[elem_type].append(elem)
            
            # Print element summary
            for elem_type, elements in element_types.items():
                print(f"  {elem_type}: {len(elements)} element(s)")
            
            # Print detailed element info
            print(f"\n  Detailed Elements:")
            for elem in page['metadata']['key_elements']:
                print(f"    • {elem['id']} ({elem['type']})")
                print(f"      Tag: <{elem['tag']}>")
                if elem.get('text'):
                    print(f"      Text: {elem['text']}")
                if elem.get('href'):
                    print(f"      Href: {elem['href']}")
                if elem.get('element_id'):
                    print(f"      ID: {elem['element_id']}")
                if elem.get('class_name'):
                    print(f"      Class: {elem['class_name']}")
                print()
        
        # Analyze edges
        if result['edges']:
            print(f"\n🔗 Navigation Flow ({len(result['edges'])} transition(s)):\n")
            for i, edge in enumerate(result['edges'], 1):
                print(f"  {i}. {edge['source']} → {edge['target']}")
                print(f"     Action: {edge['label']}\n")
        
        # Statistics
        total_elements = sum(len(page['metadata']['key_elements']) for page in result['pages'])
        print(f"\n📊 Statistics:")
        print(f"  Total Pages: {len(result['pages'])}")
        print(f"  Total Elements: {total_elements}")
        print(f"  Total Edges: {len(result['edges'])}")
        print(f"  Avg Elements per Page: {total_elements / len(result['pages']) if result['pages'] else 0:.1f}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def example_6_error_handling():
    """
    Example 6: Proper error handling
    """
    print("\n" + "=" * 70)
    print("Example 6: Error Handling")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    
    try:
        # Check if file exists
        if not Path(excel_file_path).exists():
            print(f"❌ File not found: {excel_file_path}")
            return
        
        with open(excel_file_path, "rb") as f:
            files = {
                "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }
            
            data = {
                "sheet_name": "Sheet1",
                "test_id": "TC_INVALID_999",  # Invalid test ID
                "browser_type": "edge",
                "headless": False,
                "max_iterations": 10
            }
            
            response = requests.post(API_URL, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📄 Pages: {len(result['pages'])}")
            print(f"🔗 Edges: {len(result['edges'])}")
        elif response.status_code == 404:
            print(f"❌ Test case not found: {data['test_id']}")
            print(f"   Response: {response.json()}")
        elif response.status_code == 400:
            print(f"❌ Bad request")
            print(f"   Response: {response.json()}")
        elif response.status_code == 500:
            print(f"❌ Server error")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout - automation took too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
        print("   Start server with: python backend/app/llmops_api.py")
    except FileNotFoundError:
        print(f"❌ Excel file not found: {excel_file_path}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")


def example_7_save_to_file():
    """
    Example 7: Save results to different formats
    """
    print("\n" + "=" * 70)
    print("Example 7: Save Results to Files")
    print("=" * 70)
    
    excel_file_path = "test_cases.xlsx"
    
    with open(excel_file_path, "rb") as f:
        files = {
            "file": ("test_cases.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        
        data = {
            "sheet_name": "Sheet1",
            "browser_type": "edge",
            "headless": False,
            "max_iterations": 10
        }
        
        response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        
        # Save as JSON
        json_file = "automation_results.json"
        with open(json_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 JSON saved: {json_file}")
        
        # Save as formatted text
        txt_file = "automation_results.txt"
        with open(txt_file, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("Automation Results\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Total Pages: {len(result['pages'])}\n")
            f.write(f"Total Edges: {len(result['edges'])}\n\n")
            
            for page in result['pages']:
                f.write(f"\nPage: {page['label']}\n")
                f.write(f"URL: {page['metadata']['url']}\n")
                f.write(f"Elements: {len(page['metadata']['key_elements'])}\n")
                
                for elem in page['metadata']['key_elements']:
                    f.write(f"  - {elem['type']}: {elem.get('text', elem['tag'])}\n")
        
        print(f"💾 Text saved: {txt_file}")
        
        # Save pages as CSV
        import csv
        csv_file = "pages_summary.csv"
        with open(csv_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Page ID", "Label", "URL", "Title", "Element Count"])
            
            for page in result['pages']:
                writer.writerow([
                    page['id'],
                    page['label'],
                    page['metadata']['url'],
                    page['metadata']['title'],
                    len(page['metadata']['key_elements'])
                ])
        
        print(f"💾 CSV saved: {csv_file}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("\n")
    print("🎯" * 35)
    print("Execute From Excel - Comprehensive Examples")
    print("🎯" * 35)
    print("\nMake sure:")
    print("1. API server is running: python backend/app/llmops_api.py")
    print("2. Excel file exists: test_cases.xlsx")
    print("3. Browsers are installed: python -m playwright install")
    print("\n")
    
    # Run examples
    try:
        # Uncomment the examples you want to run:
        
        example_1_basic_usage()
        # example_2_specific_test_case()
        # example_3_firefox_headless()
        # example_4_all_browsers()
        # example_5_detailed_extraction()
        # example_6_error_handling()
        # example_7_save_to_file()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("1. Check if API server is running on http://localhost:8000")
        print("2. Verify Excel file path is correct")
        print("3. Ensure Playwright browsers are installed")
