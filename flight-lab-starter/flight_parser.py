import argparse
import json
import sys
from query import run_queries

def main():
    parser = argparse.ArgumentParser(description="Flight management and search")
    parser.add_argument("-i", "--input", required=True, help="Input flights CSV file")
    parser.add_argument("-a", "--airports", help="Airports file")
    parser.add_argument("-q", "--queries", help="JSON file containing queries")
    parser.add_argument("-o", "--output", help="Output JSON file for query results")
    
    args = parser.parse_args()

    if args.queries and args.output:
        try:
            with open("db.json", "r", encoding="utf-8") as f:
                db = json.load(f)
                
            with open(args.queries, "r", encoding="utf-8") as f:
                queries = json.load(f)
                
            results = run_queries(db, queries)
            
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error processing queries: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
