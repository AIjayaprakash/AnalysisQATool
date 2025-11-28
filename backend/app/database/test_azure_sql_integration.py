""""""

Test Script for Azure SQL IntegrationTest Script: Verify Azure SQL Integration



This script tests the Azure SQL database setup and verifies all componentsThis script tests the Azure SQL database connection and basic operations.

are working correctly.Run this script to verify your setup is working correctly.

"""

Run this script after:

1. Setting up Azure SQL Databaseimport sys

2. Deploying the schema (azure_sql_schema.sql)import json

3. Configuring environment variables in .envfrom pathlib import Path

from datetime import datetime

Author: Generated for SeleniumMCPFlow Project

Date: 2024# Add parent directory to path

"""sys.path.append(str(Path(__file__).parent.parent))



import osfrom database.azure_sql_manager import (

import sys    AzureSQLManager,

from datetime import datetime    AzureSQLConfig,

from dotenv import load_dotenv    create_config_from_env

)

# Load environment variables

load_dotenv()

def test_1_connection():

# Import the manager    """Test 1: Verify database connection"""

try:    print("\n" + "=" * 80)

    from azure_sql_manager import AzureSQLManager, create_sample_metadata    print("TEST 1: Verify Database Connection")

    print("✅ Successfully imported AzureSQLManager")    print("=" * 80)

except ImportError as e:    

    print(f"❌ Failed to import AzureSQLManager: {e}")    try:

    sys.exit(1)        # Try to load from environment variables

        try:

            config = create_config_from_env()

class TestResults:            print("✅ Loaded configuration from environment variables")

    """Track test results."""        except:

    def __init__(self):            # Fallback to manual config (update with your details)

        self.passed = 0            config = AzureSQLConfig(

        self.failed = 0                server="your-server.database.windows.net",

        self.tests = []                database="playwright-db",

                    username="sqladmin",

    def add_result(self, test_name: str, passed: bool, message: str = ""):                password="YourPassword"

        self.tests.append({            )

            'name': test_name,            print("⚠️  Using hardcoded configuration (update with your details)")

            'passed': passed,        

            'message': message        print(f"\nConnection Details:")

        })        print(f"  Server: {config.server}")

        if passed:        print(f"  Database: {config.database}")

            self.passed += 1        print(f"  Username: {config.username}")

        else:        

            self.failed += 1        print("\n🔌 Attempting connection...")

            

    def print_summary(self):        with AzureSQLManager(config) as db:

        print("\n" + "=" * 70)            cursor = db.connection.cursor()

        print("  TEST SUMMARY")            cursor.execute("SELECT @@VERSION, GETDATE()")

        print("=" * 70)            version, current_time = cursor.fetchone()

                    

        for test in self.tests:            print("\n✅ CONNECTION SUCCESSFUL!")

            status = "✅ PASS" if test['passed'] else "❌ FAIL"            print(f"\nServer Info:")

            print(f"{status}: {test['name']}")            print(f"  Version: {version[:100]}...")

            if test['message']:            print(f"  Server Time: {current_time}")

                print(f"      {test['message']}")        

                return True

        print("\n" + "-" * 70)    

        print(f"Total Tests: {self.passed + self.failed}")    except Exception as e:

        print(f"Passed: {self.passed}")        print(f"\n❌ CONNECTION FAILED!")

        print(f"Failed: {self.failed}")        print(f"Error: {e}")

                print("\nTroubleshooting:")

        if self.failed == 0:        print("  1. Check your connection details")

            print("\n🎉 ALL TESTS PASSED! 🎉")        print("  2. Verify firewall rules in Azure Portal")

            print("Your Azure SQL integration is working correctly.\n")        print("  3. Ensure ODBC driver is installed")

            return 0        print("  4. Verify database exists")

        else:        return False

            print(f"\n⚠️  {self.failed} TEST(S) FAILED")

            print("Please review the errors above and check your setup.\n")

            return 1def test_2_tables_exist():

    """Test 2: Verify database tables exist"""

    print("\n" + "=" * 80)

