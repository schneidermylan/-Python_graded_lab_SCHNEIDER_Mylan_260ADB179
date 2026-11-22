from datetime import datetime

def run_query(db: list[dict], query: dict) -> dict:
    allowed_keys = {
        "flight_id", "origin", "destination", 
        "departure_datetime", "arrival_datetime", 
        "price", "min_price", "sort_by", "order", "limit"
    }
    if not isinstance(query, dict):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
        
    for k, v in query.items():
        if k not in allowed_keys:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}
        if k in ["flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "sort_by", "order"]:
            if not isinstance(v, str):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}
        if k in ["price", "min_price", "limit"]:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}
                
    if "limit" in query and query["limit"] < 0:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
        
    if "order" in query and "sort_by" not in query:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
        
    if "order" in query and query["order"] not in ["asc", "desc"]:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
    for dk in ["departure_datetime", "arrival_datetime"]:
        if dk in query:
            try:
                datetime.strptime(query[dk], "%Y-%m-%d %H:%M")
            except ValueError:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}
    matches = []
    for flight in db:
        match = True
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            match = False
        if "origin" in query and flight["origin"] != query["origin"]:
            match = False
        if "destination" in query and flight["destination"] != query["destination"]:
            match = False
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            match = False
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            match = False
        if "price" in query and flight["price"] > query["price"]:
            match = False
        if "min_price" in query and flight["price"] < query["min_price"]:
            match = False    
        if match:
            matches.append(flight)
    if "sort_by" in query:
        key = query["sort_by"]
        if key not in flight:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda x: x[key], reverse=reverse)
    if "limit" in query:
        matches = matches[:query["limit"]]
        
    return {"query": query, "matches": matches}

def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    elif not isinstance(queries, list):
        raise ValueError("Invalid queries format")
        
    results = []
    for q in queries:
        results.append(run_query(db, q))
    return results
