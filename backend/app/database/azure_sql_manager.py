"""
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
