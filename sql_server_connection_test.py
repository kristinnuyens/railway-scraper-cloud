import pyodbc
import os

# Use the same environment variables as in your function app
server = os.environ.get("SQL_SERVER", "iraildb-server.database.windows.net,1433")
database = os.environ.get("SQL_DATABASE", "iRailDB")
username = os.environ.get("SQL_USER", "sqladmin")
password = os.environ.get("SQL_PASSWORD", "zygten-xuxjyq-sEpzo0")
driver = "{ODBC Driver 18 for SQL Server}"

try:
    conn = pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes",
        timeout=5
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1 AS test")
    row = cursor.fetchone()
    print("Connection successful, test query result:", row[0])
    conn.close()
except Exception as e:
    print("Connection failed:", e)
