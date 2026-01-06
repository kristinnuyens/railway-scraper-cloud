# 🚆 Railway Departures Scraper

This project fetches live train departure data from the iRail API and stores it in an Azure SQL database using an Azure Function written in Python.

## 🛠️ Project Setup

### 1. Azure Setup
- We set up the SQL Server + Database (iraildb-server / iRailDB) for the Function App to store the scraped iRail data
- We created a Storage Account (irailscraperproject9bff) as part of the Function App runtime requirement
- We deployed the Function App (irail-scraper-project)
  ![alt text](<assets/Screenshot 2026-01-06 at 14.09.02.png>)
- Then we created the Python function in VSCode to fetch data from the iRail API and insert it into the SQL database in VSCode (as I did not get the option via the web)
   ![alt text](<assets/Screenshot 2026-01-06 at 16.44.28.png>)

### 2. Environment Setup
- Installed Azure Functions & Azure Resources VSCode extensions
- Installed required Python packages
  ```bash
  pip install azure-functions requests pyodbc
  ```
- Used Homebrew to install `ODBC Driver 18 for SQL Server`

### 3. Local Settings
1. Before connecting to the database, tested the Azure Function locally
    ```bash
    func start
    ```
    ![alt text](<assets/Screenshot 2026-01-06 at 14.08.16.png>)    

2. Create a `local.settings.json` file containing the environment variables:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SQL_SERVER": "iraildb-server.database.windows.net,1433",
    "SQL_DATABASE": "iRailDB",
    "SQL_USER": "sqladmin",
    "SQL_PASSWORD": "YOUR_PASSWORD"
  }
}
```

### 4. Fetch Data from iRail API

* Endpoint: `https://api.irail.be/liveboard/`
* Station used: Leuven
* JSON response parsed to extract departure information (vehicle, train number, type, destination, departure time, platform, delay, cancellation).

*Screenshot placeholder: `assets/api_response.png`*

---

### 4. Azure SQL Database Connection

* Connected using `pyodbc` and ODBC Driver 18.
* Azure SQL firewall configured to allow the outgoing IP seen by Azure.
* Sample code snippet for connection:

```python
import os
import pyodbc

server = os.environ["SQL_SERVER"]
database = os.environ["SQL_DATABASE"]
username = os.environ["SQL_USER"]
password = os.environ["SQL_PASSWORD"]
driver = "{ODBC Driver 18 for SQL Server}"

with pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
) as conn:
    cursor = conn.cursor()
    # Insert data here
```

*Screenshot placeholder: `assets/sql_connection.png`*

---

### 5. Azure Function Setup

* Defined a Python HTTP-triggered Azure Function:

  ```bash
  func start
  ```
* Route: `/api/fetch_leuven_departures`
* Anonymous authentication for local testing.

*Screenshot placeholder: `assets/azure_func_local.png`*

---

### 6. Current Status

* ✅ Successfully fetched API data locally.
* ✅ Prepared data insertion into SQL database.
* ⚠️ Azure SQL connection requires correct firewall IP.
* Next steps: expand data collection, handle multiple stations, deploy to Azure.

---

### 7. Next Steps / To Do

* Extend to fetch multiple stations.
* Add logging and error handling.
* Deploy the Azure Function to the cloud.
* Add automated testing for API response and database inserts.

---

### 📸 Screenshots

> Insert relevant screenshots in the `assets/` folder and reference them in sections above.

---

### 📄 References

* [iRail API Documentation](https://api.irail.be/)
* [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server)

---

```

---

I can also make a **version with colorful emojis/icons for each step and small badges** (like Python version, Azure Functions version, SQL Server) so it looks extra professional and GitHub-ready.  

Do you want me to make that fancier version next?
```
