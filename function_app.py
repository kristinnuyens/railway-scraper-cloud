import azure.functions as func
import requests
import pyodbc
from datetime import datetime
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="fetch_leuven_departures", methods=["GET"])
def fetch_leuven_departures(req: func.HttpRequest) -> func.HttpResponse:

    # fetch Leuven departures from iRail API
    url = "https://api.irail.be/liveboard/"
    params = {"station": "Leuven", "format": "json", "lang": "en"}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    departures = data.get("departures", {}).get("departure", [])

    # prepare data for SQL
    rows = []
    for d in departures[:10]:  # first 10 rows for testing
        ts = int(d.get("time"))
        dt = datetime.utcfromtimestamp(ts)
        row = {
            "vehicle": d.get("vehicle"),
            "train_number": d.get("vehicleinfo", {}).get("number"),
            "train_type": d.get("vehicleinfo", {}).get("type"),
            "destination": d.get("station"),
            "departure_time": dt,
            "platform": d.get("platform"),
            "delay_seconds": int(d.get("delay", 0)),
            "canceled": int(d.get("canceled", 0)),
            "fetched_at": datetime.utcnow()
        }
        rows.append(row)

    # connect to Azure SQL
    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    username = os.environ["SQL_USER"]
    password = os.environ["SQL_PASSWORD"]
    driver = "{ODBC Driver 18 for SQL Server}"

    with pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    ) as conn:
        cursor = conn.cursor()
        for r in rows:
            cursor.execute("""
                INSERT INTO leuven_departures
                (vehicle, train_number, train_type, destination, departure_time, platform, delay_seconds, canceled, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, r["vehicle"], r["train_number"], r["train_type"], r["destination"], r["departure_time"], r["platform"], r["delay_seconds"], r["canceled"], r["fetched_at"])
        conn.commit()

    return func.HttpResponse(f"Inserted {len(rows)} departures.")