def test_1_environment_variables(results: TestResults):    print("TEST 2: Verify Database Tables")

    """Test 1: Check environment variables."""    print("=" * 80)

    print("\n[Test 1] Checking environment variables...")    

        try:

    required_vars = {        config = create_config_from_env()

        'AZURE_SQL_SERVER': 'Database server name',        

        'AZURE_SQL_DATABASE': 'Database name',        print("\n🔍 Checking for required tables...")

        'AZURE_SQL_USERNAME': 'Database username',        

        'AZURE_SQL_PASSWORD': 'Database password'        with AzureSQLManager(config) as db:

    }            cursor = db.connection.cursor()

                

    missing = []            # Check tables

    for var, description in required_vars.items():            cursor.execute("""

        value = os.getenv(var)                SELECT TABLE_NAME 

        if not value:                FROM INFORMATION_SCHEMA.TABLES 

            missing.append(f"{var} ({description})")                WHERE TABLE_SCHEMA = 'dbo' 

            print(f"   ❌ Missing: {var}")                AND TABLE_TYPE = 'BASE TABLE'

        else:                ORDER BY TABLE_NAME

            # Mask sensitive values            """)

            display_value = value if 'PASSWORD' not in var else "****"            

            print(f"   ✅ Found: {var} = {display_value}")            tables = [row[0] for row in cursor.fetchall()]

                

    if missing:            required_tables = [

        results.add_result(                'TestExecutions',

            "Environment Variables",                'Screenshots',

            False,                'Pages',

            f"Missing variables: {', '.join(missing)}"                'PageElements',

        )                'PageEdges'

    else:            ]

        results.add_result("Environment Variables", True)            

            print(f"\nFound {len(tables)} tables:")

            for table in tables:

def test_2_database_connection(results: TestResults):                status = "✅" if table in required_tables else "ℹ️ "

    """Test 2: Test database connection."""                print(f"  {status} {table}")

    print("\n[Test 2] Testing database connection...")            

                # Check which required tables are missing

    try:            missing_tables = set(required_tables) - set(tables)

        db = AzureSQLManager()            

                    if missing_tables:

        if db.connect():                print(f"\n⚠️  Missing required tables: {', '.join(missing_tables)}")

            print(f"   ✅ Connected to: {db.database}")                print("   Run the azure_sql_schema.sql script to create tables")

            db.close()                return False

            results.add_result("Database Connection", True)            else:

            return True                print("\n✅ ALL REQUIRED TABLES EXIST!")

        else:                return True

            print("   ❌ Failed to connect")    

            results.add_result(    except Exception as e:

                "Database Connection",        print(f"\n❌ TABLE CHECK FAILED!")

                False,        print(f"Error: {e}")

                "Could not establish connection"        return False

            )

            return False

            def test_3_insert_test_execution():

    except Exception as e:    """Test 3: Insert a test execution record"""

        print(f"   ❌ Connection error: {e}")    print("\n" + "=" * 80)

        results.add_result(    print("TEST 3: Insert Test Execution")

            "Database Connection",    print("=" * 80)

            False,    

            str(e)    try:

        )        config = create_config_from_env()

        return False        

        print("\n📝 Inserting test execution record...")

        

def test_3_schema_validation(results: TestResults):        with AzureSQLManager(config) as db:

    """Test 3: Validate database schema."""            execution_id = db.insert_test_execution(

    print("\n[Test 3] Validating database schema...")                test_id="TC_TEST_001",

                    status="success",

    required_tables = [                execution_time=3.5,

        'TestExecutions',                steps_executed=5,

        'TestPages',                agent_output="Test execution for verification",

        'TestEdges',                error_message=None,

        'TestElements',                executed_at=datetime.utcnow()

        'TestScreenshots'            )

    ]            

                print(f"\n✅ INSERTION SUCCESSFUL!")

    try:            print(f"   Execution ID: {execution_id}")

        with AzureSQLManager() as db:            

            cursor = db.connection.cursor()            # Verify insertion

                        print("\n🔍 Verifying insertion...")

            missing_tables = []            execution = db.get_test_execution(execution_id)

            for table in required_tables:            

                cursor.execute(            if execution:

                    "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?",                print("✅ Verification successful!")

                    (table,)                print(f"   Test ID: {execution['test_id']}")

                )                print(f"   Status: {execution['status']}")

                if cursor.fetchone():                print(f"   Execution Time: {execution['execution_time']}s")

                    print(f"   ✅ Table exists: {table}")                return execution_id

                else:            else:

                    print(f"   ❌ Missing table: {table}")                print("❌ Verification failed - could not retrieve record")

                    missing_tables.append(table)                return None

                

            if missing_tables:    except Exception as e:

                results.add_result(        print(f"\n❌ INSERTION FAILED!")

                    "Schema Validation",        print(f"Error: {e}")

                    False,        return None

                    f"Missing tables: {', '.join(missing_tables)}"

                )

            else:def test_4_complete_metadata_storage():

                results.add_result("Schema Validation", True)    """Test 4: Store complete metadata structure"""

                    print("\n" + "=" * 80)

    except Exception as e:    print("TEST 4: Store Complete Metadata")

        print(f"   ❌ Schema validation error: {e}")    print("=" * 80)

        results.add_result("Schema Validation", False, str(e))    

    try:

        config = create_config_from_env()

