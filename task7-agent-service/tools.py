import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

def decode_vin(vin: str) -> dict:
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = {item["Variable"]: item["Value"] for item in data.get("Results", [])}
        make = results.get("Make", "").strip()
        model = results.get("Model", "").strip()
        year = results.get("Model Year", "").strip()
        if not make or not model or not year:
            return {"error": f"Could not decode VIN: {vin}"}
        return {"make": make, "model": model, "year": year, "vin": vin}
    except Exception as e:
        return {"error": str(e)}

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", ""),
        sslmode="require"
    )

def search_recalls(make: str, model: str, year: str) -> list:
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT recall_id, component, description, consequence, remedy, report_date
                FROM recalls
                WHERE LOWER(make) = LOWER(%s)
                AND LOWER(model) = LOWER(%s)
                AND year = %s
                ORDER BY report_date DESC
            """, (make, model, year))
            records = cur.fetchall()
            conn.close()
            if not records:
                return []
            return [dict(r) for r in records]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    print("Testing decode_vin...")
    result = decode_vin("1FTFW1ET5DFC10312")
    print(result)
    print("\nTesting search_recalls...")
    recalls = search_recalls("Ford", "F-150", "2020")
    print(f"Found {len(recalls)} recalls")
    if recalls:
        print(recalls[0])
