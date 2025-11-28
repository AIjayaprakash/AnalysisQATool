# Azure SQL Database Integration for Playwright Automation

Complete solution for storing Playwright automation test execution metadata in Azure SQL Database.

---

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `azure_sql_schema.sql` | Database schema (tables, views, stored procedures) |
| `azure_sql_manager.py` | Python class for database operations |
| `example_azure_sql_usage.py` | Usage examples and tutorials |
| `integration_api_to_azure_sql.py` | FastAPI integration helpers |
| `requirements-azure-sql.txt` | Python package requirements |
| `AZURE_SQL_SETUP_GUIDE.md` | Complete setup instructions |

---

## 🚀 Quick Start

### 1. Install Requirements

```bash
# Install ODBC Driver (Windows)
# Download from: https://go.microsoft.com/fwlink/?linkid=2249004

# Install Python packages
pip install -r database/requirements-azure-sql.txt
```

### 2. Create Azure SQL Database

```bash
# Using Azure CLI
az sql db create \
  --resource-group your-rg \
  --server your-server \
  --name playwright-db \
  --service-objective S0
```

### 3. Run Database Schema

```bash
# Using sqlcmd
sqlcmd -S your-server.database.windows.net \
  -d playwright-db \
  -U sqladmin \
  -P YourPassword \
  -i database/azure_sql_schema.sql
```

### 4. Configure Connection

Create `.env` file:
```bash
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=playwright-db
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=YourPassword123!
```

### 5. Store Your First Metadata

```python
import json
from database.azure_sql_manager import AzureSQLManager, create_config_from_env

# Load metadata
with open("playwright_metadata_output.json", "r") as f:
    metadata = json.load(f)

# Store to Azure SQL
config = create_config_from_env()
with AzureSQLManager(config) as db:
    execution_id = db.store_playwright_metadata(metadata)
    print(f"✅ Stored with execution_id: {execution_id}")
```

---

## 📊 Database Schema

### Tables

#### 1. **TestExecutions** - Main test execution records
- `execution_id` (PK) - Auto-increment ID
- `test_id` - Test case identifier
- `status` - success/failed/error/timeout
- `execution_time` - Duration in seconds
- `steps_executed` - Number of steps
- `agent_output` - Complete execution log
- `error_message` - Error details if failed
- `executed_at` - Execution timestamp

#### 2. **Screenshots** - Test screenshots
- `screenshot_id` (PK)
- `execution_id` (FK)
- `filename` - Screenshot filename
- `file_path` - Full path
- `step_number` - Step when captured

#### 3. **Pages** - Visited pages (graph nodes)
- `page_id` (PK)
- `execution_id` (FK)
- `page_node_id` - Node ID (e.g., "page_1")
- `page_label` - Display label
- `url` - Page URL
- `title` - Page title
- `x_position`, `y_position` - Graph coordinates
- `page_order` - Visit sequence

#### 4. **PageElements** - Interactive elements on pages
- `element_id` (PK)
- `page_id` (FK)
- `element_type` - button/input/link/etc.
- `element_label` - Display name
- `element_selector` - CSS selector
- `element_xpath` - XPath selector
- `text_content` - Element text
- Various attributes (id, class, name, etc.)

#### 5. **PageEdges** - Navigation relationships (graph edges)
- `edge_id` (PK)
- `execution_id` (FK)
- `edge_node_id` - Edge ID (e.g., "edge_1")
- `source_page_node_id` - From page
- `target_page_node_id` - To page
- `edge_label` - Description
- `edge_type` - navigation/click/etc.

### Views

- `vw_TestExecutionSummary` - Complete execution overview
- `vw_PageDetails` - Pages with element counts

### Stored Procedures

- `sp_GetTestExecutionByTestId` - Get executions by test ID
- `sp_GetPagesForExecution` - Get all pages for execution
- `sp_GetPageElements` - Get elements for a page

---

## 💻 Usage Examples

### Store Metadata from JSON

```python
from database.azure_sql_manager import AzureSQLManager, AzureSQLConfig
import json

config = AzureSQLConfig(
    server="your-server.database.windows.net",
    database="playwright-db",
    username="sqladmin",
    password="YourPassword"
)

# Load and store
with open("playwright_metadata_output.json", "r") as f:
    metadata = json.load(f)

with AzureSQLManager(config) as db:
    execution_id = db.store_playwright_metadata(metadata)
    print(f"Stored: {execution_id}")
```

### Manual Insert Components

```python
with AzureSQLManager(config) as db:
    # Insert execution
    execution_id = db.insert_test_execution(
        test_id="TC_001",
        status="success",
        execution_time=5.2,
        steps_executed=10,
        agent_output="Complete log..."
    )
    
    # Insert page
    page_id = db.insert_page(
        execution_id=execution_id,
        page_node_id="page_1",
        page_label="Login Page",
        url="https://example.com/login",
        title="Login"
    )
    
    # Insert element
    element_id = db.insert_page_element(
        page_id=page_id,
        element_type="button",
        element_label="Login Button",
        element_selector="button#login"
    )
```

### Query Data

```python
with AzureSQLManager(config) as db:
    # Get execution
    execution = db.get_test_execution(execution_id=1)
    print(f"Test: {execution['test_id']}")
    print(f"Status: {execution['status']}")
    
    # Get pages
    pages = db.get_execution_pages(execution_id=1)
    for page in pages:
        print(f"Page: {page['page_label']} - {page['url']}")
        
        # Get elements
        elements = db.get_page_elements(page['page_id'])
        for elem in elements:
            print(f"  - {elem['element_type']}: {elem['element_label']}")
```

