@echo off
REM PowerShell script for Windows to test /execute-from-excel endpoint

set API_URL=http://localhost:8000/execute-from-excel
set EXCEL_FILE=test_cases.xlsx

echo ==================================================
echo Execute From Excel - PowerShell/Windows Examples
echo ==================================================

REM Example 1: Basic usage
echo.
echo Example 1: Basic Usage (First Test Case, Chromium)
curl -X POST "%API_URL%" ^
     -F "file=@%EXCEL_FILE%" ^
     -H "Accept: application/json"

REM Example 2: Specific test case with Edge browser
echo.
echo Example 2: Specific Test Case with Edge Browser
curl -X POST "%API_URL%" ^
     -F "file=@%EXCEL_FILE%" ^
     -F "sheet_name=Sheet1" ^
     -F "test_id=TC_LOGIN_001" ^
     -F "browser_type=edge" ^
     -F "headless=false" ^
     -F "max_iterations=10" ^
     -H "Accept: application/json"

REM Example 3: Firefox headless
echo.
echo Example 3: Firefox Headless Mode
curl -X POST "%API_URL%" ^
     -F "file=@%EXCEL_FILE%" ^
     -F "browser_type=firefox" ^
     -F "headless=true" ^
     -F "max_iterations=15" ^
     -H "Accept: application/json"

REM Example 4: Save to file
echo.
echo Example 4: Save Response to File
curl -X POST "%API_URL%" ^
     -F "file=@%EXCEL_FILE%" ^
     -F "browser_type=edge" ^
     -F "headless=false" ^
     -o automation_results.json

echo Response saved to automation_results.json

echo.
echo ==================================================
echo All examples completed!
echo ==================================================
pause
