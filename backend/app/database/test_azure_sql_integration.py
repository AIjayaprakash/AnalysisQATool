"""
Test Script for Azure SQL Integration.

Run this script to verify your Azure SQL setup is working correctly.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.azure_sql_manager import (
    AzureSQLManager,
    AzureSQLConfig,
    create_config_from_env
)


def test_1_connection():
    """Test 1: Verify database connection."""
    print("\n" + "=" * 80)
    print("TEST 1: Verify Database Connection")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        print(f"\nConnection Details:")
        print(f"  Server: {config.server}")
        print(f"  Database: {config.database}")
        print(f"  Username: {config.username}")
        
        print("\n🔌 Attempting connection...")
        
        with AzureSQLManager(config) as db:
            cursor = db.connection.cursor()
            cursor.execute("SELECT @@VERSION, GETDATE()")
            version, current_time = cursor.fetchone()
            
            print("\n✅ CONNECTION SUCCESSFUL!")
            print(f"\nServer Info:")
            print(f"  Version: {version[:100]}...")
            print(f"  Server Time: {current_time}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your connection details")
        print("  2. Verify firewall rules in Azure Portal")
        print("  3. Ensure ODBC driver is installed")
        return False


def test_2_tables_exist():
    """Test 2: Verify database tables exist."""
    print("\n" + "=" * 80)
    print("TEST 2: Verify Database Tables")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        
        print("\n🔍 Checking for required tables...")
        
        with AzureSQLManager(config) as db:
            cursor = db.connection.cursor()
            
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'dbo' 
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'TestExecutions',
                'Screenshots',
                'Pages',
                'PageElements',
                'PageEdges'
            ]
            
            print(f"\nFound {len(tables)} tables:")
            for table in tables:
                status = "✅" if table in required_tables else "ℹ️ "
                print(f"  {status} {table}")
            
            missing_tables = set(required_tables) - set(tables)
            
            if missing_tables:
                print(f"\n⚠️  Missing required tables: {', '.join(missing_tables)}")
                print("   Run the azure_sql_schema.sql script to create tables")
                return False
            else:
                print("\n✅ ALL REQUIRED TABLES EXIST!")
                return True
    
    except Exception as e:
        print(f"\n❌ TABLE CHECK FAILED!")
        print(f"Error: {e}")
        return False


def test_3_insert_test_execution():
    """Test 3: Insert a test execution record."""
    print("\n" + "=" * 80)
    print("TEST 3: Insert Test Execution")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        
        print("\n📝 Inserting test execution record...")
        
        with AzureSQLManager(config) as db:
            execution_id = db.insert_test_execution(
                test_id="TC_TEST_001",
                status="success",
                execution_time=3.5,
                steps_executed=5,
                agent_output="Test execution for verification",
                error_message=None,
                executed_at=datetime.utcnow()
            )
            
            print(f"\n✅ INSERTION SUCCESSFUL!")
            print(f"   Execution ID: {execution_id}")
            
            # Verify insertion
            print("\n🔍 Verifying insertion...")
            execution = db.get_test_execution(execution_id)
            
            if execution:
                print("✅ Verification successful!")
                print(f"   Test ID: {execution['test_id']}")
                print(f"   Status: {execution['status']}")
                print(f"   Execution Time: {execution['execution_time']}s")
                return execution_id
            else:
                print("❌ Verification failed")
                return None
    
    except Exception as e:
        print(f"\n❌ INSERTION FAILED!")
        print(f"Error: {e}")
        return None


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 80)
    print("AZURE SQL DATABASE - INTEGRATION TEST SUITE")
    print("=" * 80)
    print("\nThis script will test your Azure SQL database setup.")
    
    input("\nPress Enter to start tests...")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = test_1_connection()
    
    if not results['connection']:
        print("\n⚠️  Connection failed. Fix connection issues before proceeding.")
        return
    
    # Test 2: Tables
    results['tables'] = test_2_tables_exist()
    
    if not results['tables']:
        print("\n⚠️  Tables missing. Run azure_sql_schema.sql to create tables.")
        return
    
    # Test 3: Insert
    execution_id = test_3_insert_test_execution()
    results['insert'] = execution_id is not None
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour Azure SQL integration is working correctly!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the error messages above.")
    
    print()


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
