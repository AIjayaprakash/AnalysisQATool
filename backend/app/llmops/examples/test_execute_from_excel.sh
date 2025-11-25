#!/bin/bash

# Bash script example for testing /execute-from-excel endpoint

API_URL="http://localhost:8000/execute-from-excel"
EXCEL_FILE="test_cases.xlsx"

echo "=================================================="
echo "Execute From Excel - Bash/cURL Examples"
echo "=================================================="

# Example 1: Basic usage (first test case, chromium)
echo -e "\n📌 Example 1: Basic Usage"
curl -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -H "Accept: application/json" \
     | jq '.'

# Example 2: Specific test case with Edge browser
echo -e "\n📌 Example 2: Specific Test Case with Edge Browser"
curl -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -F "sheet_name=Sheet1" \
     -F "test_id=TC_LOGIN_001" \
     -F "browser_type=edge" \
     -F "headless=false" \
     -F "max_iterations=10" \
     -H "Accept: application/json" \
     | jq '.'

# Example 3: Firefox headless mode
echo -e "\n📌 Example 3: Firefox Headless Mode"
curl -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -F "sheet_name=Sheet1" \
     -F "browser_type=firefox" \
     -F "headless=true" \
     -F "max_iterations=15" \
     -H "Accept: application/json" \
     | jq '.pages | length as $page_count | .edges | length as $edge_count | {pages: $page_count, edges: $edge_count}'

# Example 4: Save response to file
echo -e "\n📌 Example 4: Save Response to File"
curl -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -F "browser_type=chromium" \
     -F "headless=false" \
     -H "Accept: application/json" \
     -o automation_results.json

echo "✅ Response saved to automation_results.json"

# Example 5: Check only status
echo -e "\n📌 Example 5: Check Status (count pages and edges)"
curl -s -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -F "browser_type=edge" \
     | jq '{
         total_pages: (.pages | length),
         total_edges: (.edges | length),
         page_urls: [.pages[].metadata.url]
       }'

# Example 6: With error handling
echo -e "\n📌 Example 6: With Error Handling"
HTTP_CODE=$(curl -s -o response.json -w "%{http_code}" \
     -X POST "$API_URL" \
     -F "file=@$EXCEL_FILE" \
     -F "test_id=TC_001" \
     -F "browser_type=edge")

if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ Success! HTTP $HTTP_CODE"
    cat response.json | jq '.pages | length as $count | "Pages extracted: \($count)"'
else
    echo "❌ Error! HTTP $HTTP_CODE"
    cat response.json | jq '.'
fi

echo -e "\n=================================================="
echo "All examples completed!"
echo "=================================================="