def test_4_insert_test_execution(results: TestResults):        

    """Test 4: Insert a test execution."""        # Create test metadata

    print("\n[Test 4] Testing insert test execution...")        metadata = {

                "test_id": "TC_COMPLETE_001",

    try:            "status": "success",

        with AzureSQLManager() as db:            "execution_time": 5.2,

            execution_id = db.insert_test_execution(            "steps_executed": 8,

                test_id=f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",            "agent_output": json.dumps({

                status="success",                "status": "success",

                execution_time=2.5,                "messages": ["Test message 1", "Test message 2"]

                steps_executed=5,            }),

                browser_type="chromium"            "screenshots": ["test_screenshot.png"],

            )            "error_message": None,

                        "executed_at": datetime.utcnow().isoformat(),

            if execution_id:            "pages": [

                print(f"   ✅ Inserted execution with ID: {execution_id}")                {

                                    "id": "page_1",

                # Verify retrieval                    "label": "Test Page 1",

                execution = db.get_test_execution(execution_id)                    "x": 100,

                if execution:                    "y": 150,

                    print(f"   ✅ Retrieved execution: {execution['test_id']}")                    "metadata": {

                    results.add_result("Insert Test Execution", True)                        "url": "https://example.com/test",

                    return execution_id                        "title": "Test Page",

                else:                        "key_elements": [

                    print("   ❌ Failed to retrieve execution")                            {

                    results.add_result(                                "type": "button",

                        "Insert Test Execution",                                "label": "Test Button",

                        False,                                "selector": "button#test",

                        "Insert succeeded but retrieval failed"                                "id": "test",

                    )                                "class": "btn",

            else:                                "text": "Click Me"

                print("   ❌ Failed to insert execution")                            }

                results.add_result("Insert Test Execution", False)                        ]

                                    }

    except Exception as e:                }

        print(f"   ❌ Insert error: {e}")            ],

        results.add_result("Insert Test Execution", False, str(e))            "edges": []

            }

    return None        

        print("\n📦 Storing complete metadata structure...")

        print(f"   Test ID: {metadata['test_id']}")

