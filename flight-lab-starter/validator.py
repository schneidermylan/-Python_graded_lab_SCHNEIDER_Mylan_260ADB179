import re
from datetime import datetime
import math
def load_airports(path: str) -> set[str]:
    airports = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            airports.add(stripped)
    return airports
def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"
    stripped_fields = [f.strip() for f in fields]
    for f in stripped_fields:
        if not f:
            return "MISSING_FIELD"  
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped_fields
    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"
    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
    def parse_dt(dt_s: str):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", dt_s):
            return None
        try:
            return datetime.strptime(dt_s, "%Y-%m-%d %H:%M")
        except ValueError:
            return None
    dep_dt = parse_dt(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"
    arr_dt = parse_dt(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"
    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
        
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"
        
    return None

def to_record(fields: list[str]) -> dict:
    s = [f.strip() for f in fields]
    return {
        "flight_id": s[0],
        "origin": s[1],
        "destination": s[2],
        "departure_datetime": s[3],
        "arrival_datetime": s[4],
        "price": float(s[5])
    }
