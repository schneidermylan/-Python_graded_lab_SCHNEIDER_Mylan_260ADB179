from datetime import datetime

def validate_flight(flight: dict) -> bool:
    required_keys = {"flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price"}
    if not isinstance(flight, dict):
        return False
    if not required_keys.issubset(flight.keys()):
        return False

    if not isinstance(flight["flight_id"], str) or not flight["flight_id"].strip():
        return False
    if not isinstance(flight["origin"], str) or len(flight["origin"]) != 3 or not flight["origin"].isupper():
        return False
    if not isinstance(flight["destination"], str) or len(flight["destination"]) != 3 or not flight["destination"].isupper():
        return False

    for dt_key in ["departure_datetime", "arrival_datetime"]:
        if not isinstance(flight[dt_key], str):
            return False
        try:
            datetime.strptime(flight[dt_key], "%Y-%m-%d %H:%M")
        except ValueError:
            return False

    if flight["departure_datetime"] >= flight["arrival_datetime"]:
        return False

    if isinstance(flight["price"], bool) or not isinstance(flight["price"], (int, float)):
        return False
    if flight["price"] < 0:
        return False

    return True
