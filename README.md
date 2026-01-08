# 🚆 Railway Departures Scraper
This project fetches live train departure data from the iRail API and stores it in an Azure SQL database using an Azure Function written in Python. I will focus on Leuven as departure station.

## 🛠️ Project Approach
### 1. Local Setup
1. Clone the repository
   ``` bash
   git clone git@github.com:kristinnuyens/railway-scraper-cloud.git
   ```
2. Create and activate a virtual environment
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
### 2. Azure Setup
- I set up the SQL Server + Database (iraildb-server / iRailDB) for the Function App to store the scraped iRail data; creation of a table `departures` was done via the SQL Query Editor in Azure web
  ```bash
  CREATE TABLE departures (
    id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    vehicle VARCHAR(MAX) NULL,
    train_number VARCHAR(MAX) NULL,
    train_type VARCHAR(MAX) NULL,
    destination VARCHAR(MAX) NULL,
    departure_time DATETIME NULL,
    platform VARCHAR(MAX) NULL,
    delay_seconds INT NULL,
    canceled BIT NULL,
    fetched_at DATETIME NULL,
    departure_station NVARCHAR(100) NOT NULL
   );
   ```
- A Storage Account (irailscraperproject9bff) was automatically created by Azure as a runtime requirement for the Function App
- I deployed the Function App resource(irail-scraper-project)
  ![Function App Deployed](<assets/Screenshot 2026-01-06 at 14.09.02.png>)
- Then I created the Python function locally in VSCode to fetch data from the iRail API and insert it into the SQL database in VSCode (as I did not get the option via the web) and linked it to the Function App
   ![No option to create function in Azure web](<assets/Screenshot 2026-01-06 at 16.44.28.png>)

### 3. VSCode Setup
- Installed Azure Functions & Azure Resources extensions
- Installed required Python packages
  ```bash
  pip install azure-functions requests pyodbc
  ```
- Used Homebrew to install `ODBC Driver 18 for SQL Server`

### 4. Fetch Data from iRail API
I defined a Python HTTP-triggered Azure function in VSCode (see reason above) and confirmed it worked with 
```bash
func start
```
![Function alive!](<assets/Screenshot 2026-01-06 at 14.08.16.png>)

### 5. Azure SQL Database Connection
1. Connected using `pyodbc` and ODBC Driver 18
2. Configured Azure SQL firewall to allow the outgoing IP seen by Azure; later discovered an additional intermediate outbound IP (ISP-level, Telenet) that also needed firewall access
3. Set up `local.settings.json` file containing the credential and connection info

### 6. Azure Function Setup
1. Updated Python http-triggered Azure function (`fetch_leuven_departures`) in VSCode to fetch departures from iRail API (`https://api.irail.be/liveboard/`)
   ![Fetched API data](<assets/Screenshot 2026-01-06 at 14.17.02.png>)
2. Then updated the function to fetch the first 10 rows of data and add them to the database; extracted specific departure information (vehicle, train number, type, departure_station, destination, departure time, platform, delay, cancellation)
   ![Test rows inserted in Azure DB](<assets/Screenshot 2026-01-06 at 16.10.45.png>) 
   Confirmed the rows were added to the database in Azure
   ![Confirmed in Azure DB](<assets/Screenshot 2026-01-06 at 17.35.57.png>)
3. Next day I started with updating the function to first fetch current first 10 rows to add them to the database (before pulling all data); code was updated to also remove old irrelevant data from the database; confirmed that data in SQL database was updated
   ![Inserted new/update records in Azure DB](<assets/Screenshot 2026-01-07 at 09.55.07.png>)
4. Updated function to fetch departures in the next 2 hours
   
   ![Inserted upcoming 2 hours departures](<assets/Screenshot 2026-01-07 at 15.55.06.png>)

   Verified in the SQL Database; reran to see if indeed it kept on updating to the newer departures while removing old records
5. Deployed to Azure, but function would not show up in function app; installed azure-CLI via homebrew; ensured requirements.txt was complete and pushed to git; force redeployed my function app via terminal to make it show
   ```bash
   func azure functionapp publish iRailDB-scraper --python --force
   ```
   ![Function finally showing up in Function App on Azure web](<assets/Screenshot 2026-01-08 at 10.08.38.png>)
   Added logging to the function as I keep on returning errors; needed to add credentials to environment variables in function app:
   | Variable     | Purpose             |
   | ------------ | ------------------- |
   | SQL_SERVER   | SQL Server hostname |
   | SQL_DATABASE | Database name       |
   | SQL_USER     | Username            |
   | SQL_PASSWORD | Password            |
   Another IP address added to the firewall; test/run successful!
   ![Test/Run successful](<assets/Screenshot 2026-01-08 at 11.15.57.png>)
6. Updated data in the Azure DB!
   ![Azure DB with updated records](<assets/Screenshot 2026-01-08 at 11.16.34.png>)

## 🔗 Function URL
This URL triggers the function to execute and fetch and insert live data into the SQL Database:
https://iraildb-scraper-h9ffbea2gzene5e5.swedencentral-01.azurewebsites.net/api/fetch_leuven_departures

## ✅ Project Status (Must-Have Submission Checklist)

- ✅ Deployed Azure Function App (HTTP endpoint)
- ✅ Azure SQL Database with live `departures` table
- ✅ Function tested successfully from Azure portal
- ✅ Environment variables configured in App Settings
- ✅ Screenshots added: Function test run, SQL Database
- ✅ GitHub repo with source code and README

## 📄 References
* [iRail API Documentation](https://api.irail.be/)

## 🧑‍💻 Contributors

Solo project:

- Kristin Nuyens

## ⏰ Timeline

5 working days
