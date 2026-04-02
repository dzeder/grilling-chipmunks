#!/usr/bin/env python3
"""
Step 7: Compute delta between expected transformation settings and existing records.

Compares what *should* exist (based on CONVERSIONS + sub-type) against what
already exists in Salesforce (from sfdx_query_existing.py output), using the
unified key format.

Unified key format:
  Volume: Fluid Ounce(s){UOM}
  Weight: Weight{SubType}{UOM}Pound(s)

Usage:
  python3 compute_delta.py --existing /tmp/existing.json --desired-sub-type "Beer"
  python3 compute_delta.py --existing /tmp/existing.json --desired-sub-type "Beer" --uoms "Case - 12x1 - 12oz - Can"
  python3 compute_delta.py --existing /tmp/existing.json --desired-sub-type "Beer" --output /tmp/delta.json
"""

import argparse
import json
import sys
import os

# Import CONVERSIONS from generate_transformation_settings
sys.path.insert(0, os.path.dirname(__file__))
from generate_transformation_settings import CONVERSIONS


def unified_key(type_, sub_type, uom, equal_to_uom):
    """Generate unified key format (replaces v1/v2)."""
    if type_ == "Volume":
        return f"{equal_to_uom}{uom}"          # Fluid Ounce(s){UOM}
    else:
        return f"{type_}{sub_type}{uom}{equal_to_uom}"   # Weight{SubType}{UOM}Pound(s)


def build_expected_keys(sub_type, uoms):
    """Build the full set of expected (key → row_spec) for a sub-type + UOM list."""
    expected = {}
    for uom in uoms:
        if uom not in CONVERSIONS:
            continue
        fl_oz, lbs, system = CONVERSIONS[uom]
        for type_, equal_to_uom, equal_to_val in [
            ("Volume", "Fluid Ounce(s)", fl_oz),
            ("Weight", "Pound(s)", lbs),
        ]:
            key = unified_key(type_, sub_type, uom, equal_to_uom)
            expected[key] = {
                "key": key,
                "uom": uom,
                "type": type_,
                "sub_type": sub_type,
                "equal_to_uom": equal_to_uom,
                "equal_to": equal_to_val,
                "measurement_system": system,
            }
    return expected


def main():
    parser = argparse.ArgumentParser(description="Compute delta between expected and existing transformation settings")
    parser.add_argument("--existing", required=True, help="Path to JSON from sfdx_query_existing.py")
    parser.add_argument("--desired-sub-type", required=True, help="Sub-type to generate (e.g. Beer)")
    parser.add_argument("--uoms", nargs="*", help="Specific UOMs to check (default: all in CONVERSIONS)")
    parser.add_argument("--output", help="Write delta JSON to file")
    args = parser.parse_args()

    # Load existing records
    with open(args.existing) as f:
        existing_data = json.load(f)

    existing_keys = set(existing_data.get("existing_keys", []))

    # Determine UOM list
    uoms = args.uoms if args.uoms else list(CONVERSIONS.keys())
    unknown_uoms = [u for u in uoms if u not in CONVERSIONS]

    # Build expected
    expected = build_expected_keys(args.desired_sub_type, uoms)

    # Compute delta
    net_new = {}
    existing_matched = {}
    existing_mismatched = []

    for key, spec in expected.items():
        if key in existing_keys:
            existing_matched[key] = spec
        else:
            net_new[key] = spec

    # Find existing keys that don't match any expected key (for this sub-type)
    for key in existing_keys:
        if key not in expected:
            existing_mismatched.append(key)

    output = {
        "status": "ok",
        "desired_sub_type": args.desired_sub_type,
        "uoms_checked": len(uoms),
        "unknown_uoms": unknown_uoms,
        "expected_total": len(expected),
        "existing_matched_count": len(existing_matched),
        "net_new_count": len(net_new),
        "existing_mismatched_count": len(existing_mismatched),
        "net_new": list(net_new.values()),
        "existing_matched": list(existing_matched.values()),
        "existing_mismatched_keys": existing_mismatched,
        "net_new_keys": list(net_new.keys()),
    }

    print(json.dumps(output, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n# Written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
