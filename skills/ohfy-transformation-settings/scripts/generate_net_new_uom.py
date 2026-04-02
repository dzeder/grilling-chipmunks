#!/usr/bin/env python3
"""
Step 5: Generate list of net-new UOM picklist values that need to be added to Salesforce.

Compares desired UOM values against what already exists in the GlobalValueSet
and outputs only the values that need to be added manually in Salesforce Setup.

Usage:
  python3 generate_net_new_uom.py \
    --existing /tmp/uom-values.json \
    --desired "Case - 12x1 - 12oz - Can" "Case - 12x1 - 16oz - Can" \
    --output /tmp/net-new-uoms.txt

  # Or pipe desired from a file
  python3 generate_net_new_uom.py \
    --existing /tmp/uom-values.json \
    --desired-file /tmp/desired-uoms.txt \
    --output /tmp/net-new-uoms.txt
"""

import argparse
import json
import sys


def load_existing_values(json_path):
    """Load active values from sfdx_retrieve_globalvalueset.py output."""
    with open(json_path) as f:
        data = json.load(f)
    # Support both direct list and wrapped output
    if isinstance(data, list):
        return set(data)
    active = data.get("active_values", [])
    if not active:
        # Try all_values with isActive filter
        active = [v["value"] for v in data.get("all_values", []) if v.get("isActive", True)]
    return set(active)


def main():
    parser = argparse.ArgumentParser(description="Compute net-new UOM picklist values")
    parser.add_argument("--existing", required=True, help="Path to JSON from sfdx_retrieve_globalvalueset.py")
    parser.add_argument("--desired", nargs="*", default=[], help="Desired UOM values")
    parser.add_argument("--desired-file", help="File with one UOM per line")
    parser.add_argument("--output", help="Write net-new values to .txt file")
    args = parser.parse_args()

    existing = load_existing_values(args.existing)

    desired = list(args.desired)
    if args.desired_file:
        with open(args.desired_file) as f:
            file_values = [line.strip() for line in f if line.strip()]
        desired = desired + file_values

    if not desired:
        print(json.dumps({"status": "error", "message": "No desired UOM values provided"}), file=sys.stderr)
        sys.exit(1)

    net_new = [v for v in desired if v not in existing]
    already_exists = [v for v in desired if v in existing]

    result = {
        "status": "ok",
        "desired_count": len(desired),
        "existing_count": len(existing),
        "already_exists_count": len(already_exists),
        "net_new_count": len(net_new),
        "net_new": net_new,
        "already_exists": already_exists,
    }

    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            f.write("# Net-new UOM picklist values to add in Salesforce Setup\n")
            f.write("# Add these to the GlobalValueSet before importing transformation settings\n")
            f.write("#\n")
            for v in net_new:
                f.write(f"{v}\n")
        print(f"\n# Written {len(net_new)} net-new values to: {args.output}", file=sys.stderr)

    if net_new:
        print("\n# MANUAL ACTION REQUIRED:", file=sys.stderr)
        print("# Add the following values to the UOM GlobalValueSet in Salesforce Setup:", file=sys.stderr)
        for v in net_new:
            print(f"#   - {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
