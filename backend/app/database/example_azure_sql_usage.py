"""
Example Usage of Azure SQL Manager.

Run this script to see examples of how to use the Azure SQL Manager.
"""

import os
from dotenv import load_dotenv
from azure_sql_manager import AzureSQLManager, create_config_from_env

# Load environment variables
load_dotenv()


def example_1_basic_connection():
    """Example 1: Test database connection."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Connection Test")
    print("=" * 70)
    
    try:
        config = create_config_from_env()
        db = AzureSQLManager(config)
        
        if db.connect():
            print(f"✅ Connected to: {config.database}")
            db.close()
            return True
        else:
            print("❌ Connection failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_2_store_metadata():
    """Example 2: Store test metadata."""
    print("\n" + "=" * 70)
    print("Example 2: Store Test Metadata")
    print("=" * 70)
    
    metadata = {
        "test_id": "TC_EXAMPLE_001",
        "status": "success",
        "execution_time": 5.2,
        "steps_executed": 10,
        "agent_output": "Test completed successfully",
        "screenshots": ["screenshot1.png"],
        "pages": [
            {
                "id": "page_1",
                "label": "Login Page",
                "x": 100,
                "y": 150,
                "metadata": {
                    "key_elements": [
                        {
                            "type": "button",
                            "label": "Login Button",
                            "selector": "#login-btn"
                        }
                    ]
                }
            }
        ],
        "edges": []
    }
    
    try:
        config = create_config_from_env()
        with AzureSQLManager(config) as db:
            execution_id = db.store_playwright_metadata(metadata)
            
            if execution_id:
                print(f"✅ Stored with execution_id: {execution_id}")
                return execution_id
            else:
                print("❌ Storage failed")
                return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Azure SQL Manager - Examples")
    print("=" * 70)
    
    # Check environment
    required_vars = ["AZURE_SQL_SERVER", "AZURE_SQL_DATABASE", 
                     "AZURE_SQL_USERNAME", "AZURE_SQL_PASSWORD"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("Please set them in your .env file")
        return
    
    # Run examples
    if example_1_basic_connection():
        example_2_store_metadata()


if __name__ == "__main__":
    run_all_examples()
