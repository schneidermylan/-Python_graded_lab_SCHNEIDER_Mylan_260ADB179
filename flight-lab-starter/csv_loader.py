import csv
import json
from validator import validate_flight

def load_flights(csv_path: str) -> list[dict]:
    flights = []
    seen_ids = set()
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "price" in row:
                    try:
                        row["price"] = float(row["price"]) if "." in row["price"] else int(row["price"])
                    except ValueError:
                        continue
                
                if validate_flight(row):
                    flight_id = row["flight_id"]
                    if flight_id not in seen_ids:
                        seen_ids.add(flight_id)
                        flights.append(row)
    except Exception:
        pass
        
    return flights

def save_db(flights: list[dict], db_path: str = "db.json"):
    with open(db_path, mode='w', encoding='utf-8') as f:
        json.dump(flights, f, indent=4, ensure_ascii=False)
