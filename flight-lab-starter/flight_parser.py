import sys
import os
import argparse
import json
import logging
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "260ADB179"
FIRST_NAME = "Mylan"
LAST_NAME = "Schneider"

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(add_help=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i")
    group.add_argument("-d")
    group.add_argument("-j")
    
    parser.add_argument("-a")
    parser.add_argument("-o", default="db.json")
    parser.add_argument("-q")
    parser.add_argument("-r", default=".")

    try:
        args, unknown = parser.parse_known_args(argv)
    except Exception:
        return 2

    if unknown:
        return 2

    has_source = bool(args.i or args.d or args.j)
    if not has_source:
        parser.error("No data source provided (-i, -d, or -j required).")

    if (args.i or args.d) and not args.a:
        parser.error("Airport list file (-a) is required with -i or -d.")

    if args.j and "-o" in argv:
        parser.error("-o cannot be used with -j.")

    db = []
    log_messages = []

    try:
        if args.j:
            if not os.path.exists(args.j):
                sys.stderr.write(f"Error: JSON database file not found: {args.j}\n")
                return 1
            try:
                with open(args.j, "r", encoding="utf-8") as f:
                    db = json.load(f)
                if not isinstance(db, list):
                    sys.stderr.write("Error: JSON database must be a list.\n")
                    return 1
            except Exception as e:
                sys.stderr.write(f"Error: Invalid JSON database: {e}\n")
                return 1
        else:
            if not os.path.exists(args.a):
                sys.stderr.write(f"Error: Airport file not found: {args.a}\n")
                return 1
            
            try:
                airports = load_airports(args.a)
            except Exception as e:
                sys.stderr.write(f"Error: Could not load airports: {e}\n")
                return 1
            
            paths = []

            if args.i:
                if not os.path.exists(args.i):
                    sys.stderr.write(f"Error: CSV file not found: {args.i}\n")
                    return 1
                paths = [args.i]
            elif args.d:
                if not os.path.exists(args.d) or not os.path.isdir(args.d):
                    sys.stderr.write(f"Error: Directory not found: {args.d}\n")
                    return 1
                csv_files = sorted([os.path.join(args.d, f) for f in os.listdir(args.d) if f.endswith(".csv")])
                if not csv_files:
                    sys.stderr.write(f"Error: No .csv files found in directory: {args.d}\n")
                    return 1
                paths = csv_files

            db, log_messages = parse_files(paths, airports)

            try:
                os.makedirs(os.path.dirname(os.path.abspath(args.o)), exist_ok=True)
                with open(args.o, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
            except Exception as e:
                sys.stderr.write(f"Error: Could not write database file: {e}\n")
                return 1

            db_dir = os.path.dirname(os.path.abspath(args.o))
            log_path = os.path.join(db_dir, "errors.log")

            logger = logging.getLogger("flight_parser")
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(handler)

            try:
                for msg in log_messages:
                    logger.warning(msg)
            finally:
                logger.removeHandler(handler)
                handler.close()

        if args.q:
            if not os.path.exists(args.q):
                sys.stderr.write(f"Error: Query file not found: {args.q}\n")
                return 1
            try:
                with open(args.q, "r", encoding="utf-8") as f:
                    queries_data = json.load(f)
            except Exception as e:
                sys.stderr.write(f"Error: Invalid query JSON: {e}\n")
                return 1

            results = run_queries(db, queries_data)

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
            response_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp_str}.json"
            response_path = os.path.join(args.r, response_filename)

            try:
                os.makedirs(os.path.abspath(args.r), exist_ok=True)
                with open(response_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
            except Exception as e:
                sys.stderr.write(f"Error: Could not write response file: {e}\n")
                return 1

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
