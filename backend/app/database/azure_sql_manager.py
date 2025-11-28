""""""

Azure SQL Database Manager for Playwright Test Execution MetadataAzure SQL Database Manager for Playwright Automation Metadata



This module provides a comprehensive interface for storing and retrievingThis module provides functionality to store Playwright automation test execution

Playwright test execution metadata in Azure SQL Database.data into Azure SQL Database.

"""

Features:

- Connection management with retry logicimport pyodbc

- Full CRUD operations for all tablesimport json

- Transaction supportfrom typing import Dict, List, Optional, Any

- Bulk insert capabilitiesfrom datetime import datetime

- Error handling and loggingimport logging

from dataclasses import dataclass

Author: Generated for SeleniumMCPFlow Project

Date: 2024# Configure logging

"""logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

import os

import json

import logging@dataclass

from typing import Optional, Dict, List, Any, Tupleclass AzureSQLConfig:

from datetime import datetime, timedelta    """Configuration for Azure SQL Database connection"""

import time    server: str  # e.g., "your-server.database.windows.net"

    database: str

try:    username: str

    import pyodbc    password: str

except ImportError:    driver: str = "{ODBC Driver 18 for SQL Server}"  # or "{ODBC Driver 17 for SQL Server}"

    pyodbc = None    port: int = 1433

    print("⚠️ Warning: pyodbc not installed. Install it with: pip install pyodbc")    encrypt: bool = True

    trust_server_certificate: bool = False

# Configure logging

logging.basicConfig(

    level=logging.INFO,class AzureSQLManager:

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'    """Manages Azure SQL Database operations for test execution metadata"""

)    

