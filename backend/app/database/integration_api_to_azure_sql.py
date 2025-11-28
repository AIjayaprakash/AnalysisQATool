"""
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