def test_5_insert_complete_metadata(results: TestResults):        print(f"   Pages: {len(metadata['pages'])}")

    """Test 5: Insert complete metadata."""        print(f"   Elements: {len(metadata['pages'][0]['metadata']['key_elements'])}")

    print("\n[Test 5] Testing insert complete metadata...")        

            with AzureSQLManager(config) as db:

    try:            execution_id = db.store_playwright_metadata(metadata)

        metadata = create_sample_metadata()            

        metadata['test_id'] = f"TEST_FULL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"            print(f"\n✅ STORAGE SUCCESSFUL!")

                    print(f"   Execution ID: {execution_id}")

        with AzureSQLManager() as db:            

            success = db.insert_full_metadata(metadata)            # Verify storage

                        print("\n🔍 Verifying storage...")

            if success:            

                print(f"   ✅ Inserted complete metadata for: {metadata['test_id']}")            execution = db.get_test_execution(execution_id)

                            pages = db.get_execution_pages(execution_id)

                # Verify all components            

                cursor = db.connection.cursor()            print(f"✅ Execution: {execution['test_id']}")

                cursor.execute(            print(f"✅ Pages: {len(pages)} page(s) stored")

                    "SELECT execution_id FROM TestExecutions WHERE test_id = ?",            

                    (metadata['test_id'],)            for page in pages:

                )                elements = db.get_page_elements(page['page_id'])

                row = cursor.fetchone()                print(f"✅ Page '{page['page_label']}': {len(elements)} element(s)")

                            

                if row:            return execution_id

                    execution_id = row[0]    

                        except Exception as e:

                    pages = db.get_test_pages(execution_id)        print(f"\n❌ STORAGE FAILED!")

                    edges = db.get_test_edges(execution_id)        print(f"Error: {e}")

                    screenshots = db.get_test_screenshots(execution_id)        import traceback

                            traceback.print_exc()

                    print(f"   ✅ Pages: {len(pages)}")        return None

                    print(f"   ✅ Edges: {len(edges)}")

                    print(f"   ✅ Screenshots: {len(screenshots)}")

                    def test_5_query_data():

                    # Check elements    """Test 5: Query stored data"""

                    if pages:    print("\n" + "=" * 80)

                        elements = db.get_page_elements(pages[0]['page_id'])    print("TEST 5: Query Stored Data")

                        print(f"   ✅ Elements on first page: {len(elements)}")    print("=" * 80)

                        

                    results.add_result("Insert Complete Metadata", True)    try:

                    return execution_id        config = create_config_from_env()

                else:        

                    results.add_result(        print("\n🔍 Querying all test executions...")

                        "Insert Complete Metadata",        

                        False,        with AzureSQLManager(config) as db:

                        "Metadata inserted but not found"            cursor = db.connection.cursor()

                    )            

            else:            # Get count

                print("   ❌ Failed to insert metadata")            cursor.execute("SELECT COUNT(*) FROM dbo.TestExecutions")

                results.add_result("Insert Complete Metadata", False)            count = cursor.fetchone()[0]

                            

    except Exception as e:            print(f"\n✅ Found {count} test execution(s)")

        print(f"   ❌ Metadata insert error: {e}")            

        results.add_result("Insert Complete Metadata", False, str(e))            if count > 0:

                    # Get recent executions

    return None                cursor.execute("""

                    SELECT TOP 5

                        test_id,

def test_6_query_operations(results: TestResults):                        status,

    """Test 6: Test query operations."""                        execution_time,

    print("\n[Test 6] Testing query operations...")                        steps_executed,

                            executed_at

    try:                    FROM dbo.TestExecutions

        with AzureSQLManager() as db:                    ORDER BY executed_at DESC

            # Test status query                """)

            successful = db.get_executions_by_status("success")                

            print(f"   ✅ Found {len(successful)} successful executions")                print("\n📊 Recent Executions:")

                            print("-" * 80)

            # Test statistics                

            stats = db.get_execution_statistics()                for row in cursor.fetchall():

            print(f"   ✅ Statistics: {stats.get('total_executions', 0)} total executions")                    print(f"  Test ID: {row[0]}")

            print(f"   ✅ Success rate: {stats.get('success_rate', 0):.2f}%")                    print(f"    Status: {row[1]}")

                                print(f"    Time: {row[2]}s")

            results.add_result("Query Operations", True)                    print(f"    Steps: {row[3]}")

                                print(f"    Executed: {row[4]}")

    except Exception as e:                    print("-" * 80)

        print(f"   ❌ Query error: {e}")                

        results.add_result("Query Operations", False, str(e))                return True

            else:

                print("ℹ️  No executions found (this is normal for first run)")

