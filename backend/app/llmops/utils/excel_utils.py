"""Excel utilities for reading and writing test cases"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..models import TestCase, ExecutionResult


class ExcelReader:
    """Read test cases from Excel files"""
    
    def __init__(self, file_path: str, sheet_name: str = "Sheet1"):
        """
        Initialize Excel reader
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to read from
        """
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self._df: Optional[pd.DataFrame] = None
    
    def read(self) -> pd.DataFrame:
        """Read Excel file and return DataFrame"""
        if self._df is None:
            self._df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        return self._df
    
    def get_test_cases(self, 
                       test_id_col: str = "Test ID",
                       module_col: str = "Module",
                       functionality_col: str = "Functionality",
                       description_col: str = "Description",
                       steps_col: str = "Steps",
                       expected_col: str = "Expected Result",
                       priority_col: str = "Priority") -> List[TestCase]:
        """
        Extract test cases from Excel
        
        Args:
            test_id_col: Column name for test ID
            module_col: Column name for module
            functionality_col: Column name for functionality
            description_col: Column name for test description
            steps_col: Column name for test steps
            expected_col: Column name for expected result
            priority_col: Column name for priority
        
        Returns:
            List of TestCase objects
        """
        df = self.read()
        test_cases = []
        
        for _, row in df.iterrows():
            test_case = TestCase(
                test_id=str(row.get(test_id_col, "")),
                module=str(row.get(module_col, "")),
                functionality=str(row.get(functionality_col, "")),
                description=str(row.get(description_col, "")),
                steps=str(row.get(steps_col, "")) if pd.notna(row.get(steps_col)) else None,
                expected_result=str(row.get(expected_col, "")) if pd.notna(row.get(expected_col)) else None,
                priority=str(row.get(priority_col, "Medium"))
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def get_test_case_by_id(self, test_id: str, **kwargs) -> Optional[TestCase]:
        """
        Get a single test case by ID
        
        Args:
            test_id: Test case ID to find
            **kwargs: Column name mappings (same as get_test_cases)
        
        Returns:
            TestCase object or None if not found
        """
        test_cases = self.get_test_cases(**kwargs)
        for tc in test_cases:
            if tc.test_id == test_id:
                return tc
        return None


class ExcelWriter:
    """Write test execution results to Excel files"""
    
    def __init__(self, file_path: str):
        """
        Initialize Excel writer
        
        Args:
            file_path: Path to output Excel file
        """
        self.file_path = Path(file_path)
    
    def write_results(self, results: List[ExecutionResult], sheet_name: str = "Results"):
        """
        Write execution results to Excel
        
        Args:
            results: List of ExecutionResult objects
            sheet_name: Name of sheet to write to
        """
        data = []
        for result in results:
            data.append({
                "Test ID": result.test_case.test_id,
                "Module": result.test_case.module,
                "Functionality": result.test_case.functionality,
                "Description": result.test_case.description,
                "Status": result.status.value,
                "Execution Time (s)": round(result.execution_time, 2),
                "Error Message": result.error_message or "",
                "Executed At": result.executed_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Screenshots": ", ".join(result.screenshots) if result.screenshots else ""
            })
        
        df = pd.DataFrame(data)
        
        # Create directory if doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to Excel
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def append_result(self, result: ExecutionResult, sheet_name: str = "Results"):
        """
        Append a single result to existing Excel file
        
        Args:
            result: ExecutionResult object
            sheet_name: Name of sheet to append to
        """
        try:
            # Try to read existing file
            existing_df = pd.read_excel(self.file_path, sheet_name=sheet_name)
        except FileNotFoundError:
            # File doesn't exist, write as new
            self.write_results([result], sheet_name)
            return
        
        # Append new result
        new_data = {
            "Test ID": result.test_case.test_id,
            "Module": result.test_case.module,
            "Functionality": result.test_case.functionality,
            "Description": result.test_case.description,
            "Status": result.status.value,
            "Execution Time (s)": round(result.execution_time, 2),
            "Error Message": result.error_message or "",
            "Executed At": result.executed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Screenshots": ", ".join(result.screenshots) if result.screenshots else ""
        }
        
        new_df = pd.concat([existing_df, pd.DataFrame([new_data])], ignore_index=True)
        
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            new_df.to_excel(writer, sheet_name=sheet_name, index=False)
