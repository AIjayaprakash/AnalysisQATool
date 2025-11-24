"""
Test logger integration with API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoint_with_logging():
    """Test that health endpoint logs correctly"""
    print("=" * 80)
    print("Testing Health Endpoint with Logging")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Health check successful")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n📝 Check logs/$(date +%Y-%m-%d)_app.log for:")
            print("   - Health check requested")
            print("   - Health check completed")
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start it with:")
        print("   python backend/app/llmops_api.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_root_endpoint_with_logging():
    """Test that root endpoint logs correctly"""
    print("\n" + "=" * 80)
    print("Testing Root Endpoint with Logging")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Root endpoint successful")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n📝 Check logs for:")
            print("   - Root endpoint accessed")
        else:
            print(f"❌ Request failed with status: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_generate_prompt_with_logging():
    """Test that generate-prompt endpoint logs correctly"""
    print("\n" + "=" * 80)
    print("Testing Generate Prompt Endpoint with Logging")
    print("=" * 80)
    
    test_case = {
        "test_id": "TC_LOG_001",
        "module": "Login",
        "functionality": "User Login",
        "description": "Test user login functionality",
        "steps": "1. Navigate to login page\\n2. Enter credentials\\n3. Click login",
        "expected_result": "User should be logged in successfully",
        "priority": "High"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-prompt",
            json=test_case,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prompt generation successful")
            print(f"Test ID: {result['test_id']}")
            print(f"Prompt length: {len(result.get('generated_prompt', ''))}")
            print("\n📝 Check logs for:")
            print("   - Generating prompt for test case: TC_LOG_001")
            print("   - Calling LLM to generate prompt")
            print("   - Prompt generated successfully")
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def view_log_tail():
    """Show instructions to view logs"""
    print("\n" + "=" * 80)
    print("View Logs")
    print("=" * 80)
    
    import os
    from datetime import datetime
    from pathlib import Path
    
    log_dir = Path("logs")
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}_app.log"
    
    if log_file.exists():
        print(f"✅ Log file exists: {log_file}")
        print(f"\nTo view logs, run:")
        print(f"   tail -20 {log_file}")
        print(f"\nOr on Windows:")
        print(f"   Get-Content {log_file} -Tail 20")
        
        # Show last few lines
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-10:] if len(lines) >= 10 else lines
                
                print(f"\n📋 Last {len(last_lines)} log entries:")
                print("-" * 80)
                for line in last_lines:
                    print(line.rstrip())
        except Exception as e:
            print(f"⚠️  Could not read log file: {e}")
    else:
        print(f"⚠️  Log file not found: {log_file}")
        print("   Logs will be created when the API server starts")


if __name__ == "__main__":
    print("\n🔍 Logger Integration Test\n")
    
    # Test endpoints
    test_root_endpoint_with_logging()
    test_health_endpoint_with_logging()
    
    # Uncomment to test prompt generation (requires API keys)
    # test_generate_prompt_with_logging()
    
    # View logs
    view_log_tail()
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("   1. Start the server: python backend/app/llmops_api.py")
    print("   2. Run this test: python backend/app/test_logger_integration.py")
    print("   3. Check logs directory for log files")
    print("   4. Logs are color-coded in console, detailed in files")
