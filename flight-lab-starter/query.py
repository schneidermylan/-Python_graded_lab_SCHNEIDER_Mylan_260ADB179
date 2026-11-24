from datetime import datetime

def validate_query_obj(q: dict) -> bool:
    if not isinstance(q, dict):
        return False
    
    allowed_keys = {
        "flight_id", "origin", "destination", 
        "departure_datetime", "arrival_datetime", 
        "price", "min_price", 
        "sort_by", "order", "limit"
    }
    
    has_sort_by = "sort_by" in q
    has_order = "order" in q
    
    if has_order and not has_sort_by:
        return False

    for k, v in q.items():
        if k not in allowed_keys:
            return False
        
        if k in ("flight_id", "origin", "destination"):
            if not isinstance(v, str):
                return False
        elif k in ("departure_datetime", "arrival_datetime"):
            if not isinstance(v, str):
                return False
            try:
                datetime.strptime(v, "%Y-%m-%d %H:%M")
            except ValueError:
                return False
        elif k in ("price", "min_price"):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return False
        elif k == "sort_by":
            if not isinstance(v, str) or v not in {
                "flight_id", "origin", "destination", 
                "departure_datetime", "arrival_datetime", "price"
            }:
                return False
        elif k == "order":
            if not isinstance(v, str) or v not in ("asc", "desc"):
                return False
        elif k == "limit":
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                return False
                
    return True

def run_query(db: list[dict], query: dict) -> dict:
    if not validate_query_obj(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
    
    matches = []
    for flight in db:
        match = True
        for k, v in query.items():
            if k in ("sort_by", "order", "limit"):
                continue
            
            if k == "flight_id":
                if flight.get("flight_id") != v:
                    match = False
                    break
            elif k == "origin":
                if flight.get("origin") != v:
                    match = False
                    break
            elif k == "destination":
                if flight.get("destination") != v:
                    match = False
                    break
            elif k == "departure_datetime":
                if flight.get("departure_datetime", "") < v:
                    match = False
                    break
            elif k == "arrival_datetime":
                if flight.get("arrival_datetime", "") > v:
                    match = False
                    break
            elif k == "price":
                if flight.get("price", float("inf")) > float(v):
                    match = False
                    break
            elif k == "min_price":
                if flight.get("price", float("-inf")) < float(v):
                    match = False
                    break
        if match:
            matches.append(flight)
    
    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda x: x.get(sort_key), reverse=reverse)
        
    if "limit" in query:
        limit = query["limit"]
        matches = matches[:limit]
        
    return {"query": query, "matches": matches}

def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    elif not isinstance(queries, list):
        return []
        
    results = []
    for q in queries:
        results.append(run_query(db, q))
    return results
