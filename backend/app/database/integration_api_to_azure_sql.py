""""""

API Integration Module for Azure SQL DatabaseIntegration: Store Playwright Metadata to Azure SQL from API Response



This module provides integration between FastAPI endpoints and Azure SQL DatabaseThis module integrates with the existing FastAPI endpoint to automatically

for storing Playwright test execution metadata.store Playwright execution results to Azure SQL Database.

"""

Features:

- Background task support for non-blocking storageimport json

- Error handling and loggingimport os

- Environment-based configurationfrom typing import Dict, Any, Optional

- Automatic metadata extraction and storagefrom datetime import datetime

import logging

Author: Generated for SeleniumMCPFlow Project

Date: 2024from database.azure_sql_manager import (

"""    AzureSQLManager,

    AzureSQLConfig,

import os    create_config_from_env

import json)

import logging

from typing import Optional, Dict, Anylogger = logging.getLogger(__name__)

from datetime import datetime



from .azure_sql_manager import AzureSQLManagerclass PlaywrightMetadataStorage:

    """

# Configure logging    Handles storage of Playwright metadata to Azure SQL Database

logging.basicConfig(    """

    level=logging.INFO,    

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'    def __init__(self, config: Optional[AzureSQLConfig] = None):

)        """

logger = logging.getLogger(__name__)        Initialize storage handler

        

        Args:

async def store_playwright_metadata_to_azure(            config: Azure SQL configuration (defaults to environment variables)

    response: Dict[str, Any],        """

    db_config: Optional[Dict] = None        self.config = config or create_config_from_env()

):    

    """    def store_execution_result(

    Store Playwright execution metadata to Azure SQL Database.        self,

            execution_result: Dict[str, Any],

    This function is designed to be called as a FastAPI background task,        auto_commit: bool = True

    ensuring it doesn't block the API response.    ) -> Optional[int]:

            """

    Args:        Store execution result from API response

        response: PlaywrightExecutionResponse as dictionary containing:        

            - test_id: Unique test identifier        Args:

            - status: Execution status            execution_result: The execution result dictionary from API

            - execution_time: Total execution time            auto_commit: Whether to commit automatically

            - steps_executed: Number of steps            

            - agent_output: Complete agent output        Returns:

            - metadata: Parsed metadata with pages, edges, elements            execution_id if successful, None otherwise

            - screenshots: List of screenshot info        """

        db_config: Optional database configuration override        try:

                    with AzureSQLManager(self.config) as db_manager:

    Returns:                execution_id = db_manager.store_playwright_metadata(execution_result)

        None (logs success/failure)                

                        logger.info(

    Example:                    f"Successfully stored execution result to Azure SQL",

        # In FastAPI endpoint:                    extra={"execution_id": execution_id, "test_id": execution_result.get("test_id")}

        @app.post("/execute-from-excel")                )

        async def execute_endpoint(background_tasks: BackgroundTasks, ...):                

            # ... execute test ...                return execution_id

                    

            # Add background task to store results        except Exception as e:

            background_tasks.add_task(            logger.error(

                store_playwright_metadata_to_azure,                f"Failed to store execution result to Azure SQL: {e}",

                response.dict()                extra={"test_id": execution_result.get("test_id")},

            )                exc_info=True

                        )

            return response            return None

    """    

    # Check if Azure SQL storage is enabled    def store_from_json_file(self, json_file_path: str) -> Optional[int]:

    if not os.getenv("AZURE_SQL_ENABLED", "false").lower() == "true":        """

        logger.info("Azure SQL storage is disabled. Skipping storage.")        Load and store metadata from JSON file

        return        

            Args:

    db = None            json_file_path: Path to JSON file

    try:            

        # Initialize database manager        Returns:

        db = AzureSQLManager(db_config)            execution_id if successful, None otherwise

                """

        # Connect to database        try:

        if not db.connect():            with open(json_file_path, 'r', encoding='utf-8') as f:

            logger.error("Failed to connect to Azure SQL Database")                metadata = json.load(f)

            return            

                    return self.store_execution_result(metadata)

        # Extract metadata from response        

        metadata = extract_metadata_from_response(response)        except Exception as e:

                    logger.error(f"Failed to load/store from JSON file: {e}", exc_info=True)

        if not metadata:            return None

            logger.error("Failed to extract metadata from response")

            return

        def store_to_azure_sql(

        # Store complete metadata in transaction    execution_result: Dict[str, Any],

        success = db.insert_full_metadata(metadata)    config: Optional[AzureSQLConfig] = None

        ) -> Optional[int]:

        if success:    """

            logger.info(f"✅ Successfully stored metadata for test: {metadata.get('test_id')}")    Quick function to store execution result to Azure SQL

        else:    

            logger.error(f"❌ Failed to store metadata for test: {metadata.get('test_id')}")    Args:

                    execution_result: Execution result dictionary

    except Exception as e:        config: Optional Azure SQL configuration

        logger.error(f"❌ Error storing metadata to Azure SQL: {e}", exc_info=True)        

            Returns:

    finally:        execution_id if successful, None otherwise

        # Always close the connection    """

        if db and db.connection:    storage = PlaywrightMetadataStorage(config)

            db.close()    return storage.store_execution_result(execution_result)





