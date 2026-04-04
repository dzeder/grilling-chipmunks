#!/usr/bin/env python3
"""
Generate ohfy__Transformation_Setting__c import CSVs.

Unified key format (replaces v1/v2):
  Volume: Fluid Ounce(s){UOM}            e.g. Fluid Ounce(s)Case - 12x1 - 12oz - Can
  Weight: Weight{SubType}{UOM}Pound(s)   e.g. WeightBeerCase - 12x1 - 12oz - CanPound(s)

Usage:
  python3 generate_transformation_settings.py \
    --sub-type "Beer" \
    --uoms "Case - 12x1 - 12oz - Can" "Case - 12x1 - 16oz - Can" \
    --output transformation-settings-import.csv

  # Exclude records that already exist in Salesforce (net-new only):
  python3 generate_transformation_settings.py \
    --sub-type "Beer" \
    --uoms "Case - 12x1 - 12oz - Can" \
    --existing-keys "Fluid Ounce(s)Case - 12x1 - 12oz - Can" \
    --output net-new.csv

  # Pass existing keys from delta JSON:
  python3 generate_transformation_settings.py \
    --sub-type "Beer" \
    --uoms "Case - 12x1 - 12oz - Can" \
    --existing-keys-file /tmp/delta.json \
    --output net-new.csv
"""

import argparse
import csv
import json

# Conversion data: UOM -> (fluid_oz, pounds, measurement_system)
CONVERSIONS = {
    # Barrels
    "1/2 Barrel(s)":              (1984.0,  124.0,  "US"),
    "1/4 Barrel(s)":              (992.0,   62.0,   "US"),
    "1/6 Barrel(s)":              (661.33,  41.33,  "US"),
    "Gallon(s)":                  (1689.6,  105.6,  "US"),
    # US oz cases
    "Case - 12x1 - 12oz - Can":   (144.0,   9.0,    "US"),
    "Case - 12x1 - 19.2oz - Can": (230.4,   14.4,   "US"),
    "Case - 12x1 - 24oz - Can":   (288.0,   18.0,   "US"),
    "Case - 12x1 - 25.4oz - Can": (304.8,   19.05,  "US"),
    "Case - 12x1 - 32oz - Bottle":(384.0,   24.0,   "US"),
    "Case - 12x1 - 32oz - Can":   (384.0,   24.0,   "US"),
    "Case - 12x1 - 40oz - Bottle":(480.0,   30.0,   "US"),
    "Case - 15x1 - 12oz - Can":   (180.0,   11.25,  "US"),
    "Case - 15x1 - 18oz - Bottle":(270.0,   16.88,  "US"),
    "Case - 15x1 - 22oz - Bottle":(330.0,   20.63,  "US"),
    "Case - 1x12 - 12oz - Can":   (144.0,   9.0,    "US"),
    "Case - 1x15 - 12oz - Can":   (180.0,   11.25,  "US"),
    "Case - 1x15 - 16oz - Bottle":(240.0,   15.0,   "US"),
    "Case - 1x18 - 12oz - Bottle":(216.0,   13.5,   "US"),
    "Case - 1x18 - 12oz - Can":   (216.0,   13.5,   "US"),
    "Case - 1x18 - 16oz - Can":   (288.0,   18.0,   "US"),
    "Case - 1x20 - 12oz - Bottle":(240.0,   15.0,   "US"),
    "Case - 1x24 - 10oz - Can":   (240.0,   15.0,   "US"),
    "Case - 1x24 - 11.5oz - Bottle":(276.0, 17.25,  "US"),
    "Case - 1x24 - 12oz - Bottle":(288.0,   18.0,   "US"),
    "Case - 1x24 - 12oz - Can":   (288.0,   18.0,   "US"),
    "Case - 1x24 - 16oz - Bottle":(384.0,   24.0,   "US"),
    "Case - 1x24 - 16oz - Can":   (384.0,   24.0,   "US"),
    "Case - 1x30 - 12oz - Can":   (360.0,   22.5,   "US"),
    "Case - 1x36 - 12oz - Can":   (432.0,   27.0,   "US"),
    "Case - 2x12 - 10oz - Can":   (240.0,   15.0,   "US"),
    "Case - 2x12 - 11.5oz - Bottle":(276.0, 17.25,  "US"),
    "Case - 2x12 - 12oz - Bottle":(288.0,   18.0,   "US"),
    "Case - 2x12 - 12oz - Can":   (288.0,   18.0,   "US"),
    "Case - 2x12 - 16oz - Can":   (384.0,   24.0,   "US"),
    "Case - 2x12 - 8oz - Can":    (192.0,   12.0,   "US"),
    "Case - 2x15 - 12oz - Can":   (360.0,   22.5,   "US"),
    "Case - 2x24 - 8oz - Can":    (384.0,   24.0,   "US"),
    "Case - 2x9 - 16oz - Bottle": (288.0,   18.0,   "US"),
    "Case - 3x8 - 16oz - Can":    (384.0,   24.0,   "US"),
    "Case - 4x3 - 24oz - Can":    (288.0,   18.0,   "US"),
    "Case - 4x6 - 10oz - Can":    (240.0,   15.0,   "US"),
    "Case - 4x6 - 11.5oz - Bottle":(276.0,  17.25,  "US"),
    "Case - 4x6 - 12oz - Bottle": (288.0,   18.0,   "US"),
    "Case - 4x6 - 12oz - Can":    (288.0,   18.0,   "US"),
    "Case - 4x6 - 16oz - Can":    (384.0,   24.0,   "US"),
    "Case - 4x6 - 7oz - Bottle":  (168.0,   10.5,   "US"),
    "Case - 4x6 - 8oz - Can":     (192.0,   12.0,   "US"),
    "Case - 6x4 - 16oz - Can":    (384.0,   24.0,   "US"),
    "Case - 6x4 - 8.4oz - Can":   (201.6,   12.6,   "US"),
    # Metric cases
    "12x1 - 275mL - Bottle":      (111.55,  6.97,   "Metric"),
    "1x15 - 250mL - Can":         (126.8,   7.93,   "Metric"),
    "1x24 - 150mL - Can":         (121.73,  7.61,   "Metric"),
    "1x24 - 250mL - Can":         (202.88,  12.68,  "Metric"),
    "1x24 - 330mL - Bottle":      (267.8,   16.74,  "Metric"),
    "20x1 - 50cL - Bottle":       (338.14,  21.13,  "Metric"),
    "24x1 - 500mL - Can":         (405.77,  25.36,  "Metric"),
    "2x12 - 330mL - Bottle":      (267.8,   16.74,  "Metric"),
    "2x12 - 33cL - Bottle":       (267.8,   16.74,  "Metric"),
    "3x8 - 150mL - Can":          (121.73,  7.61,   "Metric"),
    "4x6 - 330mL - Bottle":       (267.8,   16.74,  "Metric"),
    "4x6 - 330mL - Can":          (267.8,   16.74,  "Metric"),
    "4x6 - 33cL - Bottle":        (267.8,   16.74,  "Metric"),
    "6x1 - 375mL - Bottle":       (76.09,   4.76,   "Metric"),
    "6x1 - 750mL - Bottle":       (152.16,  9.51,   "Metric"),
    "6x4 - 200mL - Bottle":       (162.31,  10.14,  "Metric"),
    "6x4 - 500mL - Can":          (405.77,  25.36,  "Metric"),
    "8x1 - 500mL - Bottle":       (135.26,  8.45,   "Metric"),
}

