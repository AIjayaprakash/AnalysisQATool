# Azure SQL Database Setup Guide

## 📋 Prerequisites

1. **Azure SQL Database** - Create a database in Azure Portal
2. **ODBC Driver** - Install Microsoft ODBC Driver for SQL Server
3. **Python Packages** - Install required Python packages

---

## 🔧 Step 1: Install ODBC Driver

### Windows
Download and install from Microsoft:
- [ODBC Driver 18 for SQL Server](https://go.microsoft.com/fwlink/?linkid=2249004)
- Or [ODBC Driver 17 for SQL Server](https://go.microsoft.com/fwlink/?linkid=2187214)

### Linux (Ubuntu/Debian)
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18
```

---

## 📦 Step 2: Install Python Packages

```bash
cd database
pip install -r requirements-azure-sql.txt
```

Or install individually:
```bash
pip install pyodbc==5.0.1
pip install python-dotenv==1.0.0
```

---

## 🗄️ Step 3: Create Azure SQL Database

### Option A: Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **SQL Database**
3. Note down:
   - Server name (e.g., `your-server.database.windows.net`)
   - Database name
   - Admin username and password

### Option B: Azure CLI
```bash
# Create resource group
az group create --name playwright-rg --location eastus

# Create SQL server
az sql server create \
  --name your-server-name \
  --resource-group playwright-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password YourPassword123!

# Create database
az sql db create \
  --resource-group playwright-rg \
  --server your-server-name \
  --name playwright-db \
  --service-objective S0
```

---

## 🔐 Step 4: Configure Firewall Rules

Allow your IP address to access the database:

### Azure Portal
1. Go to your SQL Server
2. Settings → Networking
3. Add your client IP address
4. Check "Allow Azure services and resources to access this server"

### Azure CLI
```bash
# Add your IP
az sql server firewall-rule create \
  --resource-group playwright-rg \
  --server your-server-name \
  --name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP

# Allow Azure services
az sql server firewall-rule create \
  --resource-group playwright-rg \
  --server your-server-name \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

## 📊 Step 5: Create Database Schema

### Option A: Using Azure Portal Query Editor
1. Go to your database in Azure Portal
2. Click "Query editor"
3. Login with SQL authentication
4. Copy and paste the contents of `azure_sql_schema.sql`
5. Click "Run"

### Option B: Using SQL Server Management Studio (SSMS)
1. Connect to your Azure SQL Server
2. Open `azure_sql_schema.sql`
3. Execute the script

### Option C: Using Command Line (sqlcmd)
```bash
sqlcmd -S your-server.database.windows.net -d your-database -U sqladmin -P YourPassword -i azure_sql_schema.sql
```

### Option D: Using Python
```python
from database.azure_sql_manager import AzureSQLManager, AzureSQLConfig

config = AzureSQLConfig(
    server="your-server.database.windows.net",
    database="your-database",
    username="sqladmin",
    password="YourPassword"
)

with AzureSQLManager(config) as db:
    with open("azure_sql_schema.sql", "r") as f:
        schema_sql = f.read()
    
    cursor = db.connection.cursor()
    cursor.execute(schema_sql)
    db.connection.commit()
```

---

## ⚙️ Step 6: Configure Application

### Option A: Environment Variables (Recommended)

Create a `.env` file:
```bash
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=playwright-db
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=YourPassword123!
AZURE_SQL_DRIVER={ODBC Driver 18 for SQL Server}
```

Load in your application:
```python
from dotenv import load_dotenv
from database.azure_sql_manager import create_config_from_env, AzureSQLManager

load_dotenv()

config = create_config_from_env()
with AzureSQLManager(config) as db:
    # Use database
    pass
```

### Option B: Configuration File

Create `config/database.json`:
```json
{
  "server": "your-server.database.windows.net",
  "database": "playwright-db",
  "username": "sqladmin",
  "password": "YourPassword123!",
  "driver": "{ODBC Driver 18 for SQL Server}",
  "port": 1433,
  "encrypt": true,
  "trust_server_certificate": false
}
```

Load in your application:
```python
import json
from database.azure_sql_manager import create_config_from_dict, AzureSQLManager

with open("config/database.json", "r") as f:
    config_dict = json.load(f)

config = create_config_from_dict(config_dict)
with AzureSQLManager(config) as db:
    # Use database
    pass
```

### Option C: Direct Configuration
```python
from database.azure_sql_manager import AzureSQLConfig, AzureSQLManager

config = AzureSQLConfig(
    server="your-server.database.windows.net",
    database="playwright-db",
    username="sqladmin",
    password="YourPassword123!",
    driver="{ODBC Driver 18 for SQL Server}"
)

with AzureSQLManager(config) as db:
    # Use database
    pass
```

---

## 🚀 Step 7: Test Connection

```python
from database.azure_sql_manager import AzureSQLManager, AzureSQLConfig

config = AzureSQLConfig(
    server="your-server.database.windows.net",
    database="playwright-db",
    username="sqladmin",
    password="YourPassword123!"
)

try:
    with AzureSQLManager(config) as db:
        cursor = db.connection.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"SQL Server Version: {version}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## 📝 Step 8: Store Your First Metadata

```python
import json
from database.azure_sql_manager import AzureSQLManager, AzureSQLConfig

# Load your metadata
with open("playwright_metadata_output.json", "r") as f:
    metadata = json.load(f)

# Configure database
config = AzureSQLConfig(
    server="your-server.database.windows.net",
    database="playwright-db",
    username="sqladmin",
    password="YourPassword123!"
)

# Store metadata
with AzureSQLManager(config) as db:
    execution_id = db.store_playwright_metadata(metadata)
    print(f"✅ Stored with execution_id: {execution_id}")
```

---

## 🔍 Step 9: Query Your Data

### Query Test Executions
```python
with AzureSQLManager(config) as db:
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM vw_TestExecutionSummary ORDER BY executed_at DESC")
    
    for row in cursor.fetchall():
        print(f"Test: {row.test_id}, Status: {row.status}, Pages: {row.total_pages}")
```

### Query Specific Execution
```python
with AzureSQLManager(config) as db:
    execution = db.get_test_execution(execution_id=1)
    print(f"Test: {execution['test_id']}")
    print(f"Status: {execution['status']}")
    
    pages = db.get_execution_pages(execution_id=1)
    for page in pages:
        print(f"Page: {page['page_label']} - {page['url']}")
```

---

## 🛠️ Troubleshooting

### Issue 1: "ODBC Driver not found"
**Solution**: Install the Microsoft ODBC Driver (see Step 1)

### Issue 2: "Login failed for user"
**Solution**: 
- Verify username/password
- Check if user has access to the database
- Verify firewall rules (Step 4)

### Issue 3: "Cannot open server requested by login"
**Solution**:
- Check server name (should include `.database.windows.net`)
- Verify database exists
- Check firewall rules

### Issue 4: "SSL Provider: The certificate chain was issued by an authority that is not trusted"
**Solution**: Set `trust_server_certificate=True` in config:
```python
config = AzureSQLConfig(
    server="...",
    database="...",
    username="...",
    password="...",
    trust_server_certificate=True  # Add this
)
```

### Issue 5: "Connection timeout"
**Solution**:
- Check network connectivity
- Verify firewall rules
- Try increasing connection timeout in connection string

---

## 📚 Useful SQL Queries

### Get all test executions
```sql
SELECT * FROM vw_TestExecutionSummary 
ORDER BY executed_at DESC;
```

### Get success rate
```sql
SELECT 
    status,
    COUNT(*) as count,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
FROM dbo.TestExecutions
GROUP BY status;
```

### Get most visited pages
```sql
SELECT 
    url,
    title,
    COUNT(*) as visit_count
FROM dbo.Pages
GROUP BY url, title
ORDER BY visit_count DESC;
```

### Get executions with errors
```sql
SELECT 
    test_id,
    error_message,
    executed_at
FROM dbo.TestExecutions
WHERE status = 'failed'
ORDER BY executed_at DESC;
```

---

## 🔐 Security Best Practices

1. **Never commit passwords** - Use environment variables or Azure Key Vault
2. **Use Azure AD authentication** - More secure than SQL authentication
3. **Restrict firewall rules** - Only allow necessary IP addresses
4. **Use managed identity** - When running on Azure (App Service, Functions, etc.)
5. **Encrypt connections** - Always use `encrypt=True`
6. **Regular backups** - Enable automated backups in Azure Portal
7. **Monitor access** - Use Azure SQL Database auditing

---

## 📖 Additional Resources

- [Azure SQL Documentation](https://docs.microsoft.com/en-us/azure/azure-sql/)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [SQL Server ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/)
- [Azure SQL Security Best Practices](https://docs.microsoft.com/en-us/azure/azure-sql/database/security-best-practice)

---

## ✅ Checklist

- [ ] ODBC Driver installed
- [ ] Python packages installed
- [ ] Azure SQL Database created
- [ ] Firewall rules configured
- [ ] Database schema created
- [ ] Connection tested
- [ ] Configuration file/environment variables set
- [ ] First metadata stored successfully

---

**You're all set!** 🎉

Your Playwright automation metadata is now being stored in Azure SQL Database!