---

## 🔗 FastAPI Integration

### Add to Existing Endpoint

```python
# In llmops_api.py
from database.integration_api_to_azure_sql import store_to_azure_sql

@app.post("/execute-from-excel")
async def execute_playwright_from_excel(...):
    # ... existing code ...
    
    # Store to Azure SQL
    try:
        execution_id = store_to_azure_sql(full_response)
        if execution_id:
            full_response["azure_execution_id"] = execution_id
            logger.info(f"Stored to Azure SQL: {execution_id}")
    except Exception as e:
        logger.error(f"Azure SQL storage failed: {e}")
    
    return full_response
```

### Background Storage (Async)

```python
from fastapi import BackgroundTasks
from database.integration_api_to_azure_sql import store_to_azure_sql

async def store_background(execution_result: dict):
    try:
        execution_id = store_to_azure_sql(execution_result)
        logger.info(f"Background storage: {execution_id}")
    except Exception as e:
        logger.error(f"Storage failed: {e}")

@app.post("/execute-from-excel")
async def execute_playwright_from_excel(
    background_tasks: BackgroundTasks,
    ...
):
    # ... existing code ...
    
    # Add background task
    background_tasks.add_task(store_background, full_response)
    
    return full_response
```

---

## 📈 Useful Queries

### Get All Test Executions

```sql
SELECT * FROM vw_TestExecutionSummary 
ORDER BY executed_at DESC;
```

### Success Rate

```sql
SELECT 
    status,
    COUNT(*) as count,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
FROM dbo.TestExecutions
GROUP BY status;
```

### Most Visited Pages

```sql
SELECT 
    url,
    title,
    COUNT(*) as visit_count
FROM dbo.Pages
GROUP BY url, title
ORDER BY visit_count DESC;
```

### Failed Tests with Errors

```sql
SELECT 
    test_id,
    error_message,
    executed_at
FROM dbo.TestExecutions
WHERE status = 'failed'
ORDER BY executed_at DESC;
```

### Execution Duration Trends

```sql
SELECT 
    CAST(executed_at AS DATE) as date,
    AVG(execution_time) as avg_time,
    MIN(execution_time) as min_time,
    MAX(execution_time) as max_time,
    COUNT(*) as test_count
FROM dbo.TestExecutions
GROUP BY CAST(executed_at AS DATE)
ORDER BY date DESC;
```

---

## 🔐 Security Recommendations

1. **Use Environment Variables** - Never hardcode credentials
2. **Azure AD Authentication** - More secure than SQL auth
3. **Firewall Rules** - Restrict to necessary IPs
4. **Managed Identity** - Use when running on Azure
5. **Encrypt Connections** - Always use `encrypt=True`
6. **Regular Backups** - Enable automated backups
7. **Audit Logs** - Monitor database access

---

## 🛠️ Troubleshooting

### ODBC Driver Not Found
```bash
# Windows: Download and install
https://go.microsoft.com/fwlink/?linkid=2249004

# Linux:
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

# macOS:
brew install msodbcsql18
```

### Connection Timeout
- Check firewall rules in Azure Portal
- Add your IP to allowed list
- Verify server name includes `.database.windows.net`

### Login Failed
- Verify username/password
- Check database exists
- Ensure user has permissions

### SSL Certificate Error
```python
config = AzureSQLConfig(
    ...
    trust_server_certificate=True  # Add this
)
```

---

## 📚 Additional Resources

- [Setup Guide](AZURE_SQL_SETUP_GUIDE.md) - Complete setup instructions
- [Example Usage](example_azure_sql_usage.py) - 5 detailed examples
- [API Integration](integration_api_to_azure_sql.py) - FastAPI integration
- [Azure SQL Docs](https://docs.microsoft.com/en-us/azure/azure-sql/)

---

## 🎯 Features

- ✅ Complete database schema with relationships
- ✅ Automatic metadata storage from JSON
- ✅ Manual component insertion
- ✅ Query helpers and utilities
- ✅ FastAPI integration
- ✅ Background task support
- ✅ Environment-based configuration
- ✅ Connection pooling support
- ✅ Comprehensive error handling
- ✅ Views and stored procedures
- ✅ Transaction support

---

## 📝 Example Metadata Structure

Your `playwright_metadata_output.json` should have this structure:

```json
{
  "test_id": "TC_001",
  "status": "success",
  "execution_time": 5.5,
  "steps_executed": 10,
  "agent_output": "...",
  "screenshots": ["screenshot1.png"],
  "error_message": null,
  "executed_at": "2025-11-27T10:00:00",
  "pages": [
    {
      "id": "page_1",
      "label": "Login Page",
      "x": 100,
      "y": 100,
      "metadata": {
        "url": "https://example.com",
        "title": "Login",
        "key_elements": [
          {
            "type": "input",
            "label": "Username",
            "selector": "input#username"
          }
        ]
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "page_1",
      "target": "page_2",
      "label": "Navigate"
    }
  ]
}
```

---

## ✅ Checklist

Before you start:
- [ ] Azure SQL Database created
- [ ] ODBC Driver installed
- [ ] Python packages installed
- [ ] Database schema created
- [ ] Firewall rules configured
- [ ] Configuration file/environment variables set
- [ ] Connection tested

---

**Ready to store your Playwright automation data!** 🚀

For detailed setup instructions, see [AZURE_SQL_SETUP_GUIDE.md](AZURE_SQL_SETUP_GUIDE.md)
