import azure.functions as func
import requests
import pyodbc
from datetime import datetime, timedelta
import os
import time
import pytz
import logging
import json

# Initialize the FunctionApp
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="fetch_leuven_departures", methods=["GET"])
def fetch_leuven_departures(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("Function started")

    # Database connection
    server = os.environ.get("SQL_SERVER")
    if not server:
        return func.HttpResponse("SQL_SERVER environment variable missing", status_code=500)
    if "," not in server:
        server = f"{server},1433"

    database = os.environ.get("SQL_DATABASE")
    username = os.environ.get("SQL_USER")
    password = os.environ.get("SQL_PASSWORD")
    driver = "{ODBC Driver 18 for SQL Server}"

    try:
        conn = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;",
            timeout=5
        )
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return func.HttpResponse("Database connection failed", status_code=500)

    cursor = conn.cursor()

    # Clear old departures
    try:
        cursor.execute("DELETE FROM departures;")
        conn.commit()
    except Exception as e:
        logging.error(f"Failed to clear old departures: {e}")
        conn.close()
        return func.HttpResponse("Failed to clear old departures", status_code=500)

    # Fetch data from API
    url = "https://api.irail.be/v1/liveboard/"
    station = "Leuven"
    params = {"station": station, "format": "json", "lang": "en"}
    rows = []

    tz = pytz.timezone("Europe/Brussels")
    now_utc = datetime.utcnow()
    now_local = pytz.utc.localize(now_utc).astimezone(tz)
    window_end = now_local + timedelta(hours=2)

    for minutes_ahead in range(0, 120, 15):
        future_time = now_local + timedelta(minutes=minutes_ahead)
        params["date"] = future_time.strftime("%d%m%y")
        params["time"] = future_time.strftime("%H%M")

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed for {params}: {e}")
            continue

        departures = response.json().get("departures", {}).get("departure", [])
        for d in departures:
            dt = datetime.utcfromtimestamp(int(d["time"]))
            dt_local = pytz.utc.localize(dt).astimezone(tz)
            if now_local <= dt_local <= window_end:
                rows.append((
                    station,
                    d.get("vehicle"),
                    d.get("vehicleinfo", {}).get("number"),
                    d.get("vehicleinfo", {}).get("type"),
                    d.get("station"),
                    dt_local,
                    d.get("platform"),
                    int(d.get("delay", 0)),
                    int(d.get("canceled", 0)),
                    now_local
                ))

        time.sleep(0.25)

    # Deduplicate
    seen = set()
    deduped_rows = []
    for r in rows:
        key = (r[1], r[2], r[5])
        if key not in seen:
            deduped_rows.append(r)
            seen.add(key)

    # Insert into DB
    if deduped_rows:
        try:
            cursor.executemany("""
                INSERT INTO departures
                (departure_station, vehicle, train_number, train_type, destination,
                 departure_time, platform, delay_seconds, canceled, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, deduped_rows)
            conn.commit()
        except Exception as e:
            logging.error(f"DB insert failed: {e}")
            conn.close()
            return func.HttpResponse("Failed to insert departures", status_code=500)

    conn.close()
    logging.info(f"Inserted {len(deduped_rows)} departures")
    return func.HttpResponse(
    json.dumps({
        "status": "success",
        "inserted_rows": len(deduped_rows)
    }),
    status_code=200,
    mimetype="application/json"
)
