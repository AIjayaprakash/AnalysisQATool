"""
Database package for Azure SQL integration.

This package provides:
- AzureSQLManager: Database manager for CRUD operations
- Integration functions for storing Playwright metadata
- Example usage scripts and tests
"""

from .azure_sql_manager import AzureSQLManager

__all__ = ['AzureSQLManager']