COLUMNS = [
    "_", "ohfy__Equal_To_UOM__c", "ohfy__Measurement_System__c",
    "ohfy__Sub_Type__c", "ohfy__Type__c", "ohfy__UOM__c",
    "ohfy__Active__c", "ohfy__Equal_To__c", "ohfy__Key__c",
]


def make_key(type_, sub_type, uom, equal_to_uom):
    """Unified key format — replaces v1/v2 variants.

    Volume: Fluid Ounce(s){UOM}          e.g. Fluid Ounce(s)Case - 12x1 - 12oz - Can
    Weight: Weight{SubType}{UOM}Pound(s) e.g. WeightBeerCase - 12x1 - 12oz - CanPound(s)
    """
    if type_ == "Volume":
        return f"{equal_to_uom}{uom}"
    return f"{type_}{sub_type}{uom}{equal_to_uom}"


def build_rows(uoms, sub_type, existing_keys=None):
    """Build CSV rows, skipping any whose key already exists in existing_keys."""
    rows = []
    missing = []
    skipped = []
    excluded = set(existing_keys) if existing_keys else set()

    for uom in uoms:
        if uom not in CONVERSIONS:
            missing.append(uom)
            continue
        fl_oz, lbs, system = CONVERSIONS[uom]
        for type_, equal_to_uom, equal_to_val in [
            ("Volume", "Fluid Ounce(s)", fl_oz),
            ("Weight", "Pound(s)", lbs),
        ]:
            key = make_key(type_, sub_type, uom, equal_to_uom)
            if key in excluded:
                skipped.append(key)
                continue
            rows.append({
                "_": "[ohfy__Transformation_Setting__c]",
                "ohfy__Equal_To_UOM__c": equal_to_uom,
                "ohfy__Measurement_System__c": system,
                "ohfy__Sub_Type__c": sub_type,
                "ohfy__Type__c": type_,
                "ohfy__UOM__c": uom,
                "ohfy__Active__c": "true",
                "ohfy__Equal_To__c": str(equal_to_val),
                "ohfy__Key__c": key,
            })
    return rows, missing, skipped


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows → {path}")


def load_existing_keys_from_file(path):
    """Load existing keys from a JSON file (delta output or query output)."""
    with open(path) as f:
        data = json.load(f)
    # Support both delta output (net_new_keys excluded, use existing_keys) and query output
    if "existing_keys" in data:
        return data["existing_keys"]
    if "existing_matched" in data:
        return [r["key"] for r in data.get("existing_matched", [])]
    if isinstance(data, list):
        return data
    return []


def main():
    parser = argparse.ArgumentParser(description="Generate transformation settings CSV (net-new only)")
    parser.add_argument("--sub-type", required=True, help="Product sub-type, e.g. Beer")
    parser.add_argument("--uoms", nargs="+", required=True, help="UOM strings to include")
    parser.add_argument("--existing-keys", nargs="*", default=[], help="Keys to exclude (already exist in Salesforce)")
    parser.add_argument("--existing-keys-file", help="JSON file containing existing keys (from sfdx_query_existing.py or compute_delta.py)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    # Collect all existing keys to exclude
    existing_keys = list(args.existing_keys)
    if args.existing_keys_file:
        existing_keys += load_existing_keys_from_file(args.existing_keys_file)

    rows, missing, skipped = build_rows(args.uoms, args.sub_type, existing_keys)

    if missing:
        print(f"WARNING: No conversion data for: {missing}")
        print("Add to CONVERSIONS dict or supply conversion values manually.")
    if skipped:
        print(f"Skipped {len(skipped)} existing records: {skipped}")

    write_csv(args.output, rows)


if __name__ == "__main__":
    main()
