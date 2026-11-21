"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import os
import json
import glob
import argparse
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files, write_errors_log
from query import run_queries

STUDENT_ID = "260ADB179"
FIRST_NAME = "Mylan"
LAST_NAME = "SCHNEIDER"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = argparse.ArgumentParser(description="Flight query tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", help="Single CSV file")
    group.add_argument("-d", help="Folder containing CSV files")
    group.add_argument("-j", help="Existing JSON database")
    
    parser.add_argument("-a", help="Airport list file")
    parser.add_argument("-o", default="db.json", help="Output path for JSON database")
    parser.add_argument("-q", help="Query JSON file")
    parser.add_argument("-r", default=".", help="Folder for query response file")
    
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    has_source = bool(args.i or args.d or args.j)
    if not has_source:
        print("Error: No data source provided", file=sys.stderr)
        return 2
        
    if (args.i or args.d) and not args.a:
        print("Error: -a is required with -i or -d", file=sys.stderr)
        return 2
        
    if args.j and args.o != "db.json":
        print("Error: -o cannot be used with -j", file=sys.stderr)
        return 2

    db = []
    
    try:
        if args.i:
            if not os.path.exists(args.i) or not os.path.exists(args.a):
                print(f"Error: File not found", file=sys.stderr)
                return 1
            airports = load_airports(args.a)
            valid_recs, log_msgs = parse_files([args.i], airports)
            db = valid_recs
            
            os.makedirs(os.path.dirname(os.path.abspath(args.o)) or ".", exist_ok=True)
            with open(args.o, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
                
            log_dir = os.path.dirname(os.path.abspath(args.o)) or "."
            errors_path = os.path.join(log_dir, "errors.log")
            write_errors_log(errors_path, log_msgs)
            
        elif args.d:
            if not os.path.isdir(args.d) or not os.path.exists(args.a):
                print(f"Error: Directory or airport file not found", file=sys.stderr)
                return 1
            airports = load_airports(args.a)
            csv_paths = sorted(glob.glob(os.path.join(args.d, "*.csv")))
            if not csv_paths:
                print(f"Error: No .csv files found in folder", file=sys.stderr)
                return 1
                
            valid_recs, log_msgs = parse_files(csv_paths, airports)
            db = valid_recs
            
            os.makedirs(os.path.dirname(os.path.abspath(args.o)) or ".", exist_ok=True)
            with open(args.o, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
                
            log_dir = os.path.dirname(os.path.abspath(args.o)) or "."
            errors_path = os.path.join(log_dir, "errors.log")
            write_errors_log(errors_path, log_msgs)
            
        elif args.j:
            if not os.path.exists(args.j):
                print(f"Error: JSON database not found", file=sys.stderr)
                return 1
            with open(args.j, "r", encoding="utf-8") as f:
                content = json.load(f)
                if not isinstance(content, list):
                    print(f"Error: JSON database must be an array", file=sys.stderr)
                    return 1
                db = content

        if args.q:
            if not os.path.exists(args.q):
                print(f"Error: Query file not found", file=sys.stderr)
                return 1
            with open(args.q, "r", encoding="utf-8") as f:
                try:
                    queries_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in query file", file=sys.stderr)
                    return 1
                    
            if not isinstance(queries_data, (dict, list)):
                print(f"Error: Query structure invalid", file=sys.stderr)
                return 1
                
            response_results = run_queries(db, queries_data)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
            resp_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp_str}.json"
            resp_path = os.path.join(args.r, resp_filename)
            
            os.makedirs(os.path.abspath(args.r), exist_ok=True)
            with open(resp_path, "w", encoding="utf-8") as f:
                json.dump(response_results, f, indent=2)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
