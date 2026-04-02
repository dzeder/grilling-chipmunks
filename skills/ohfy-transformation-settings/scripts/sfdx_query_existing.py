#!/usr/bin/env python3
"""
Step 6: Query existing ohfy__Transformation_Setting__c records from Salesforce.

Runs a SOQL query via sf CLI and outputs matching records as JSON.

Usage:
  python3 sfdx_query_existing.py --target-org <alias> --sub-type "Beer"
  python3 sfdx_query_existing.py --target-org <alias> --sub-type "Beer" --output /tmp/existing.json
  python3 sfdx_query_existing.py --target-org <alias>  # Query all records
"""

import argparse
import json
import subprocess
import sys

OBJECT = "ohfy__Transformation_Setting__c"
SELECT_FIELDS = [
    "Id",
    "Name",
    "ohfy__Key__c",
    "ohfy__UOM__c",
    "ohfy__Equal_To_UOM__c",
    "ohfy__Type__c",
    "ohfy__Sub_Type__c",
    "ohfy__Equal_To__c",
    "ohfy__Measurement_System__c",
    "ohfy__Active__c",
]


def run_sf(args, error_label="sf command"):
    cmd = ["sf"] + args + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        print(json.dumps({"error": "sf CLI not found"}))
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(json.dumps({"error": f"{error_label} timed out"}))
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "non-JSON output", "raw": result.stdout, "stderr": result.stderr}


def build_soql(sub_type=None, active_only=False):
    fields = ", ".join(SELECT_FIELDS)
    where_clauses = []
    if sub_type:
        escaped = sub_type.replace("'", "\\'")
        where_clauses.append(f"ohfy__Sub_Type__c = '{escaped}'")
    if active_only:
        where_clauses.append("ohfy__Active__c = true")
    where = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    return f"SELECT {fields} FROM {OBJECT}{where} ORDER BY ohfy__Key__c"


def query_records(target_org, soql):
    return run_sf(
        ["data", "query", "--query", soql, "--target-org", target_org],
        "SOQL query"
    )


def main():
    parser = argparse.ArgumentParser(description="Query existing Transformation Setting records")
    parser.add_argument("--target-org", required=True, help="Org alias or username")
    parser.add_argument("--sub-type", help="Filter by ohfy__Sub_Type__c value (e.g. Beer)")
    parser.add_argument("--active-only", action="store_true", help="Filter to active records only")
    parser.add_argument("--output", help="Write JSON output to file")
    args = parser.parse_args()

    soql = build_soql(sub_type=args.sub_type, active_only=args.active_only)

    raw = query_records(args.target_org, soql)

    if raw.get("status") == 1 or "error" in raw:
        print(json.dumps({
            "status": "error",
            "soql": soql,
            "message": raw.get("message", "Query failed"),
            "detail": raw
        }, indent=2))
        sys.exit(1)

    records = raw.get("result", {}).get("records", [])

    # Extract existing keys for delta computation
    existing_keys = [r.get("ohfy__Key__c") for r in records if r.get("ohfy__Key__c")]

    # Group by sub_type for summary
    sub_types = {}
    for r in records:
        st = r.get("ohfy__Sub_Type__c", "(none)")
        sub_types[st] = sub_types.get(st, 0) + 1

    output = {
        "status": "ok",
        "soql": soql,
        "total_count": len(records),
        "sub_type_filter": args.sub_type,
        "sub_type_counts": sub_types,
        "existing_keys": existing_keys,
        "records": records
    }

    print(json.dumps(output, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n# Written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
