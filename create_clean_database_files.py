"""
Script to create clean database files for Azure SQL integration.
Run this script to regenerate all database Python files with proper formatting.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "backend" / "app" / "database"
BASE_DIR.mkdir(parents=True, exist_ok=True)

print(f"Creating files in: {BASE_DIR}")
print("=" * 80)

# File 1: azure_sql_manager.py
print("\n1. Creating azure_sql_manager.py...")

azure_sql_manager_content = '''"""
Azure SQL Database Manager for Playwright Test Execution Metadata.

This module provides database operations for storing and retrieving
Playwright automation test execution metadata.
"""

import pyodbc
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AzureSQLConfig:
    """Configuration for Azure SQL Database connection."""
    server: str
    database: str
    username: str
    password: str
    driver: str = "{ODBC Driver 18 for SQL Server}"
    port: int = 1433
    encrypt: bool = True
    trust_server_certificate: bool = False


def create_config_from_env() -> AzureSQLConfig:
    """Create configuration from environment variables."""
    import os
    return AzureSQLConfig(
        server=os.getenv("AZURE_SQL_SERVER", ""),
        database=os.getenv("AZURE_SQL_DATABASE", ""),
        username=os.getenv("AZURE_SQL_USERNAME", ""),
        password=os.getenv("AZURE_SQL_PASSWORD", ""),
        driver=os.getenv("AZURE_SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")
    )


class AzureSQLManager:
    """Manages Azure SQL Database operations for test execution metadata."""
    
    def __init__(self, config: AzureSQLConfig):
        """Initialize Azure SQL Manager."""
        self.config = config
        self.connection = None
    
    def get_connection_string(self) -> str:
        """Generate Azure SQL connection string."""
        return (
            f"DRIVER={self.config.driver};"
            f"SERVER={self.config.server},{self.config.port};"
            f"DATABASE={self.config.database};"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
            f"Encrypt={'yes' if self.config.encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if self.config.trust_server_certificate else 'no'};"
        )
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            conn_str = self.get_connection_string()
            self.connection = pyodbc.connect(conn_str, timeout=30)
            logger.info(f"Connected to Azure SQL: {self.config.database}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def store_playwright_metadata(self, metadata: Dict[str, Any]) -> Optional[int]:
        """
        Store complete Playwright metadata in database.
        
        Args:
            metadata: Complete metadata dictionary from Playwright execution
            
        Returns:
            execution_id if successful, None otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Insert test execution
            insert_query = """
            INSERT INTO dbo.TestExecutions (
                test_id, status, execution_time, steps_executed,
                agent_output, error_message, executed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
            SELECT SCOPE_IDENTITY() AS execution_id;
            """
            
            cursor.execute(
                insert_query,
                (
                    metadata.get("test_id", "UNKNOWN"),
                    metadata.get("status", "unknown"),
                    metadata.get("execution_time", 0.0),
                    metadata.get("steps_executed", 0),
                    str(metadata.get("agent_output", "")),
                    metadata.get("error_message"),
                    metadata.get("executed_at", datetime.utcnow())
                )
            )
            
            result = cursor.fetchone()
            execution_id = int(result[0]) if result else None
            
            # Store screenshots
            for screenshot in metadata.get("screenshots", []):
                self._insert_screenshot(cursor, execution_id, screenshot)
            
            # Store pages
            page_id_map = {}
            for page in metadata.get("pages", []):
                page_id = self._insert_page(cursor, execution_id, page)
                if page_id:
                    page_id_map[page.get("id")] = page_id
                    
                    # Store elements for this page
                    for element in page.get("metadata", {}).get("key_elements", []):
                        self._insert_element(cursor, page_id, element)
            
            # Store edges
            for edge in metadata.get("edges", []):
                self._insert_edge(cursor, execution_id, edge, page_id_map)
            
            self.connection.commit()
            logger.info(f"Stored metadata for test: {metadata.get('test_id')}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error storing metadata: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def _insert_screenshot(self, cursor, execution_id: int, screenshot: Any):
        """Insert screenshot record."""
        query = """
        INSERT INTO dbo.Screenshots (execution_id, filename, file_path)
        VALUES (?, ?, ?)
        """
        filename = screenshot if isinstance(screenshot, str) else str(screenshot)
        cursor.execute(query, (execution_id, filename, filename))
    
    def _insert_page(self, cursor, execution_id: int, page: Dict) -> Optional[int]:
        """Insert page record and return page_id."""
        query = """
        INSERT INTO dbo.Pages (execution_id, page_node_id, page_label, x_position, y_position)
        VALUES (?, ?, ?, ?, ?);
        SELECT SCOPE_IDENTITY() AS page_id;
        """
        cursor.execute(
            query,
            (
                execution_id,
                page.get("id", ""),
                page.get("label", "Unknown"),
                page.get("x", 0),
                page.get("y", 0)
            )
        )
        result = cursor.fetchone()
        return int(result[0]) if result else None
    
    def _insert_element(self, cursor, page_id: int, element: Dict):
        """Insert page element record."""
        query = """
        INSERT INTO dbo.PageElements (
            page_id, element_type, element_label,
            selector, element_id, element_class, element_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            (
                page_id,
                element.get("type", ""),
                element.get("label", ""),
                element.get("selector", ""),
                element.get("id", ""),
                element.get("class", ""),
                element.get("text", "")
            )
        )
    
    def _insert_edge(self, cursor, execution_id: int, edge: Dict, page_id_map: Dict):
        """Insert edge record."""
        query = """
        INSERT INTO dbo.PageEdges (
            execution_id, source_page_id, target_page_id, edge_label
        )
        VALUES (?, ?, ?, ?)
        """
        source_id = page_id_map.get(edge.get("source"))
        target_id = page_id_map.get(edge.get("target"))
        
        if source_id and target_id:
            cursor.execute(
                query,
                (execution_id, source_id, target_id, edge.get("label", ""))
            )
    
    def get_test_execution(self, execution_id: int) -> Optional[Dict]:
        """Retrieve test execution by ID."""
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT execution_id, test_id, status, execution_time,
                   steps_executed, agent_output, error_message, executed_at
            FROM dbo.TestExecutions
            WHERE execution_id = ?
            """
            cursor.execute(query, (execution_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "execution_id": row[0],
                    "test_id": row[1],
                    "status": row[2],
                    "execution_time": float(row[3]) if row[3] else None,
                    "steps_executed": row[4],
                    "agent_output": row[5],
                    "error_message": row[6],
                    "executed_at": row[7]
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving execution: {e}")
            return None
    
    def get_execution_pages(self, execution_id: int) -> List[Dict]:
        """Retrieve all pages for an execution."""
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT page_id, page_node_id, page_label, x_position, y_position
            FROM dbo.Pages
            WHERE execution_id = ?
            """
            cursor.execute(query, (execution_id,))
            
            return [
                {
                    "page_id": row[0],
                    "page_node_id": row[1],
                    "page_label": row[2],
                    "x_position": row[3],
                    "y_position": row[4]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error retrieving pages: {e}")
            return []
    
    def get_page_elements(self, page_id: int) -> List[Dict]:
        """Retrieve all elements for a page."""
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT element_id, element_type, element_label, selector,
                   element_id, element_class, element_text
            FROM dbo.PageElements
            WHERE page_id = ?
            """
            cursor.execute(query, (page_id,))
            
            return [
                {
                    "element_id": row[0],
                    "type": row[1],
                    "label": row[2],
                    "selector": row[3],
                    "id": row[4],
                    "class": row[5],
                    "text": row[6]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"Error retrieving elements: {e}")
            return []


if __name__ == "__main__":
    print("Azure SQL Manager loaded")
    print("Import this module to use AzureSQLManager class")
'''

with open(BASE_DIR / "azure_sql_manager.py", "w", encoding="utf-8") as f:
    f.write(azure_sql_manager_content)
print("   ✅ Created azure_sql_manager.py")

# File 2: integration_api_to_azure_sql.py
print("\n2. Creating integration_api_to_azure_sql.py...")

integration_content = '''"""
API Integration Module for Azure SQL Database.

This module integrates with FastAPI endpoints to automatically store
Playwright execution results to Azure SQL Database.
"""

import json
import os
import logging
from typing import Dict, Any, Optional

from database.azure_sql_manager import (
    AzureSQLManager,
    AzureSQLConfig,
    create_config_from_env
)

logger = logging.getLogger(__name__)


def store_to_azure_sql(
    execution_result: Dict[str, Any],
    config: Optional[AzureSQLConfig] = None
) -> Optional[int]:
    """
    Store execution result to Azure SQL Database.
    
    Args:
        execution_result: Execution result dictionary from API
        config: Optional Azure SQL configuration
        
    Returns:
        execution_id if successful, None otherwise
    """
    try:
        # Use provided config or load from environment
        db_config = config or create_config_from_env()
        
        with AzureSQLManager(db_config) as db_manager:
            execution_id = db_manager.store_playwright_metadata(execution_result)
            
            if execution_id:
                logger.info(
                    f"Stored execution to Azure SQL",
                    extra={"execution_id": execution_id, "test_id": execution_result.get("test_id")}
                )
                return execution_id
            else:
                logger.warning("Failed to store execution to Azure SQL")
                return None
                
    except Exception as e:
        logger.error(f"Azure SQL storage error: {e}", exc_info=True)
        return None


def verify_azure_sql_connection(config: Optional[AzureSQLConfig] = None) -> bool:
    """
    Verify Azure SQL connection.
    
    Args:
        config: Optional Azure SQL configuration
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        db_config = config or create_config_from_env()
        
        with AzureSQLManager(db_config) as db_manager:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result and result[0] == 1:
                logger.info("✅ Azure SQL connection verified")
                return True
            else:
                logger.error("❌ Azure SQL connection verification failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Azure SQL connection failed: {e}")
        return False


def get_execution_summary(
    execution_id: int,
    config: Optional[AzureSQLConfig] = None
) -> Optional[Dict]:
    """
    Get execution summary from Azure SQL.
    
    Args:
        execution_id: Execution ID to retrieve
        config: Optional Azure SQL configuration
        
    Returns:
        Execution summary dictionary or None
    """
    try:
        db_config = config or create_config_from_env()
        
        with AzureSQLManager(db_config) as db_manager:
            execution = db_manager.get_test_execution(execution_id)
            
            if execution:
                pages = db_manager.get_execution_pages(execution_id)
                execution["pages"] = pages
                
                # Get elements for each page
                for page in execution["pages"]:
                    elements = db_manager.get_page_elements(page["page_id"])
                    page["elements"] = elements
                
                return execution
            
            return None
            
    except Exception as e:
        logger.error(f"Failed to get execution summary: {e}")
        return None


if __name__ == "__main__":
    print("Azure SQL Integration Module")
    print("Functions: store_to_azure_sql, verify_azure_sql_connection, get_execution_summary")
'''

with open(BASE_DIR / "integration_api_to_azure_sql.py", "w", encoding="utf-8") as f:
    f.write(integration_content)
print("   ✅ Created integration_api_to_azure_sql.py")

# File 3: example_azure_sql_usage.py
print("\n3. Creating example_azure_sql_usage.py...")

example_content = '''"""
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
    print("\\n" + "=" * 70)
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
    print("\\n" + "=" * 70)
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
    print("\\n" + "=" * 70)
    print("Azure SQL Manager - Examples")
    print("=" * 70)
    
    # Check environment
    required_vars = ["AZURE_SQL_SERVER", "AZURE_SQL_DATABASE", 
                     "AZURE_SQL_USERNAME", "AZURE_SQL_PASSWORD"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"\\n❌ Missing environment variables: {', '.join(missing)}")
        print("Please set them in your .env file")
        return
    
    # Run examples
    if example_1_basic_connection():
        example_2_store_metadata()


if __name__ == "__main__":
    run_all_examples()
'''

with open(BASE_DIR / "example_azure_sql_usage.py", "w", encoding="utf-8") as f:
    f.write(example_content)
print("   ✅ Created example_azure_sql_usage.py")

# File 4: test_azure_sql_integration.py
print("\n4. Creating test_azure_sql_integration.py...")

test_content = '''"""
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
    print("\\n" + "=" * 80)
    print("TEST 1: Verify Database Connection")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        print(f"\\nConnection Details:")
        print(f"  Server: {config.server}")
        print(f"  Database: {config.database}")
        print(f"  Username: {config.username}")
        
        print("\\n🔌 Attempting connection...")
        
        with AzureSQLManager(config) as db:
            cursor = db.connection.cursor()
            cursor.execute("SELECT @@VERSION, GETDATE()")
            version, current_time = cursor.fetchone()
            
            print("\\n✅ CONNECTION SUCCESSFUL!")
            print(f"\\nServer Info:")
            print(f"  Version: {version[:100]}...")
            print(f"  Server Time: {current_time}")
        
        return True
    
    except Exception as e:
        print(f"\\n❌ CONNECTION FAILED!")
        print(f"Error: {e}")
        print("\\nTroubleshooting:")
        print("  1. Check your connection details")
        print("  2. Verify firewall rules in Azure Portal")
        print("  3. Ensure ODBC driver is installed")
        return False


def test_2_tables_exist():
    """Test 2: Verify database tables exist."""
    print("\\n" + "=" * 80)
    print("TEST 2: Verify Database Tables")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        
        print("\\n🔍 Checking for required tables...")
        
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
            
            print(f"\\nFound {len(tables)} tables:")
            for table in tables:
                status = "✅" if table in required_tables else "ℹ️ "
                print(f"  {status} {table}")
            
            missing_tables = set(required_tables) - set(tables)
            
            if missing_tables:
                print(f"\\n⚠️  Missing required tables: {', '.join(missing_tables)}")
                print("   Run the azure_sql_schema.sql script to create tables")
                return False
            else:
                print("\\n✅ ALL REQUIRED TABLES EXIST!")
                return True
    
    except Exception as e:
        print(f"\\n❌ TABLE CHECK FAILED!")
        print(f"Error: {e}")
        return False


def test_3_insert_test_execution():
    """Test 3: Insert a test execution record."""
    print("\\n" + "=" * 80)
    print("TEST 3: Insert Test Execution")
    print("=" * 80)
    
    try:
        config = create_config_from_env()
        
        print("\\n📝 Inserting test execution record...")
        
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
            
            print(f"\\n✅ INSERTION SUCCESSFUL!")
            print(f"   Execution ID: {execution_id}")
            
            # Verify insertion
            print("\\n🔍 Verifying insertion...")
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
        print(f"\\n❌ INSERTION FAILED!")
        print(f"Error: {e}")
        return None


def run_all_tests():
    """Run all tests in sequence."""
    print("\\n" + "=" * 80)
    print("AZURE SQL DATABASE - INTEGRATION TEST SUITE")
    print("=" * 80)
    print("\\nThis script will test your Azure SQL database setup.")
    
    input("\\nPress Enter to start tests...")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = test_1_connection()
    
    if not results['connection']:
        print("\\n⚠️  Connection failed. Fix connection issues before proceeding.")
        return
    
    # Test 2: Tables
    results['tables'] = test_2_tables_exist()
    
    if not results['tables']:
        print("\\n⚠️  Tables missing. Run azure_sql_schema.sql to create tables.")
        return
    
    # Test 3: Insert
    execution_id = test_3_insert_test_execution()
    results['insert'] = execution_id is not None
    
    # Summary
    print("\\n" + "=" * 80)
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
        print("\\n🎉 ALL TESTS PASSED!")
        print("\\nYour Azure SQL integration is working correctly!")
    else:
        print("\\n⚠️  SOME TESTS FAILED")
        print("\\nPlease review the error messages above.")
    
    print()


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\\n\\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
'''

with open(BASE_DIR / "test_azure_sql_integration.py", "w", encoding="utf-8") as f:
    f.write(test_content)
print("   ✅ Created test_azure_sql_integration.py")

print("\\n" + "=" * 80)
print("✅ ALL FILES CREATED SUCCESSFULLY!")
print("=" * 80)
print(f"\\nLocation: {BASE_DIR}")
print("\\nFiles created:")
print("  1. __init__.py")
print("  2. azure_sql_manager.py")
print("  3. integration_api_to_azure_sql.py")
print("  4. example_azure_sql_usage.py")
print("  5. test_azure_sql_integration.py")
print("\\nYou can now use these files for Azure SQL integration!")
print()
