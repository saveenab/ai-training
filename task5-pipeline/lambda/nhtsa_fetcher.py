import logging
import requests 
from datetime import datetime

logger = logging.getLogger(__name__)

NHTSA_BASE_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle"

TARGET_VEHICLES =[
    {"make": "Toyota",       "model": "Camry"},
    {"make": "Toyota",       "model": "RAV4"},
    {"make": "Toyota",       "model": "Highlander"},
    {"make": "Ford",         "model": "F-150"},
    {"make": "Ford",         "model": "Explorer"},
    {"make": "Ford",         "model": "Escape"},
    {"make": "Honda",        "model": "Civic"},
    {"make": "Honda",        "model": "CR-V"},
    {"make": "Honda",        "model": "Accord"},
    {"make": "Chevrolet",    "model": "Silverado"},
    {"make": "Chevrolet",    "model": "Equinox"},
    {"make": "Tesla",        "model": "Model 3"},
    {"make": "Tesla",        "model": "Model Y"},
    {"make": "BMW",          "model": "3 Series"},
    {"make": "Hyundai",      "model": "Tucson"},
    {"make": "Hyundai",      "model": "Elantra"},
    {"make": "Kia",          "model": "Sportage"},
    {"make": "Nissan",       "model": "Altima"},
    {"make": "Nissan",       "model": "Rogue"},
]

TARGET_YEARS = [2020,2021,2022,2023,2024]

def fetch_recalls(make: str, model: str, year: int) -> list:
    url = f"{NHTSA_BASE_URL}?make={make}&model={model}&modelYear={year}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout — {make} {model} {year}, skipping")
        return []

    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP error — {make} {model} {year}: {e}, skipping")
        return []

    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed — {make} {model} {year}: {e}, skipping")
        return []
    
def parse_recall(raw: dict, make: str, model: str) -> dict:
    recall_id = raw.get("NHTSACampaignNumber", "").strip()

    if not recall_id:
        logger.warning("Skipping record with no campaign number")
        return None

    raw_date = raw.get("ReportReceivedDate", "")
    report_date = None
    if raw_date:
        try:
            # NHTSA returns dates as "15/06/2023" (DD/MM/YYYY)
            report_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            logger.warning(f"Could not parse date: {raw_date}")

    return {
        "recall_id":   recall_id,
        "title":       raw.get("Component", "").strip() or "Untitled",
        "category":    raw.get("Component", "").strip(),
        "component":   raw.get("Component", "").strip(),
        "description": raw.get("Summary", "").strip(),
        "consequence": raw.get("Consequence", "").strip(),
        "remedy":      raw.get("Remedy", "").strip(),
        "report_date": report_date,
        "make":        make,
        "model":       model,
        "year":        raw.get("ModelYear"),
    }


def fetch_all_recalls() -> list:
    all_records = []

    for vehicle in TARGET_VEHICLES:
        make  = vehicle["make"]
        model = vehicle["model"]
        for year in TARGET_YEARS:
            raw_records = fetch_recalls(make, model, year)
            for raw in raw_records:
                parsed = parse_recall(raw, make, model)
                if parsed:
                    all_records.append(parsed)

    logger.info(f"Total recalls fetched: {len(all_records)}")
    return all_records

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    print("\n=== Testing full fetch: all vehicles + years ===")
    all_records = fetch_all_recalls()
    print(f"\nTotal records fetched: {len(all_records)}")

    if all_records:
        print("\nFirst record:")
        print(json.dumps(all_records[0], indent=2))
        print("\nLast record:")
        print(json.dumps(all_records[-1], indent=2))