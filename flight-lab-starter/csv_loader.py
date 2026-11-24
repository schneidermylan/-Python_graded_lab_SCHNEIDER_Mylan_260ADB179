import csv
import os
from validator import validate_row, to_record

def parse_files(paths, airports: set[str]) -> tuple[list[dict], list[str]]:
    if isinstance(paths, (str, os.PathLike)):
        paths = [paths]
    
    if airports is None:
        airports = set()
    elif not isinstance(airports, set):
        airports = set(airports)

    valid_records = []
    log_messages = []
    seen_flights = set()
    
    for path in paths:
        if not os.path.exists(path):
            continue
        basename = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                line_num = 0
                for raw_fields in reader:
                    line_num += 1
                    if line_num == 1:
                        continue
                    if not raw_fields:
                        continue
                    joined_raw = ",".join(raw_fields).strip()
                    if not joined_raw or joined_raw.startswith("#"):
                        continue
                    
                    err_code = validate_row(raw_fields, airports)
                    
                    if err_code is not None:
                        raw_line_str = ",".join([f.strip() for f in raw_fields])
                        msg = f"{basename}:{line_num}: {err_code} | {raw_line_str}"
                        log_messages.append(msg)
                    else:
                        record = to_record(raw_fields)
                        dup_key = (record["flight_id"], record["departure_datetime"])
                        
                        if dup_key in seen_flights:
                            raw_line_str = ",".join([f.strip() for f in raw_fields])
                            msg = f"{basename}:{line_num}: DUPLICATE_FLIGHT | {raw_line_str}"
                            log_messages.append(msg)
                        else:
                            seen_flights.add(dup_key)
                            valid_records.append(record)
        except Exception:
            pass
                        
    return valid_records, log_messages

def write_errors_log(log_path: str, log_messages: list[str]):
    if not log_path:
        return
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            for msg in log_messages:
                f.write(msg + "\n")
    except Exception:
        pass