def extract_metadata_from_response(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:# ==================== FastAPI Integration ====================

    """

    Extract and format metadata from API response for database storage.def add_azure_sql_storage_to_api():

        """

    Args:    Example integration with FastAPI endpoint

        response: API response dictionary    

            Add this to your llmops_api.py after the /execute-from-excel endpoint

    Returns:    """

        Formatted metadata dictionary or None if extraction fails    

    """    example_code = '''

    try:# In llmops_api.py, add this import at the top:

        # Base execution infofrom database.integration_api_to_azure_sql import store_to_azure_sql

        metadata = {

            'test_id': response.get('test_id', 'UNKNOWN'),# Then modify the /execute-from-excel endpoint:

            'status': response.get('status', 'unknown'),

            'execution_time': response.get('execution_time', 0.0),@app.post("/execute-from-excel")

            'steps_executed': response.get('steps_executed', 0),async def execute_playwright_from_excel(

            'browser_type': response.get('browser_type', 'chromium'),    file: UploadFile = File(...),

            'agent_output': response.get('agent_output', ''),    sheet_name: str = Form("Sheet1"),

            'error_message': response.get('error_message'),    test_id: Optional[str] = Form(None),

        }    browser_type: str = Form("chromium"),

            headless: bool = Form(False),

        # Extract viewport if present    max_iterations: int = Form(20)

        if 'viewport' in response:):

            metadata['viewport'] = response['viewport']    """Execute Playwright automation from Excel test case"""

            

        # Extract parsed metadata    try:

        parsed_metadata = response.get('metadata', {})        # ... existing code to execute automation ...

                

        # Extract pages        # After getting full_response:

        if 'nodes' in parsed_metadata:        full_response = {

            metadata['pages'] = parsed_metadata['nodes']            "test_id": selected_test.get("ID", test_id or "unknown"),

        elif 'pages' in parsed_metadata:            "status": "success" if status == "success" else "failed",

            metadata['pages'] = parsed_metadata['pages']            "execution_time": execution_time,

        else:            "steps_executed": tool_calls,

            metadata['pages'] = []            "agent_output": str(result),

                    "screenshots": screenshots,

        # Extract edges            "error_message": error_message,

        if 'edges' in parsed_metadata:            "executed_at": datetime.now().isoformat(),

            metadata['edges'] = parsed_metadata['edges']            "pages": pages,

        else:            "edges": edges

            metadata['edges'] = []        }

                

        # Extract screenshots        # ✅ NEW: Store to Azure SQL Database

        if 'screenshots' in response:        try:

            metadata['screenshots'] = response['screenshots']            execution_id = store_to_azure_sql(full_response)

        elif 'screenshots' in parsed_metadata:            if execution_id:

            metadata['screenshots'] = parsed_metadata['screenshots']                logger.info(f"Stored execution to Azure SQL with ID: {execution_id}")

        else:                # Optionally add execution_id to response

            metadata['screenshots'] = []                full_response["azure_execution_id"] = execution_id

                    else:

        logger.info(f"Extracted metadata: {metadata['test_id']} - "                logger.warning("Failed to store execution to Azure SQL")

                   f"{len(metadata.get('pages', []))} pages, "        except Exception as e:

                   f"{len(metadata.get('edges', []))} edges, "            logger.error(f"Azure SQL storage error: {e}")

                   f"{len(metadata.get('screenshots', []))} screenshots")            # Continue even if storage fails

                

        return metadata        return full_response

            

    except Exception as e:    except Exception as e:

        logger.error(f"Error extracting metadata: {e}", exc_info=True)        logger.error(f"Error in execute-from-excel: {e}")

        return None        raise HTTPException(status_code=500, detail=str(e))

'''

    

def store_metadata_sync(    print(example_code)

    metadata: Dict[str, Any],    return example_code

    db_config: Optional[Dict] = None

) -> bool:

    """# ==================== Background Task Integration ====================

    Synchronous version of metadata storage (for non-async contexts).

    def create_background_storage_task():

    Args:    """

        metadata: Complete metadata dictionary    Example using FastAPI BackgroundTasks for async storage

        db_config: Optional database configuration    """

            

    Returns:    example_code = '''

        True if successful, False otherwisefrom fastapi import BackgroundTasks

    """from database.integration_api_to_azure_sql import store_to_azure_sql

    # Check if Azure SQL storage is enabled

    if not os.getenv("AZURE_SQL_ENABLED", "false").lower() == "true":async def store_to_azure_background(execution_result: dict):

        logger.info("Azure SQL storage is disabled. Skipping storage.")    """Background task to store to Azure SQL"""

        return False    try:

            execution_id = store_to_azure_sql(execution_result)

    db = None        logger.info(f"Background storage completed with ID: {execution_id}")

    try:    except Exception as e:

        # Initialize and connect        logger.error(f"Background storage failed: {e}")

        db = AzureSQLManager(db_config)

        @app.post("/execute-from-excel")

        if not db.connect():async def execute_playwright_from_excel(

            logger.error("Failed to connect to Azure SQL Database")    background_tasks: BackgroundTasks,

            return False    file: UploadFile = File(...),

            # ... other parameters

        # Store metadata):

        success = db.insert_full_metadata(metadata)    """Execute Playwright automation from Excel test case"""

            

        if success:    # ... existing code ...

            logger.info(f"✅ Successfully stored metadata for test: {metadata.get('test_id')}")    

            return True    # Add background task for Azure SQL storage

        else:    background_tasks.add_task(store_to_azure_background, full_response)

            logger.error(f"❌ Failed to store metadata for test: {metadata.get('test_id')}")    

            return False    return full_response

            '''

    except Exception as e:    

        logger.error(f"❌ Error storing metadata to Azure SQL: {e}", exc_info=True)    print(example_code)

        return False    return example_code

        

    finally:

        if db and db.connection:# ==================== Batch Storage ====================

            db.close()

def store_multiple_executions(

    execution_results: list[Dict[str, Any]],

def get_execution_by_test_id(    config: Optional[AzureSQLConfig] = None

    test_id: str,) -> list[Optional[int]]:

    db_config: Optional[Dict] = None    """

) -> Optional[Dict[str, Any]]:    Store multiple execution results in batch

    """    

    Retrieve execution metadata by test_id.    Args:

            execution_results: List of execution result dictionaries

    Args:        config: Optional Azure SQL configuration

        test_id: Test identifier to search for        

        db_config: Optional database configuration    Returns:

                List of execution_ids (None for failed items)

    Returns:    """

        Complete metadata dictionary or None    storage = PlaywrightMetadataStorage(config)

    """    execution_ids = []

    db = None    

    try:    for result in execution_results:

        db = AzureSQLManager(db_config)        execution_id = storage.store_execution_result(result)

                execution_ids.append(execution_id)

        if not db.connect():    

            logger.error("Failed to connect to Azure SQL Database")    return execution_ids

            return None

        

        # Find execution by test_id# ==================== Utility Functions ====================

        query = "SELECT execution_id FROM TestExecutions WHERE test_id = ?"

        cursor = db.connection.cursor()def verify_azure_sql_connection(config: Optional[AzureSQLConfig] = None) -> bool:

        cursor.execute(query, (test_id,))    """

        row = cursor.fetchone()    Verify Azure SQL connection

            

        if not row:    Args:

            logger.warning(f"No execution found for test_id: {test_id}")        config: Optional Azure SQL configuration

            return None        

            Returns:

        execution_id = row[0]        True if connection successful, False otherwise

            """

        # Get complete metadata    try:

        execution = db.get_test_execution(execution_id)        test_config = config or create_config_from_env()

        if execution:        

            execution['pages'] = db.get_test_pages(execution_id)        with AzureSQLManager(test_config) as db_manager:

            execution['edges'] = db.get_test_edges(execution_id)            cursor = db_manager.connection.cursor()

            execution['screenshots'] = db.get_test_screenshots(execution_id)            cursor.execute("SELECT 1")

                        result = cursor.fetchone()

            # Get elements for each page            

            for page in execution['pages']:            if result and result[0] == 1:

                page['elements'] = db.get_page_elements(page['page_id'])                logger.info("✅ Azure SQL connection verified successfully")

                        return True

        return execution            else:

                        logger.error("❌ Azure SQL connection verification failed")

    except Exception as e:                return False

        logger.error(f"Error retrieving execution: {e}", exc_info=True)    

        return None    except Exception as e:

                logger.error(f"❌ Azure SQL connection failed: {e}")

    finally:        return False

        if db and db.connection:

            db.close()

def get_execution_summary(execution_id: int, config: Optional[AzureSQLConfig] = None) -> Optional[Dict]:

    """

def get_recent_executions(    Get execution summary from Azure SQL

    limit: int = 10,    

    status: Optional[str] = None,    Args:

    db_config: Optional[Dict] = None        execution_id: Execution ID to retrieve

) -> list:        config: Optional Azure SQL configuration

    """        

    Get recent test executions.    Returns:

            Execution summary dictionary or None

    Args:    """

        limit: Maximum number of executions to return    try:

        status: Optional status filter (success/failed/error/timeout)        test_config = config or create_config_from_env()

        db_config: Optional database configuration        

                with AzureSQLManager(test_config) as db_manager:

    Returns:            execution = db_manager.get_test_execution(execution_id)

        List of execution dictionaries            

    """            if execution:

    db = None                pages = db_manager.get_execution_pages(execution_id)

    try:                execution["pages"] = pages

        db = AzureSQLManager(db_config)                

                        # Get elements for each page

        if not db.connect():                for page in execution["pages"]:

            logger.error("Failed to connect to Azure SQL Database")                    elements = db_manager.get_page_elements(page["page_id"])

            return []                    page["elements"] = elements

                        

        if status:                return execution

            executions = db.get_executions_by_status(status)            

        else:            return None

            query = """    

            SELECT TOP (?)     except Exception as e:

                execution_id, test_id, status, execution_time,         logger.error(f"Failed to get execution summary: {e}")

                steps_executed, browser_type, executed_at        return None

            FROM TestExecutions

            ORDER BY executed_at DESC

            """# ==================== Example Usage ====================

            cursor = db.connection.cursor()

            cursor.execute(query, (limit,))def example_usage():

            rows = cursor.fetchall()    """Example usage of the integration"""

                

            executions = [    print("=" * 80)

                {    print("Example: Integration with API")

                    'execution_id': row[0],    print("=" * 80)

                    'test_id': row[1],    

                    'status': row[2],    # Example 1: Store from API response

                    'execution_time': float(row[3]) if row[3] else None,    print("\n1. Store execution result from API response:")

                    'steps_executed': row[4],    print("""

                    'browser_type': row[5],from database.integration_api_to_azure_sql import store_to_azure_sql

                    'executed_at': row[6]

                }execution_result = {

                for row in rows    "test_id": "TC_001",

            ]    "status": "success",

            "execution_time": 5.2,

        return executions[:limit]    "steps_executed": 10,

            "agent_output": "...",

    except Exception as e:    "screenshots": ["screenshot1.png"],

        logger.error(f"Error retrieving recent executions: {e}", exc_info=True)    "pages": [{"id": "page_1", "label": "Login", ...}]

        return []}

        

    finally:execution_id = store_to_azure_sql(execution_result)

        if db and db.connection:print(f"Stored with execution_id: {execution_id}")

            db.close()""")

    

    # Example 2: Verify connection

# ==================== FastAPI Integration Example ====================    print("\n2. Verify Azure SQL connection:")

    print("""

"""from database.integration_api_to_azure_sql import verify_azure_sql_connection

Example integration with FastAPI endpoint:

if verify_azure_sql_connection():

from fastapi import FastAPI, BackgroundTasks    print("✅ Connection OK")

from .database.integration_api_to_azure_sql import store_playwright_metadata_to_azureelse:

    print("❌ Connection failed")

app = FastAPI()""")

    

@app.post("/execute-from-excel")    # Example 3: Get execution summary

async def execute_from_excel(    print("\n3. Retrieve execution summary:")

    background_tasks: BackgroundTasks,    print("""

    # ... other parameters ...from database.integration_api_to_azure_sql import get_execution_summary

):

    # ... execute test and get response ...summary = get_execution_summary(execution_id=1)

    print(f"Test: {summary['test_id']}")

    # Add background task to store in Azure SQLprint(f"Status: {summary['status']}")

    if os.getenv("AZURE_SQL_ENABLED", "false").lower() == "true":print(f"Pages: {len(summary['pages'])}")

        background_tasks.add_task(""")

            store_playwright_metadata_to_azure,    

            response.dict()    print("\n" + "=" * 80 + "\n")

        )

    

    return responseif __name__ == "__main__":

    example_usage()


@app.get("/executions/recent")
async def get_recent_test_executions(limit: int = 10):
    '''Get recent test executions from Azure SQL'''
    executions = get_recent_executions(limit=limit)
    return {"executions": executions}


@app.get("/executions/{test_id}")
async def get_execution_details(test_id: str):
    '''Get complete execution details by test_id'''
    execution = get_execution_by_test_id(test_id)
    if execution:
        return execution
    else:
        return {"error": "Execution not found"}
"""


if __name__ == "__main__":
    print("Azure SQL Integration Module loaded successfully")
    print("\nThis module provides:")
    print("  - store_playwright_metadata_to_azure(): Background task for FastAPI")
    print("  - store_metadata_sync(): Synchronous storage")
    print("  - get_execution_by_test_id(): Retrieve by test ID")
    print("  - get_recent_executions(): Get recent test runs")
    print("\nSee module docstring for FastAPI integration example")
