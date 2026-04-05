#!/usr/bin/env python3
"""
Step 2: Describe ohfy__Transformation_Setting__c and auto-discover GlobalValueSet name.

Retrieves field metadata for ohfy__Transformation_Setting__c and extracts
the GlobalValueSet name from the ohfy__UOM__c picklist field describe.

Usage:
  python3 sfdx_describe_object.py --target-org <alias>
  python3 sfdx_describe_object.py --target-org <alias> --object ohfy__Transformation_Setting__c
"""

import argparse
import json
import subprocess
import sys

DEFAULT_OBJECT = "ohfy__Transformation_Setting__c"
KEY_FIELDS = [
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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
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


def describe_object(target_org, obj_name):
    return run_sf(
        ["sobject", "describe", "--sobject", obj_name, "--target-org", target_org],
        f"describe {obj_name}"
    )


def extract_global_value_set(field_describe):
    """Extract GlobalValueSet name from a picklist field describe result."""
    # The valueSetName appears in the field metadata under 'valueSetName' in some API versions
    # It may also appear nested under 'valueSet' -> 'valueSetName'
    if not field_describe:
        return None
    vs_name = field_describe.get("valueSetName")
    if vs_name:
        return vs_name
    value_set = field_describe.get("valueSet", {})
    if isinstance(value_set, dict):
        return value_set.get("valueSetName")
    return None


def main():
    parser = argparse.ArgumentParser(description="Describe Salesforce object and extract field metadata")
    parser.add_argument("--target-org", required=True, help="Org alias or username")
    parser.add_argument("--object", default=DEFAULT_OBJECT, help=f"Object API name (default: {DEFAULT_OBJECT})")
    args = parser.parse_args()

    raw = describe_object(args.target_org, args.object)

    if raw.get("status") == 1 or "error" in raw:
        print(json.dumps({
            "status": "error",
            "object": args.object,
            "message": raw.get("message", "Describe failed"),
            "detail": raw
        }, indent=2))
        sys.exit(1)

    fields = raw.get("result", {}).get("fields", [])
    if not fields:
        print(json.dumps({"status": "error", "message": "No fields returned", "raw": raw}, indent=2))
        sys.exit(1)

    # Build field map by name
    field_map = {f["name"]: f for f in fields}

    # Extract key field metadata
    key_field_meta = {}
    for fname in KEY_FIELDS:
        f = field_map.get(fname)
        if f:
            key_field_meta[fname] = {
                "label": f.get("label"),
                "type": f.get("type"),
                "length": f.get("length"),
                "required": not f.get("nillable", True),
                "picklistValues": [v["value"] for v in f.get("picklistValues", [])] if f.get("picklistValues") else None,
                "valueSetName": extract_global_value_set(f),
            }
        else:
            key_field_meta[fname] = {"status": "not_found"}

    # Auto-discover GlobalValueSet from ohfy__UOM__c
    uom_field = field_map.get("ohfy__UOM__c", {})
    global_value_set_name = extract_global_value_set(uom_field)

    print(json.dumps({
        "status": "ok",
        "object": args.object,
        "total_fields": len(fields),
        "global_value_set_name": global_value_set_name,
        "uom_picklist_values": [v["value"] for v in uom_field.get("picklistValues", [])],
        "key_fields": key_field_meta
    }, indent=2))


if __name__ == "__main__":
    main()