logger = logging.getLogger(__name__)    def __init__(self, config: AzureSQLConfig):

        """

        Initialize Azure SQL Manager

class AzureSQLManager:        

    """        Args:

    Manager class for Azure SQL Database operations.            config: Azure SQL configuration

            """

    Handles connection management, CRUD operations, and data integrity        self.config = config

    for Playwright test execution metadata.        self.connection = None

    """        

        def get_connection_string(self) -> str:

    def __init__(self, config: Optional[Dict[str, str]] = None):        """

        """        Generate Azure SQL connection string

        Initialize the Azure SQL Manager.        

                Returns:

        Args:            Connection string for Azure SQL

            config: Optional database configuration dictionary.        """

                   If not provided, reads from environment variables.        return (

                               f"DRIVER={self.config.driver};"

        Environment Variables:            f"SERVER={self.config.server},{self.config.port};"

            AZURE_SQL_SERVER: Database server name            f"DATABASE={self.config.database};"

            AZURE_SQL_DATABASE: Database name            f"UID={self.config.username};"

            AZURE_SQL_USERNAME: Database username            f"PWD={self.config.password};"

            AZURE_SQL_PASSWORD: Database password            f"Encrypt={'yes' if self.config.encrypt else 'no'};"

            AZURE_SQL_DRIVER: ODBC driver (default: ODBC Driver 17 for SQL Server)            f"TrustServerCertificate={'yes' if self.config.trust_server_certificate else 'no'};"

        """            f"Connection Timeout=30;"

        if config:        )

            self.server = config.get('server')    

            self.database = config.get('database')    def connect(self):

            self.username = config.get('username')        """Establish connection to Azure SQL Database"""

            self.password = config.get('password')        try:

            self.driver = config.get('driver', '{ODBC Driver 17 for SQL Server}')            connection_string = self.get_connection_string()

        else:            self.connection = pyodbc.connect(connection_string)

            self.server = os.getenv('AZURE_SQL_SERVER')            logger.info("Successfully connected to Azure SQL Database")

            self.database = os.getenv('AZURE_SQL_DATABASE')            return self.connection

            self.username = os.getenv('AZURE_SQL_USERNAME')        except pyodbc.Error as e:

            self.password = os.getenv('AZURE_SQL_PASSWORD')            logger.error(f"Failed to connect to Azure SQL Database: {e}")

            self.driver = os.getenv('AZURE_SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')            raise

            

        self.connection = None    def disconnect(self):

        self.connection_string = self._build_connection_string()        """Close connection to Azure SQL Database"""

                if self.connection:

    def _build_connection_string(self) -> str:            self.connection.close()

        """Build the ODBC connection string."""            logger.info("Disconnected from Azure SQL Database")

        return (    

            f'DRIVER={self.driver};'    def __enter__(self):

            f'SERVER={self.server};'        """Context manager entry"""

            f'DATABASE={self.database};'        self.connect()

            f'UID={self.username};'        return self

            f'PWD={self.password};'    

            f'Encrypt=yes;'    def __exit__(self, exc_type, exc_val, exc_tb):

            f'TrustServerCertificate=no;'        """Context manager exit"""

            f'Connection Timeout=30;'        self.disconnect()

        )    

        def insert_test_execution(

    def connect(self, max_retries: int = 3) -> bool:        self,

        """        test_id: str,

        Establish connection to Azure SQL Database with retry logic.        status: str,

                execution_time: float,

        Args:        steps_executed: int,

            max_retries: Maximum number of connection attempts        agent_output: str,

                    error_message: Optional[str] = None,

        Returns:        executed_at: Optional[datetime] = None

            True if connection successful, False otherwise    ) -> int:

        """        """

        if pyodbc is None:        Insert test execution record

            logger.error("pyodbc is not installed. Cannot connect to database.")        

            return False        Args:

                        test_id: Test case ID

        for attempt in range(max_retries):            status: Execution status (success, failed, error, timeout)

            try:            execution_time: Execution time in seconds

                self.connection = pyodbc.connect(self.connection_string)            steps_executed: Number of steps executed

                logger.info(f"✅ Connected to Azure SQL Database: {self.database}")            agent_output: Complete agent output log

                return True            error_message: Error message if any

            except pyodbc.Error as e:            executed_at: Execution timestamp

                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")            

                if attempt < max_retries - 1:        Returns:

                    time.sleep(2 ** attempt)  # Exponential backoff            execution_id of the inserted record

                else:        """

                    logger.error(f"❌ Failed to connect after {max_retries} attempts")        if not self.connection:

                    return False            raise ConnectionError("Not connected to database. Call connect() first.")

        return False        

            cursor = self.connection.cursor()

    def close(self):        

        """Close the database connection safely."""        try:

        if self.connection:            # Convert agent_output to string if it's a dict

            try:            if isinstance(agent_output, dict):

                self.connection.close()                agent_output = json.dumps(agent_output)

                logger.info("Database connection closed")            

            except Exception as e:            query = """

                logger.error(f"Error closing connection: {e}")            INSERT INTO dbo.TestExecutions 

                    (test_id, status, execution_time, steps_executed, agent_output, error_message, executed_at)

    def __enter__(self):            VALUES (?, ?, ?, ?, ?, ?, ?)

        """Context manager entry."""            """

        self.connect()            

        return self            executed_at = executed_at or datetime.utcnow()

                

    def __exit__(self, exc_type, exc_val, exc_tb):            cursor.execute(

        """Context manager exit."""                query,

        self.close()                (test_id, status, execution_time, steps_executed, agent_output, error_message, executed_at)

                )

    # ==================== TestExecutions Table Operations ====================            

                # Get the inserted ID

    def insert_test_execution(            cursor.execute("SELECT @@IDENTITY AS execution_id")

        self,            execution_id = cursor.fetchone()[0]

        test_id: str,            

        status: str,            self.connection.commit()

        execution_time: float,            logger.info(f"Inserted test execution: {test_id} (execution_id: {execution_id})")

        steps_executed: int,            

        browser_type: Optional[str] = None,            return int(execution_id)

        viewport_width: Optional[int] = None,        

        viewport_height: Optional[int] = None,        except pyodbc.Error as e:

        agent_output: Optional[str] = None,            self.connection.rollback()

        error_message: Optional[str] = None,            logger.error(f"Failed to insert test execution: {e}")

        metadata_json: Optional[str] = None            raise

    ) -> Optional[int]:        finally:

        """            cursor.close()

        Insert a test execution record.    

            def insert_screenshot(

        Args:        self,

            test_id: Unique test identifier        execution_id: int,

            status: Execution status (success/failed/error/timeout)        filename: str,

            execution_time: Total execution time in seconds        file_path: Optional[str] = None,

            steps_executed: Number of steps executed        step_number: Optional[int] = None,

            browser_type: Browser used (chromium/firefox/webkit)        description: Optional[str] = None

            viewport_width: Browser viewport width    ) -> int:

            viewport_height: Browser viewport height        """

            agent_output: Complete agent output text        Insert screenshot record

            error_message: Error message if failed        

            metadata_json: Complete metadata as JSON string        Args:

                        execution_id: Foreign key to test execution

        Returns:            filename: Screenshot filename

            execution_id if successful, None otherwise            file_path: Full file path

        """            step_number: Step number when screenshot was taken

        if not self.connection:            description: Screenshot description

            logger.error("No database connection")            

            return None        Returns:

                    screenshot_id of the inserted record

        query = """        """

        INSERT INTO TestExecutions (        if not self.connection:

            test_id, status, execution_time, steps_executed,            raise ConnectionError("Not connected to database")

            browser_type, viewport_width, viewport_height,        

            agent_output, error_message, metadata_json, executed_at        cursor = self.connection.cursor()

        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());        

        SELECT SCOPE_IDENTITY() AS execution_id;        try:

        """            query = """

                    INSERT INTO dbo.Screenshots 

        try:                (execution_id, filename, file_path, step_number, description)

            cursor = self.connection.cursor()            VALUES (?, ?, ?, ?, ?)

            cursor.execute(            """

                query,            

                (test_id, status, execution_time, steps_executed,            cursor.execute(query, (execution_id, filename, file_path, step_number, description))

                 browser_type, viewport_width, viewport_height,            

                 agent_output, error_message, metadata_json)            cursor.execute("SELECT @@IDENTITY AS screenshot_id")

            )            screenshot_id = cursor.fetchone()[0]

                        

            result = cursor.fetchone()            self.connection.commit()

            execution_id = int(result[0]) if result else None            logger.info(f"Inserted screenshot: {filename} (screenshot_id: {screenshot_id})")

                        

            self.connection.commit()            return int(screenshot_id)

            logger.info(f"✅ Inserted test execution: {test_id} (execution_id: {execution_id})")        

            return execution_id        except pyodbc.Error as e:

                        self.connection.rollback()

        except pyodbc.Error as e:            logger.error(f"Failed to insert screenshot: {e}")

            logger.error(f"❌ Error inserting test execution: {e}")            raise

            self.connection.rollback()        finally:

            return None            cursor.close()

        

    def get_test_execution(self, execution_id: int) -> Optional[Dict]:    def insert_page(

        """        self,

        Retrieve a test execution by execution_id.        execution_id: int,

                page_node_id: str,

        Args:        page_label: str,

            execution_id: The execution ID to retrieve        url: str,

                    title: Optional[str] = None,

        Returns:        x_position: Optional[int] = None,

            Dictionary with execution data or None        y_position: Optional[int] = None,

        """        page_order: Optional[int] = None

        if not self.connection:    ) -> int:

            logger.error("No database connection")        """

            return None        Insert page record

                

        query = """        Args:

        SELECT             execution_id: Foreign key to test execution

            execution_id, test_id, status, execution_time, steps_executed,            page_node_id: Node ID (e.g., "page_1")

            browser_type, viewport_width, viewport_height,            page_label: Page label/description

            agent_output, error_message, metadata_json, executed_at            url: Page URL

        FROM TestExecutions            title: Page title

        WHERE execution_id = ?            x_position: X coordinate in graph

        """            y_position: Y coordinate in graph

                    page_order: Order of page visit

        try:            

            cursor = self.connection.cursor()        Returns:

            cursor.execute(query, (execution_id,))            page_id of the inserted record

            row = cursor.fetchone()        """

                    if not self.connection:

            if row:            raise ConnectionError("Not connected to database")

                return {        

                    'execution_id': row[0],        cursor = self.connection.cursor()

                    'test_id': row[1],        

                    'status': row[2],        try:

                    'execution_time': float(row[3]) if row[3] else None,            query = """

                    'steps_executed': row[4],            INSERT INTO dbo.Pages 

                    'browser_type': row[5],                (execution_id, page_node_id, page_label, url, title, x_position, y_position, page_order)

                    'viewport_width': row[6],            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                    'viewport_height': row[7],            """

                    'agent_output': row[8],            

                    'error_message': row[9],            cursor.execute(

                    'metadata_json': row[10],                query,

                    'executed_at': row[11]                (execution_id, page_node_id, page_label, url, title, x_position, y_position, page_order)

                }            )

            return None            

                        cursor.execute("SELECT @@IDENTITY AS page_id")

        except pyodbc.Error as e:            page_id = cursor.fetchone()[0]

            logger.error(f"❌ Error retrieving test execution: {e}")            

            return None            self.connection.commit()

                logger.info(f"Inserted page: {page_label} (page_id: {page_id})")

    def get_executions_by_status(self, status: str) -> List[Dict]:            

        """            return int(page_id)

        Retrieve all test executions with a specific status.        

                except pyodbc.Error as e:

        Args:            self.connection.rollback()

            status: Status to filter by (success/failed/error/timeout)            logger.error(f"Failed to insert page: {e}")

                        raise

        Returns:        finally:

            List of execution dictionaries            cursor.close()

        """    

        if not self.connection:    def insert_page_element(

            logger.error("No database connection")        self,

            return []        page_id: int,

                element_type: Optional[str] = None,

        query = """        element_label: Optional[str] = None,

        SELECT         element_selector: Optional[str] = None,

            execution_id, test_id, status, execution_time, steps_executed,        element_xpath: Optional[str] = None,

            browser_type, executed_at        element_id_attr: Optional[str] = None,

        FROM TestExecutions        element_class: Optional[str] = None,

        WHERE status = ?        text_content: Optional[str] = None,

        ORDER BY executed_at DESC        **kwargs

        """    ) -> int:

                """

        try:        Insert page element record

            cursor = self.connection.cursor()        

            cursor.execute(query, (status,))        Args:

            rows = cursor.fetchall()            page_id: Foreign key to page

                        element_type: Type of element (button, input, link, etc.)

            return [            element_label: Element label

                {            element_selector: CSS selector

                    'execution_id': row[0],            element_xpath: XPath selector

                    'test_id': row[1],            element_id_attr: HTML id attribute

                    'status': row[2],            element_class: HTML class attribute

                    'execution_time': float(row[3]) if row[3] else None,            text_content: Element text content

                    'steps_executed': row[4],            **kwargs: Additional element attributes

                    'browser_type': row[5],            

                    'executed_at': row[6]        Returns:

                }            element_id of the inserted record

                for row in rows        """

            ]        if not self.connection:

                        raise ConnectionError("Not connected to database")

        except pyodbc.Error as e:        

            logger.error(f"❌ Error retrieving executions by status: {e}")        cursor = self.connection.cursor()

            return []        

            try:

    def get_executions_by_date_range(            query = """

        self,            INSERT INTO dbo.PageElements 

        start_date: datetime,                (page_id, element_type, element_label, element_selector, element_xpath, 

        end_date: datetime                 element_id_attr, element_class, text_content)

    ) -> List[Dict]:            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """            """

        Retrieve test executions within a date range.            

                    cursor.execute(

        Args:                query,

            start_date: Start of date range                (page_id, element_type, element_label, element_selector, element_xpath,

            end_date: End of date range                 element_id_attr, element_class, text_content)

                        )

        Returns:            

            List of execution dictionaries            cursor.execute("SELECT @@IDENTITY AS element_id")

        """            element_id = cursor.fetchone()[0]

        if not self.connection:            

            logger.error("No database connection")            self.connection.commit()

            return []            logger.info(f"Inserted page element: {element_label or element_type} (element_id: {element_id})")

                    

        query = """            return int(element_id)

        SELECT         

            execution_id, test_id, status, execution_time, steps_executed,        except pyodbc.Error as e:

            browser_type, executed_at            self.connection.rollback()

        FROM TestExecutions            logger.error(f"Failed to insert page element: {e}")

        WHERE executed_at BETWEEN ? AND ?            raise

        ORDER BY executed_at DESC        finally:

        """            cursor.close()

            

        try:    def insert_page_edge(

            cursor = self.connection.cursor()        self,

            cursor.execute(query, (start_date, end_date))        execution_id: int,

            rows = cursor.fetchall()        edge_node_id: str,

                    source_page_node_id: str,

            return [        target_page_node_id: str,

                {        edge_label: Optional[str] = None,

                    'execution_id': row[0],        edge_type: str = "navigation",

                    'test_id': row[1],        action_performed: Optional[str] = None

                    'status': row[2],    ) -> int:

                    'execution_time': float(row[3]) if row[3] else None,        """

                    'steps_executed': row[4],        Insert page edge (navigation relationship)

                    'browser_type': row[5],        

                    'executed_at': row[6]        Args:

                }            execution_id: Foreign key to test execution

                for row in rows            edge_node_id: Edge node ID (e.g., "edge_1")

            ]            source_page_node_id: Source page node ID

                        target_page_node_id: Target page node ID

        except pyodbc.Error as e:            edge_label: Edge label/description

            logger.error(f"❌ Error retrieving executions by date range: {e}")            edge_type: Type of edge (navigation, click, etc.)

            return []            action_performed: Action that triggered the edge

                

    def update_execution_status(        Returns:

        self,            edge_id of the inserted record

        execution_id: int,        """

        status: str,        if not self.connection:

        error_message: Optional[str] = None            raise ConnectionError("Not connected to database")

    ) -> bool:        

        """        cursor = self.connection.cursor()

        Update the status of a test execution.        

                try:

        Args:            query = """

            execution_id: Execution ID to update            INSERT INTO dbo.PageEdges 

            status: New status                (execution_id, edge_node_id, source_page_node_id, target_page_node_id, 

            error_message: Optional error message                 edge_label, edge_type, action_performed)

                        VALUES (?, ?, ?, ?, ?, ?, ?)

        Returns:            """

            True if successful, False otherwise            

        """            cursor.execute(

        if not self.connection:                query,

            logger.error("No database connection")                (execution_id, edge_node_id, source_page_node_id, target_page_node_id,

            return False                 edge_label, edge_type, action_performed)

                    )

        query = """            

        UPDATE TestExecutions            cursor.execute("SELECT @@IDENTITY AS edge_id")

        SET status = ?, error_message = ?            edge_id = cursor.fetchone()[0]

        WHERE execution_id = ?            

        """            self.connection.commit()

                    logger.info(f"Inserted page edge: {edge_node_id} (edge_id: {edge_id})")

        try:            

            cursor = self.connection.cursor()            return int(edge_id)

            cursor.execute(query, (status, error_message, execution_id))        

            self.connection.commit()        except pyodbc.Error as e:

            logger.info(f"✅ Updated execution {execution_id} status to {status}")            self.connection.rollback()

            return True            logger.error(f"Failed to insert page edge: {e}")

                        raise

        except pyodbc.Error as e:        finally:

            logger.error(f"❌ Error updating execution status: {e}")            cursor.close()

            self.connection.rollback()    

            return False    def store_playwright_metadata(self, metadata: Dict[str, Any]) -> int:

            """

    def delete_test_execution(self, execution_id: int) -> bool:        Store complete Playwright metadata from JSON

        """        

        Delete a test execution and all related data (cascading delete).        This is the main method that stores all data from the playwright_metadata_output.json

                

        Args:        Args:

            execution_id: Execution ID to delete            metadata: Complete metadata dictionary

                        

        Returns:        Returns:

            True if successful, False otherwise            execution_id of the stored test execution

        """        """

        if not self.connection:        if not self.connection:

            logger.error("No database connection")            raise ConnectionError("Not connected to database")

            return False        

                try:

        query = "DELETE FROM TestExecutions WHERE execution_id = ?"            # Parse executed_at timestamp

                    executed_at = None

        try:            if "executed_at" in metadata:

            cursor = self.connection.cursor()                try:

            cursor.execute(query, (execution_id,))                    executed_at = datetime.fromisoformat(metadata["executed_at"].replace('Z', '+00:00'))

            self.connection.commit()                except:

            logger.info(f"✅ Deleted execution {execution_id} and related data")                    executed_at = datetime.utcnow()

            return True            

                        # 1. Insert test execution

        except pyodbc.Error as e:            execution_id = self.insert_test_execution(

            logger.error(f"❌ Error deleting execution: {e}")                test_id=metadata.get("test_id", "unknown"),

            self.connection.rollback()                status=metadata.get("status", "unknown"),

            return False                execution_time=float(metadata.get("execution_time", 0)),

                    steps_executed=int(metadata.get("steps_executed", 0)),

    # ==================== TestPages Table Operations ====================                agent_output=metadata.get("agent_output", ""),

                    error_message=metadata.get("error_message"),

    def insert_page(                executed_at=executed_at

        self,            )

        execution_id: int,            

        page_node_id: str,            logger.info(f"Created test execution record with ID: {execution_id}")

        label: str,            

        url: Optional[str] = None,            # 2. Insert screenshots

        title: Optional[str] = None,            screenshots = metadata.get("screenshots", [])

        description: Optional[str] = None,            for idx, screenshot_filename in enumerate(screenshots):

        position_x: Optional[float] = None,                self.insert_screenshot(

        position_y: Optional[float] = None,                    execution_id=execution_id,

        elements_json: Optional[str] = None                    filename=screenshot_filename,

    ) -> Optional[int]:                    step_number=idx + 1

        """                )

        Insert a page node record.            

                    # 3. Insert pages

        Args:            pages = metadata.get("pages", [])

            execution_id: Parent execution ID            page_id_map = {}  # Map page_node_id to page_id

            page_node_id: Unique page node identifier            

            label: Page label/name            for idx, page in enumerate(pages):

            url: Page URL                page_metadata = page.get("metadata", {})

            title: Page title                

            description: Page description                page_id = self.insert_page(

            position_x: X position in flow diagram                    execution_id=execution_id,

            position_y: Y position in flow diagram                    page_node_id=page.get("id", f"page_{idx+1}"),

            elements_json: Page elements as JSON string                    page_label=page.get("label", "Unknown Page"),

                                url=page_metadata.get("url", ""),

        Returns:                    title=page_metadata.get("title"),

            page_id if successful, None otherwise                    x_position=page.get("x"),

        """                    y_position=page.get("y"),

        if not self.connection:                    page_order=idx + 1

            logger.error("No database connection")                )

            return None                

                        page_id_map[page.get("id")] = page_id

        query = """                

        INSERT INTO TestPages (                # 4. Insert page elements (key_elements)

            execution_id, page_node_id, label, url, title, description,                key_elements = page_metadata.get("key_elements", [])

            position_x, position_y, elements_json                for element in key_elements:

        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);                    if isinstance(element, dict):

        SELECT SCOPE_IDENTITY() AS page_id;                        self.insert_page_element(

        """                            page_id=page_id,

                                    element_type=element.get("type"),

        try:                            element_label=element.get("label"),

            cursor = self.connection.cursor()                            element_selector=element.get("selector"),

            cursor.execute(                            element_xpath=element.get("xpath"),

                query,                            element_id_attr=element.get("id"),

                (execution_id, page_node_id, label, url, title, description,                            element_class=element.get("class"),

                 position_x, position_y, elements_json)                            text_content=element.get("text")

            )                        )

                        

            result = cursor.fetchone()            # 5. Insert page edges (if present in metadata)

            page_id = int(result[0]) if result else None            edges = metadata.get("edges", [])

                        for edge in edges:

            self.connection.commit()                self.insert_page_edge(

            logger.info(f"✅ Inserted page: {label} (page_id: {page_id})")                    execution_id=execution_id,

            return page_id                    edge_node_id=edge.get("id", ""),

                                source_page_node_id=edge.get("source", ""),

        except pyodbc.Error as e:                    target_page_node_id=edge.get("target", ""),

            logger.error(f"❌ Error inserting page: {e}")                    edge_label=edge.get("label"),

            self.connection.rollback()                    edge_type=edge.get("type", "navigation")

            return None                )

                

    def get_test_pages(self, execution_id: int) -> List[Dict]:            logger.info(f"Successfully stored complete metadata for execution_id: {execution_id}")

        """            return execution_id

        Retrieve all pages for a test execution.        

                except Exception as e:

        Args:            logger.error(f"Failed to store Playwright metadata: {e}")

            execution_id: Execution ID to retrieve pages for            raise

                

        Returns:    def get_test_execution(self, execution_id: int) -> Optional[Dict[str, Any]]:

            List of page dictionaries        """

        """        Retrieve test execution by ID

        if not self.connection:        

            logger.error("No database connection")        Args:

            return []            execution_id: Execution ID

                    

        query = """        Returns:

        SELECT             Dictionary with execution details or None

            page_id, execution_id, page_node_id, label, url, title,        """

            description, position_x, position_y, elements_json        if not self.connection:

        FROM TestPages            raise ConnectionError("Not connected to database")

        WHERE execution_id = ?        

        ORDER BY page_id        cursor = self.connection.cursor()

        """        

                try:

        try:            query = """

            cursor = self.connection.cursor()            SELECT 

            cursor.execute(query, (execution_id,))                execution_id, test_id, status, execution_time, steps_executed,

            rows = cursor.fetchall()                agent_output, error_message, executed_at, created_at

                        FROM dbo.TestExecutions

            return [            WHERE execution_id = ?

                {            """

                    'page_id': row[0],            

                    'execution_id': row[1],            cursor.execute(query, (execution_id,))

                    'page_node_id': row[2],            row = cursor.fetchone()

                    'label': row[3],            

                    'url': row[4],            if not row:

                    'title': row[5],                return None

                    'description': row[6],            

                    'position_x': float(row[7]) if row[7] else None,            return {

                    'position_y': float(row[8]) if row[8] else None,                "execution_id": row[0],

                    'elements_json': row[9]                "test_id": row[1],

                }                "status": row[2],

                for row in rows                "execution_time": float(row[3]),

            ]                "steps_executed": row[4],

                            "agent_output": row[5],

        except pyodbc.Error as e:                "error_message": row[6],

            logger.error(f"❌ Error retrieving pages: {e}")                "executed_at": row[7].isoformat() if row[7] else None,

            return []                "created_at": row[8].isoformat() if row[8] else None

                }

    # ==================== TestEdges Table Operations ====================        

            finally:

    def insert_edge(            cursor.close()

        self,    

        execution_id: int,    def get_execution_pages(self, execution_id: int) -> List[Dict[str, Any]]:

        source_page_id: int,        """

        target_page_id: int,        Get all pages for a test execution

        edge_label: str,        

        edge_type: Optional[str] = None,        Args:

        action_trigger: Optional[str] = None            execution_id: Execution ID

    ) -> Optional[int]:            

        """        Returns:

        Insert a page edge (navigation) record.            List of page dictionaries

                """

        Args:        if not self.connection:

            execution_id: Parent execution ID            raise ConnectionError("Not connected to database")

            source_page_id: Source page ID        

            target_page_id: Target page ID        cursor = self.connection.cursor()

            edge_label: Edge label/description        

            edge_type: Edge type        try:

            action_trigger: Action that triggered navigation            query = """

                        SELECT 

        Returns:                page_id, page_node_id, page_label, url, title,

            edge_id if successful, None otherwise                x_position, y_position, page_order

        """            FROM dbo.Pages

        if not self.connection:            WHERE execution_id = ?

            logger.error("No database connection")            ORDER BY page_order, page_id

            return None            """

                    

        query = """            cursor.execute(query, (execution_id,))

        INSERT INTO TestEdges (            rows = cursor.fetchall()

            execution_id, source_page_id, target_page_id,            

            edge_label, edge_type, action_trigger            pages = []

        ) VALUES (?, ?, ?, ?, ?, ?);            for row in rows:

        SELECT SCOPE_IDENTITY() AS edge_id;                pages.append({

        """                    "page_id": row[0],

                            "page_node_id": row[1],

        try:                    "page_label": row[2],

            cursor = self.connection.cursor()                    "url": row[3],

            cursor.execute(                    "title": row[4],

                query,                    "x_position": row[5],

                (execution_id, source_page_id, target_page_id,                    "y_position": row[6],

                 edge_label, edge_type, action_trigger)                    "page_order": row[7]

            )                })

                        

            result = cursor.fetchone()            return pages

            edge_id = int(result[0]) if result else None        

                    finally:

            self.connection.commit()            cursor.close()

            logger.info(f"✅ Inserted edge: {edge_label} (edge_id: {edge_id})")    

            return edge_id    def get_page_elements(self, page_id: int) -> List[Dict[str, Any]]:

                    """

        except pyodbc.Error as e:        Get all elements for a page

            logger.error(f"❌ Error inserting edge: {e}")        

            self.connection.rollback()        Args:

            return None            page_id: Page ID

                

    def get_test_edges(self, execution_id: int) -> List[Dict]:        Returns:

        """            List of element dictionaries

        Retrieve all edges for a test execution.        """

                if not self.connection:

        Args:            raise ConnectionError("Not connected to database")

            execution_id: Execution ID to retrieve edges for        

                    cursor = self.connection.cursor()

        Returns:        

            List of edge dictionaries        try:

        """            query = """

        if not self.connection:            SELECT 

            logger.error("No database connection")                element_id, element_type, element_label, element_selector,

            return []                element_xpath, element_id_attr, element_class, text_content

                    FROM dbo.PageElements

        query = """            WHERE page_id = ?

        SELECT             ORDER BY element_type, element_label

            edge_id, execution_id, source_page_id, target_page_id,            """

            edge_label, edge_type, action_trigger            

        FROM TestEdges            cursor.execute(query, (page_id,))

        WHERE execution_id = ?            rows = cursor.fetchall()

        ORDER BY edge_id            

        """            elements = []

                    for row in rows:

        try:                elements.append({

            cursor = self.connection.cursor()                    "element_id": row[0],

            cursor.execute(query, (execution_id,))                    "element_type": row[1],

            rows = cursor.fetchall()                    "element_label": row[2],

                                "element_selector": row[3],

            return [                    "element_xpath": row[4],

                {                    "element_id_attr": row[5],

                    'edge_id': row[0],                    "element_class": row[6],

                    'execution_id': row[1],                    "text_content": row[7]

                    'source_page_id': row[2],                })

                    'target_page_id': row[3],            

                    'edge_label': row[4],            return elements

                    'edge_type': row[5],        

                    'action_trigger': row[6]        finally:

                }            cursor.close()

                for row in rows

            ]

            def create_config_from_env() -> AzureSQLConfig:

        except pyodbc.Error as e:    """

            logger.error(f"❌ Error retrieving edges: {e}")    Create Azure SQL config from environment variables

            return []    

        Environment variables:

    # ==================== TestElements Table Operations ====================        AZURE_SQL_SERVER: Server name

            AZURE_SQL_DATABASE: Database name

    def insert_element(        AZURE_SQL_USERNAME: Username

        self,        AZURE_SQL_PASSWORD: Password

        page_id: int,        AZURE_SQL_DRIVER: ODBC Driver (optional)

        element_type: str,        

        element_label: str,    Returns:

        selector: Optional[str] = None,        AzureSQLConfig instance

        xpath: Optional[str] = None,    """

        attributes_json: Optional[str] = None    import os

    ) -> Optional[int]:    

        """    return AzureSQLConfig(

        Insert a page element record.        server=os.getenv("AZURE_SQL_SERVER", ""),

                database=os.getenv("AZURE_SQL_DATABASE", ""),

        Args:        username=os.getenv("AZURE_SQL_USERNAME", ""),

            page_id: Parent page ID        password=os.getenv("AZURE_SQL_PASSWORD", ""),

            element_type: Element type (button/input/link/etc)        driver=os.getenv("AZURE_SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")

            element_label: Element label/description    )

            selector: CSS selector

            xpath: XPath selector

            attributes_json: Element attributes as JSONdef create_config_from_dict(config_dict: Dict[str, Any]) -> AzureSQLConfig:

                """

        Returns:    Create Azure SQL config from dictionary

            element_id if successful, None otherwise    

        """    Args:

        if not self.connection:        config_dict: Dictionary with connection parameters

            logger.error("No database connection")        

            return None    Returns:

                AzureSQLConfig instance

        query = """    """

        INSERT INTO TestElements (    return AzureSQLConfig(

            page_id, element_type, element_label,        server=config_dict.get("server", ""),

            selector, xpath, attributes_json        database=config_dict.get("database", ""),

        ) VALUES (?, ?, ?, ?, ?, ?);        username=config_dict.get("username", ""),

        SELECT SCOPE_IDENTITY() AS element_id;        password=config_dict.get("password", ""),

        """        driver=config_dict.get("driver", "{ODBC Driver 18 for SQL Server}"),

                port=config_dict.get("port", 1433),

        try:        encrypt=config_dict.get("encrypt", True),

            cursor = self.connection.cursor()        trust_server_certificate=config_dict.get("trust_server_certificate", False)

            cursor.execute(    )

                query,
                (page_id, element_type, element_label,
                 selector, xpath, attributes_json)
            )
            
            result = cursor.fetchone()
            element_id = int(result[0]) if result else None
            
            self.connection.commit()
            logger.info(f"✅ Inserted element: {element_label} (element_id: {element_id})")
            return element_id
            
        except pyodbc.Error as e:
            logger.error(f"❌ Error inserting element: {e}")
            self.connection.rollback()
            return None
    
    def get_page_elements(self, page_id: int) -> List[Dict]:
        """
        Retrieve all elements for a page.
        
        Args:
            page_id: Page ID to retrieve elements for
            
        Returns:
            List of element dictionaries
        """
        if not self.connection:
            logger.error("No database connection")
            return []
        
        query = """
        SELECT 
            element_id, page_id, element_type, element_label,
            selector, xpath, attributes_json
        FROM TestElements
        WHERE page_id = ?
        ORDER BY element_id
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (page_id,))
            rows = cursor.fetchall()
            
            return [
                {
                    'element_id': row[0],
                    'page_id': row[1],
                    'element_type': row[2],
                    'element_label': row[3],
                    'selector': row[4],
                    'xpath': row[5],
                    'attributes_json': row[6]
                }
                for row in rows
            ]
            
        except pyodbc.Error as e:
            logger.error(f"❌ Error retrieving elements: {e}")
            return []
    
    # ==================== TestScreenshots Table Operations ====================
    
    def insert_screenshot(
        self,
        execution_id: int,
        filename: str,
        file_path: str,
        step_number: int,
        page_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a screenshot record.
        
        Args:
            execution_id: Parent execution ID
            filename: Screenshot filename
            file_path: Full file path
            step_number: Step number in test execution
            page_id: Associated page ID (optional)
            description: Screenshot description
            
        Returns:
            screenshot_id if successful, None otherwise
        """
        if not self.connection:
            logger.error("No database connection")
            return None
        
        query = """
        INSERT INTO TestScreenshots (
            execution_id, filename, file_path, step_number,
            page_id, description, captured_at
        ) VALUES (?, ?, ?, ?, ?, ?, GETDATE());
        SELECT SCOPE_IDENTITY() AS screenshot_id;
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                query,
                (execution_id, filename, file_path, step_number,
                 page_id, description)
            )
            
            result = cursor.fetchone()
            screenshot_id = int(result[0]) if result else None
            
            self.connection.commit()
            logger.info(f"✅ Inserted screenshot: {filename} (screenshot_id: {screenshot_id})")
            return screenshot_id
            
        except pyodbc.Error as e:
            logger.error(f"❌ Error inserting screenshot: {e}")
            self.connection.rollback()
            return None
    
    def get_test_screenshots(self, execution_id: int) -> List[Dict]:
        """
        Retrieve all screenshots for a test execution.
        
        Args:
            execution_id: Execution ID to retrieve screenshots for
            
        Returns:
            List of screenshot dictionaries
        """
        if not self.connection:
            logger.error("No database connection")
            return []
        
        query = """
        SELECT 
            screenshot_id, execution_id, filename, file_path,
            step_number, page_id, description, captured_at
        FROM TestScreenshots
        WHERE execution_id = ?
        ORDER BY step_number
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (execution_id,))
            rows = cursor.fetchall()
            
            return [
                {
                    'screenshot_id': row[0],
                    'execution_id': row[1],
                    'filename': row[2],
                    'file_path': row[3],
                    'step_number': row[4],
                    'page_id': row[5],
                    'description': row[6],
                    'captured_at': row[7]
                }
                for row in rows
            ]
            
        except pyodbc.Error as e:
            logger.error(f"❌ Error retrieving screenshots: {e}")
            return []
    
    # ==================== Complex Operations ====================
    
    def insert_full_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Insert complete Playwright metadata in a single transaction.
        
        This method handles:
        - Test execution record
        - All pages
        - All edges between pages
        - All elements on pages
        - All screenshots
        
        Args:
            metadata: Complete metadata dictionary from Playwright execution
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.error("No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 1. Insert test execution
            test_id = metadata.get('test_id', 'UNKNOWN')
            status = metadata.get('status', 'unknown')
            execution_time = metadata.get('execution_time', 0.0)
            steps_executed = metadata.get('steps_executed', 0)
            
            execution_id = self.insert_test_execution(
                test_id=test_id,
                status=status,
                execution_time=execution_time,
                steps_executed=steps_executed,
                browser_type=metadata.get('browser_type'),
                viewport_width=metadata.get('viewport', {}).get('width'),
                viewport_height=metadata.get('viewport', {}).get('height'),
                agent_output=metadata.get('agent_output'),
                error_message=metadata.get('error_message'),
                metadata_json=json.dumps(metadata)
            )
            
            if not execution_id:
                logger.error("Failed to insert test execution")
                return False
            
            # 2. Insert screenshots
            screenshots = metadata.get('screenshots', [])
            for idx, screenshot in enumerate(screenshots):
                self.insert_screenshot(
                    execution_id=execution_id,
                    filename=screenshot.get('filename', f'screenshot_{idx}.png'),
                    file_path=screenshot.get('file_path', ''),
                    step_number=idx + 1,
                    description=screenshot.get('description')
                )
            
            # 3. Insert pages and build page_id mapping
            page_id_map = {}  # Maps page_node_id to database page_id
            pages = metadata.get('pages', [])
            
            for page in pages:
                page_node_id = page.get('id', page.get('node_id', ''))
                label = page.get('label', 'Unknown Page')
                
                page_id = self.insert_page(
                    execution_id=execution_id,
                    page_node_id=page_node_id,
                    label=label,
                    url=page.get('url'),
                    title=page.get('title'),
                    description=page.get('description'),
                    position_x=page.get('position', {}).get('x'),
                    position_y=page.get('position', {}).get('y'),
                    elements_json=json.dumps(page.get('elements', []))
                )
                
                if page_id:
                    page_id_map[page_node_id] = page_id
                    
                    # 4. Insert elements for this page
                    elements = page.get('elements', [])
                    for element in elements:
                        self.insert_element(
                            page_id=page_id,
                            element_type=element.get('type', 'unknown'),
                            element_label=element.get('label', 'Unknown Element'),
                            selector=element.get('selector'),
                            xpath=element.get('xpath'),
                            attributes_json=json.dumps(element.get('attributes', {}))
                        )
            
            # 5. Insert edges (using page_id mapping)
            edges = metadata.get('edges', [])
            for edge in edges:
                source_node_id = edge.get('source')
                target_node_id = edge.get('target')
                
                source_page_id = page_id_map.get(source_node_id)
                target_page_id = page_id_map.get(target_node_id)
                
                if source_page_id and target_page_id:
                    self.insert_edge(
                        execution_id=execution_id,
                        source_page_id=source_page_id,
                        target_page_id=target_page_id,
                        edge_label=edge.get('label', 'Navigate'),
                        edge_type=edge.get('type'),
                        action_trigger=edge.get('trigger')
                    )
            
            logger.info(f"✅ Successfully inserted complete metadata for test: {test_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting full metadata: {e}")
            self.connection.rollback()
            return False
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics across all tests.
        
        Returns:
            Dictionary with statistics
        """
        if not self.connection:
            logger.error("No database connection")
            return {}
        
        query = """
        SELECT 
            COUNT(*) as total_executions,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
            AVG(execution_time) as avg_execution_time,
            MAX(execution_time) as max_execution_time,
            MIN(execution_time) as min_execution_time
        FROM TestExecutions
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                return {
                    'total_executions': row[0],
                    'successful': row[1],
                    'failed': row[2],
                    'errors': row[3],
                    'avg_execution_time': float(row[4]) if row[4] else 0.0,
                    'max_execution_time': float(row[5]) if row[5] else 0.0,
                    'min_execution_time': float(row[6]) if row[6] else 0.0,
                    'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0.0
                }
            return {}
            
        except pyodbc.Error as e:
            logger.error(f"❌ Error retrieving statistics: {e}")
            return {}


# ==================== Helper Functions ====================

def create_sample_metadata() -> Dict[str, Any]:
    """Create sample metadata for testing."""
    return {
        "test_id": "TC_001",
        "status": "success",
        "execution_time": 5.5,
        "steps_executed": 10,
        "browser_type": "chromium",
        "viewport": {"width": 1920, "height": 1080},
        "agent_output": "Test completed successfully",
        "pages": [
            {
                "id": "page_1",
                "label": "Home Page",
                "url": "https://example.com",
                "title": "Example Home",
                "description": "Landing page",
                "position": {"x": 100, "y": 100},
                "elements": [
                    {
                        "type": "button",
                        "label": "Login Button",
                        "selector": "#login-btn",
                        "xpath": "//button[@id='login-btn']",
                        "attributes": {"class": "btn btn-primary"}
                    }
                ]
            },
            {
                "id": "page_2",
                "label": "Login Page",
                "url": "https://example.com/login",
                "title": "Login",
                "description": "User login page",
                "position": {"x": 300, "y": 100}
            }
        ],
        "edges": [
            {
                "source": "page_1",
                "target": "page_2",
                "label": "Click Login",
                "type": "navigation",
                "trigger": "button_click"
            }
        ],
        "screenshots": [
            {
                "filename": "step_1.png",
                "file_path": "/screenshots/step_1.png",
                "description": "Home page loaded"
            },
            {
                "filename": "step_2.png",
                "file_path": "/screenshots/step_2.png",
                "description": "Login page"
            }
        ]
    }


if __name__ == "__main__":
    print("Azure SQL Manager module loaded successfully")
    print("Use this module to interact with Azure SQL Database")
    print("\nExample usage:")
    print("  from azure_sql_manager import AzureSQLManager")
    print("  db = AzureSQLManager()")
    print("  db.connect()")
    print("  # Your database operations here")
    print("  db.close()")