def test_7_update_operations(results: TestResults):                return True

    """Test 7: Test update operations."""    

    print("\n[Test 7] Testing update operations...")    except Exception as e:

            print(f"\n❌ QUERY FAILED!")

    try:        print(f"Error: {e}")

        with AzureSQLManager() as db:        return False

            # Create a test execution

            execution_id = db.insert_test_execution(

                test_id=f"TEST_UPDATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",def run_all_tests():

                status="running",    """Run all tests in sequence"""

                execution_time=0.0,    print("\n" + "=" * 80)

                steps_executed=0    print("AZURE SQL DATABASE - INTEGRATION TEST SUITE")

            )    print("=" * 80)

                print("\nThis script will test your Azure SQL database setup.")

            if execution_id:    print("Make sure you have:")

                # Update status    print("  1. Created the database in Azure")

                success = db.update_execution_status(    print("  2. Run the azure_sql_schema.sql script")

                    execution_id=execution_id,    print("  3. Set up environment variables or updated the config")

                    status="success"    print("  4. Configured firewall rules")

                )    

                    input("\nPress Enter to start tests...")

                if success:    

                    # Verify update    results = {}

                    execution = db.get_test_execution(execution_id)    

                    if execution and execution['status'] == "success":    # Test 1: Connection

                        print(f"   ✅ Status updated successfully")    results['connection'] = test_1_connection()

                        results.add_result("Update Operations", True)    

                    else:    if not results['connection']:

                        results.add_result(        print("\n⚠️  Connection failed. Fix connection issues before proceeding.")

                            "Update Operations",        return

                            False,    

                            "Update succeeded but verification failed"    # Test 2: Tables

                        )    results['tables'] = test_2_tables_exist()

                else:    

                    results.add_result("Update Operations", False, "Update failed")    if not results['tables']:

            else:        print("\n⚠️  Tables missing. Run azure_sql_schema.sql to create tables.")

                results.add_result(        return

                    "Update Operations",    

                    False,    # Test 3: Insert

                    "Could not create test execution"    execution_id = test_3_insert_test_execution()

                )    results['insert'] = execution_id is not None

                    

    except Exception as e:    # Test 4: Complete metadata

        print(f"   ❌ Update error: {e}")    execution_id = test_4_complete_metadata_storage()

        results.add_result("Update Operations", False, str(e))    results['metadata'] = execution_id is not None

    

    # Test 5: Query

def test_8_delete_operations(results: TestResults):    results['query'] = test_5_query_data()

    """Test 8: Test delete operations."""    

    print("\n[Test 8] Testing delete operations...")    # Summary

        print("\n" + "=" * 80)

    try:    print("TEST SUMMARY")

        with AzureSQLManager() as db:    print("=" * 80)

            # Create a test execution    

            execution_id = db.insert_test_execution(    all_passed = True

                test_id=f"TEST_DELETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",    for test_name, passed in results.items():

                status="success",        status = "✅ PASSED" if passed else "❌ FAILED"

                execution_time=1.0,        print(f"{status}: {test_name.replace('_', ' ').title()}")

                steps_executed=1        if not passed:

            )            all_passed = False

                

            if execution_id:    print("=" * 80)

                print(f"   ✅ Created test execution: {execution_id}")    

                    if all_passed:

                # Delete it        print("\n🎉 ALL TESTS PASSED!")

                success = db.delete_test_execution(execution_id)        print("\nYour Azure SQL integration is working correctly!")

                        print("You can now use it to store Playwright automation metadata.")

                if success:    else:

                    # Verify deletion        print("\n⚠️  SOME TESTS FAILED")

                    execution = db.get_test_execution(execution_id)        print("\nPlease review the error messages above and:")

                    if execution is None:        print("  1. Check your connection configuration")

                        print(f"   ✅ Execution deleted successfully")        print("  2. Verify database schema is created")

                        results.add_result("Delete Operations", True)        print("  3. Check firewall rules")

                    else:        print("  4. Review the setup guide: AZURE_SQL_SETUP_GUIDE.md")

                        results.add_result(    

                            "Delete Operations",    print()

                            False,

                            "Delete succeeded but record still exists"

                        )if __name__ == "__main__":

                else:    try:

                    results.add_result("Delete Operations", False, "Delete failed")        run_all_tests()

            else:    except KeyboardInterrupt:

                results.add_result(        print("\n\n⚠️  Tests interrupted by user")

                    "Delete Operations",    except Exception as e:

                    False,        print(f"\n\n❌ Unexpected error: {e}")

                    "Could not create test execution"        import traceback

                )        traceback.print_exc()

                
    except Exception as e:
        print(f"   ❌ Delete error: {e}")
        results.add_result("Delete Operations", False, str(e))


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  AZURE SQL INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\nThis script will test your Azure SQL setup")
    print("Make sure you have:")
    print("  1. Created Azure SQL Database")
    print("  2. Deployed the schema (azure_sql_schema.sql)")
    print("  3. Configured .env with credentials")
    print("\nStarting tests...\n")
    
    results = TestResults()
    
    # Run all tests
    test_1_environment_variables(results)
    test_2_database_connection(results)
    test_3_schema_validation(results)
    test_4_insert_test_execution(results)
    test_5_insert_complete_metadata(results)
    test_6_query_operations(results)
    test_7_update_operations(results)
    test_8_delete_operations(results)
    
    # Print summary
    exit_code = results.print_summary()
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
