#!/usr/bin/env python3
"""Load product hierarchy (Item_Lines → Item_Types → Items) for 5 suppliers."""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

TARGET_ORG = "gulf-partial-copy-sandbox"
SUPPLIER_CODES = ["3M", "3N", "2F", "2U", "1C"]
ITEM_TYPE_RT = "012al000005RF2AAAW"  # Finished Good
OUTPUT_DIR = Path("migration_output")

# Item_Line/Item_Type Type__c: product type, not beverage type
# All items for these 5 suppliers are Finished Goods
ITEM_LINE_TYPE = "Finished Good"

# Item_Type Subtype__c: valid picklist values are Beer, Wine, Spirit, Seltzer, Cider, Kombucha, RTD
SUBTYPE_MAP = {
    "Beer": "Beer",
    "Wine": "Wine",
    "Spirits": "Spirit",  # VIP uses plural, Ohanafy uses singular
    "Non-Alcoholic": "",  # No valid picklist match; leave blank
}

# Packaging_Type__c mapping: VIP descriptions → valid Ohanafy picklist values
PACKAGING_TYPE_MAP = {
    # Exact keg/barrel matches
    "1/2 Barrel(s)": "1/2 Barrel(s)",
    "1/4 Barrel(s)": "1/4 Barrel(s)",
    "1/6 Barrel(s)": "1/6 Barrel(s)",
    "Barrel(s)": "Barrel(s)",
    # Case configurations with direct mappings
    "4/6/12Z CAN": "Case - 4x6 - 12oz - Can",
    "6/4/16Z CAN": "Case - 6x4 - 16oz - Can",
    "2/12Z CAN": "Case - 2x12 - 12oz - Can",
    "2/12/12Z CAN": "Case - 2x12 - 12oz - Can",
    "15/19.2Z CAN": "Case - 15x - 19.2oz - Can",
    "12/19.2Z CAN": "Case - 15x - 19.2oz - Can",
}

# Patterns for singles → "Each"
SINGLES_PATTERNS = ("SINGLES", "SINGLE")

# Valid Packaging_Type values per dependent picklist config (from field metadata)
# Values NOT in this set will be blanked out to avoid restricted picklist errors
VALID_PACKAGING_TYPES = {
    "US Count": {"Each"},
    "US Volume": {
        "1/2 Barrel(s)",
        "1/4 Barrel(s)",
        "1/6 Barrel(s)",
        "Barrel(s)",
        "Cup(s)",
        "Fluid Ounce(s)",
        "Gallon(s)",
        "Pint(s)",
        "Proof Gallon(s)",
        "Quart(s)",
        "Tablespoon(s)",
        "Teaspoon(s)",
        "Wine Gallon(s)",
        "Case - 4x6 - 12oz - Can",
        "Case - 6x4 - 16oz - Can",
        "Case - 4x4 - 16oz - Can",
        "Case - 20x - 22oz - Bottle",
        # Added via dependent picklist metadata deployment
        "Case Equivalent(s)",
        "Case - 2x12 - 12oz - Can",
        "Case - 15x - 19.2oz - Can",
    },
}

# Transformation Settings: Packaging_Type → Fluid Ounces conversion
# These must exist in the org for the Item validation rule to pass
TRANSFORMATION_SETTINGS = {
    # UOM value: (equal_to_fluid_oz, type)
    "Case - 4x6 - 12oz - Can": (288.0, "Volume"),
    "Case - 6x4 - 16oz - Can": (384.0, "Volume"),
    "Case - 2x12 - 12oz - Can": (288.0, "Volume"),
    "Case - 15x - 19.2oz - Can": (288.0, "Volume"),
    "Case Equivalent(s)": (288.0, "Volume"),
    "1/2 Barrel(s)": (1984.0, "Volume"),
    "1/4 Barrel(s)": (992.0, "Volume"),
    "1/6 Barrel(s)": (661.0, "Volume"),
    "Barrel(s)": (3968.0, "Volume"),
    "Each": (12.0, "Volume"),
}
TS_VOLUME_RT = "012al000005RF1yAAG"  # Volume record type


def map_packaging_type(vip_value, package_type):
    """Map VIP Packaging_Type to valid Ohanafy picklist value.
    Returns (packaging_type, uom) tuple.
    """
    if not vip_value:
        if package_type == "Kegged":
            return "1/6 Barrel(s)", "US Volume"
        return "Case Equivalent(s)", "US Volume"
    if vip_value in PACKAGING_TYPE_MAP:
        mapped = PACKAGING_TYPE_MAP[vip_value]
        if mapped == "Each":
            return mapped, "US Count"
        return mapped, "US Volume"
    # Singles/each
    if any(p in vip_value.upper() for p in SINGLES_PATTERNS):
        return "Each", "US Count"
    # Kegged items default
    if package_type == "Kegged":
        return "1/6 Barrel(s)", "US Volume"
    # Unknown packaged items default to Case Equivalent(s)
    return "Case Equivalent(s)", "US Volume"


def validate_packaging_for_uom(packaging_type, uom):
    """Ensure packaging_type is valid for the given UOM per dependent picklist.
    Returns valid packaging_type or blank string.
    """
    if not packaging_type:
        return ""
    valid_set = VALID_PACKAGING_TYPES.get(uom, set())
    if packaging_type in valid_set:
        return packaging_type
    return ""  # Blank out invalid values


def run_sf_query(soql):
    """Run SOQL query and return records."""
    result = subprocess.run(
        ["sf", "data", "query", "--query", soql, "--target-org", TARGET_ORG, "--json"], capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    if data.get("status") != 0:
        print(f"  SOQL error: {data}", file=sys.stderr)
        sys.exit(1)
    return data["result"]["records"]


def run_sf_import(sobject, csv_path):
    """Bulk import CSV into Salesforce. Returns job info."""
    print(f"  Importing {csv_path} into {sobject}...")
    result = subprocess.run(
        [
            "sf",
            "data",
            "import",
            "bulk",
            "--sobject",
            sobject,
            "--file",
            str(csv_path),
            "--wait",
            "10",
            "--target-org",
            TARGET_ORG,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)

    # Extract job ID
    job_id = (
        data.get("result", {}).get("jobId")
        or data.get("result", {}).get("jobInfo", {}).get("id")
        or data.get("data", {}).get("jobId", "")
    )

    # Check if error response
    if "FailedRecordDetailsError" in data.get("name", ""):
        msg = data.get("message", "")
        print(f"  {msg}")
        if job_id:
            _show_bulk_errors(job_id)
        sys.exit(1)

    if "JobFailedError" in data.get("name", ""):
        print(f"  Job failed: {data.get('message', '')}", file=sys.stderr)
        sys.exit(1)

    # Success path
    job_info = data.get("result", {}).get("jobInfo", {})
    records_processed = job_info.get("numberRecordsProcessed", "?")
    records_failed = job_info.get("numberRecordsFailed", "?")
    print(f"  Processed: {records_processed}, Failed: {records_failed}")

    if str(records_failed) not in ("0", "?") and int(str(records_failed)) > 0:
        if job_id:
            _show_bulk_errors(job_id)
        if int(str(records_failed)) == int(str(records_processed)):
            sys.exit(1)
    return data


def run_sf_upsert(sobject, csv_path, external_id):
    """Bulk upsert CSV into Salesforce using external ID."""
    print(f"  Upserting {csv_path} into {sobject} on {external_id}...")
    result = subprocess.run(
        [
            "sf",
            "data",
            "upsert",
            "bulk",
            "--sobject",
            sobject,
            "--file",
            str(csv_path),
            "--external-id",
            external_id,
            "--wait",
            "15",
            "--target-org",
            TARGET_ORG,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)

    # Extract job ID from either success or error response
    job_id = (
        data.get("result", {}).get("jobId")
        or data.get("result", {}).get("jobInfo", {}).get("id")
        or data.get("data", {}).get("jobId", "")
    )

    # Check if this is an error response (all records failed)
    if "FailedRecordDetailsError" in data.get("name", ""):
        msg = data.get("message", "")
        print(f"  {msg}")
        if job_id:
            _show_bulk_errors(job_id)
        sys.exit(1)

    # Success path
    job_info = data.get("result", {}).get("jobInfo", {})
    records_processed = job_info.get("numberRecordsProcessed", "?")
    records_failed = job_info.get("numberRecordsFailed", "?")
    print(f"  Processed: {records_processed}, Failed: {records_failed}")

    if str(records_failed) not in ("0", "?") and int(str(records_failed)) > 0:
        if job_id:
            _show_bulk_errors(job_id)
        if int(str(records_failed)) == int(str(records_processed)):
            sys.exit(1)
    return data


def _show_bulk_errors(job_id, max_errors=5):
    """Fetch and display errors from a bulk job."""
    subprocess.run(
        ["sf", "data", "bulk", "results", "--job-id", job_id, "--target-org", TARGET_ORG],
        capture_output=True,
        text=True,
    )
    failed_csv = Path(f"{job_id}-failed-records.csv")
    if failed_csv.exists():
        with open(failed_csv) as f:
            reader = csv.DictReader(f)
            shown = 0
            for row in reader:
                if row.get("sf__Error") and shown < max_errors:
                    print(f"    Error: {row['sf__Error']}")
                    shown += 1
        failed_csv.unlink(missing_ok=True)
    success_csv = Path(f"{job_id}-success-records.csv")
    success_csv.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Step 1: Verify suppliers exist in org
# ---------------------------------------------------------------------------
def step1_verify_suppliers():
    """Verify all 5 supplier Accounts exist. Return {code: {id, ext_id}}."""
    print("\n=== Step 1: Verify Suppliers ===")
    codes_str = ",".join(f"'{c}'" for c in SUPPLIER_CODES)
    records = run_sf_query(
        f"SELECT Id, Name, ohfy__External_ID__c, ohfy__Customer_Number__c "
        f"FROM Account "
        f"WHERE ohfy__Customer_Number__c IN ({codes_str}) AND Type = 'Supplier'"
    )
    suppliers = {}
    for r in records:
        code = r["ohfy__Customer_Number__c"]
        suppliers[code] = {
            "id": r["Id"],
            "ext_id": r["ohfy__External_ID__c"],
            "name": r["Name"],
        }
        print(f"  {r['Name']:30s}  code={code}  ext_id={r['ohfy__External_ID__c']}  id={r['Id']}")

    missing = set(SUPPLIER_CODES) - set(suppliers.keys())
    if missing:
        print(f"  MISSING suppliers: {missing}", file=sys.stderr)
        sys.exit(1)
    print(f"  All {len(suppliers)} suppliers verified.")
    return suppliers


# ---------------------------------------------------------------------------
# Step 2: Load Item_Lines
# ---------------------------------------------------------------------------
def step2_load_item_lines(suppliers):
    """Load 5 Item_Line records. Return {supplier_code: item_line_id}."""
    print("\n=== Step 2: Load Item_Lines ===")

    # Check for existing
    codes_str = ",".join(f"'{c}'" for c in SUPPLIER_CODES)
    existing = run_sf_query(f"SELECT Id, ohfy__Key__c FROM ohfy__Item_Line__c WHERE ohfy__Key__c IN ({codes_str})")
    existing_map = {r["ohfy__Key__c"]: r["Id"] for r in existing}
    if existing_map:
        print(f"  Found {len(existing_map)} existing Item_Lines: {list(existing_map.keys())}")

    # Filter source CSV for our 5 suppliers
    source_rows = []
    with open(OUTPUT_DIR / "Item_Lines.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ohfy__Key__c"] in SUPPLIER_CODES:
                source_rows.append(row)

    # Determine which need inserting
    to_insert = [r for r in source_rows if r["ohfy__Key__c"] not in existing_map]

    if not to_insert:
        print("  All 5 Item_Lines already exist. Skipping insert.")
    else:
        # Generate corrected CSV
        csv_path = OUTPUT_DIR / "load_Item_Lines_5suppliers.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(
                [
                    "Name",
                    "ohfy__Key__c",
                    "ohfy__Supplier__r.ohfy__External_ID__c",
                    "ohfy__Type__c",
                ]
            )
            for row in to_insert:
                code = row["ohfy__Key__c"]
                writer.writerow(
                    [
                        row["Name"],
                        code,
                        suppliers[code]["ext_id"],
                        ITEM_LINE_TYPE,
                    ]
                )
        print(f"  Generated {csv_path} with {len(to_insert)} records")
        run_sf_import("ohfy__Item_Line__c", csv_path)

    # Query back all 5 Item_Line IDs
    time.sleep(2)  # Brief wait for indexing
    records = run_sf_query(f"SELECT Id, ohfy__Key__c FROM ohfy__Item_Line__c WHERE ohfy__Key__c IN ({codes_str})")
    item_line_ids = {r["ohfy__Key__c"]: r["Id"] for r in records}
    for code in SUPPLIER_CODES:
        if code not in item_line_ids:
            print(f"  ERROR: Item_Line for {code} not found after insert!", file=sys.stderr)
            sys.exit(1)
        print(f"  {code} → {item_line_ids[code]}")
    return item_line_ids


# ---------------------------------------------------------------------------
# Step 3: Load Item_Types
# ---------------------------------------------------------------------------
def step3_load_item_types(item_line_ids):
    """Load Item_Types for the 5 suppliers. Return {brand_code: item_type_id}."""
    print("\n=== Step 3: Load Item_Types ===")

    # Read source CSV, filter for our suppliers
    source_rows = []
    with open(OUTPUT_DIR / "Item_Types.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ohfy__Item_Line__c"] in SUPPLIER_CODES:
                source_rows.append(row)
    print(f"  Found {len(source_rows)} Item_Types for 5 suppliers")

    # Collect brand codes
    brand_codes = [r["ohfy__Key__c"] for r in source_rows]

    # Check for existing
    existing_map = {}
    # Query in batches (SOQL IN clause limit)
    batch_size = 100
    for i in range(0, len(brand_codes), batch_size):
        batch = brand_codes[i : i + batch_size]
        codes_str = ",".join(f"'{c}'" for c in batch)
        records = run_sf_query(f"SELECT Id, ohfy__Key__c FROM ohfy__Item_Type__c WHERE ohfy__Key__c IN ({codes_str})")
        for r in records:
            existing_map[r["ohfy__Key__c"]] = r["Id"]
    if existing_map:
        print(f"  Found {len(existing_map)} existing Item_Types")

    to_insert = [r for r in source_rows if r["ohfy__Key__c"] not in existing_map]

    if not to_insert:
        print("  All Item_Types already exist. Skipping insert.")
    else:
        # Generate corrected CSV
        csv_path = OUTPUT_DIR / "load_Item_Types_5suppliers.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(
                [
                    "Name",
                    "ohfy__Key__c",
                    "ohfy__Item_Line__c",
                    "ohfy__Subtype__c",
                    "ohfy__Type__c",
                    "ohfy__Short_Name__c",
                    "ohfy__Supplier_Number__c",
                ]
            )
            for row in to_insert:
                supplier_code = row["ohfy__Item_Line__c"]
                raw_subtype = row["ohfy__Subtype__c"]
                writer.writerow(
                    [
                        row["Name"],
                        row["ohfy__Key__c"],
                        item_line_ids[supplier_code],  # Actual SF ID
                        SUBTYPE_MAP.get(raw_subtype, ""),
                        ITEM_LINE_TYPE,  # Type__c = "Finished Good"
                        row["ohfy__Short_Name__c"],
                        row["ohfy__Supplier_Number__c"],
                    ]
                )
        print(f"  Generated {csv_path} with {len(to_insert)} records")
        run_sf_import("ohfy__Item_Type__c", csv_path)

    # Query back all Item_Type IDs for our brand codes
    time.sleep(2)
    item_type_ids = dict(existing_map)  # Start with existing
    for i in range(0, len(brand_codes), batch_size):
        batch = brand_codes[i : i + batch_size]
        codes_str = ",".join(f"'{c}'" for c in batch)
        records = run_sf_query(f"SELECT Id, ohfy__Key__c FROM ohfy__Item_Type__c WHERE ohfy__Key__c IN ({codes_str})")
        for r in records:
            item_type_ids[r["ohfy__Key__c"]] = r["Id"]

    found = sum(1 for bc in brand_codes if bc in item_type_ids)
    missing = [bc for bc in brand_codes if bc not in item_type_ids]
    print(f"  Resolved {found}/{len(brand_codes)} Item_Type IDs")
    if missing:
        print(f"  WARNING: Missing Item_Types: {missing[:10]}...")
    return item_type_ids


# ---------------------------------------------------------------------------
# Step 3.5: Ensure Transformation Settings exist
# ---------------------------------------------------------------------------
def step3b_ensure_transformation_settings():
    """Create Transformation Settings needed for Item validation."""
    print("\n=== Step 3.5: Ensure Transformation Settings ===")

    # Check what already exists
    existing = run_sf_query("SELECT ohfy__UOM__c FROM ohfy__Transformation_Setting__c")
    existing_uoms = {r["ohfy__UOM__c"] for r in existing}

    needed = {uom for uom in TRANSFORMATION_SETTINGS if uom not in existing_uoms}
    if not needed:
        print(f"  All {len(TRANSFORMATION_SETTINGS)} Transformation Settings exist.")
        return

    print(f"  Creating {len(needed)} Transformation Settings...")
    for uom in sorted(needed):
        equal_to, ts_type = TRANSFORMATION_SETTINGS[uom]
        # Key__c must be unique — use UOM name + target UOM
        key = f"{uom}__Fluid Ounce(s)"
        values = (
            f"RecordTypeId='{TS_VOLUME_RT}' "
            f"ohfy__Key__c='{key}' "
            f"ohfy__UOM__c='{uom}' "
            f"ohfy__Equal_To__c={equal_to} "
            f"ohfy__Equal_To_UOM__c='Fluid Ounce(s)' "
            f"ohfy__Type__c='{ts_type}' "
            f"ohfy__Is_Active__c=true"
        )
        result = subprocess.run(
            [
                "sf",
                "data",
                "create",
                "record",
                "--sobject",
                "ohfy__Transformation_Setting__c",
                "--values",
                values,
                "--target-org",
                TARGET_ORG,
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        if data.get("status") == 0:
            rec_id = data["result"]["id"]
            print(f"    Created: {uom} → {equal_to} fl oz  ({rec_id})")
        else:
            err = data.get("message", "unknown error")
            print(f"    FAILED: {uom} — {err}")


# ---------------------------------------------------------------------------
# Step 4: Load Items
# ---------------------------------------------------------------------------
def step4_load_items(item_line_ids, item_type_ids):
    """Load Items for the 5 suppliers. Returns count."""
    print("\n=== Step 4: Load Items ===")

    # Read source CSV, filter for our suppliers
    source_rows = []
    with open(OUTPUT_DIR / "Items.csv", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            if row["ohfy__Item_Line__c"] in SUPPLIER_CODES:
                source_rows.append(row)
    print(f"  Found {len(source_rows)} Items for 5 suppliers")

    # Build output headers — drop RecordTypeId (user profile may not have access)
    out_headers = [h for h in headers if h != "RecordTypeId"]

    # Generate CSV with SF IDs substituted
    csv_path = OUTPUT_DIR / "load_Items_5suppliers.csv"
    skipped = 0
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers, lineterminator="\n")
        writer.writeheader()
        for row in source_rows:
            brand_code = row["ohfy__Item_Type__c"]
            supplier_code = row["ohfy__Item_Line__c"]

            if brand_code not in item_type_ids:
                skipped += 1
                continue
            if supplier_code not in item_line_ids:
                skipped += 1
                continue

            row["ohfy__Item_Type__c"] = item_type_ids[brand_code]
            row["ohfy__Item_Line__c"] = item_line_ids[supplier_code]
            row.pop("RecordTypeId", None)
            # Map Packaging_Type__c and determine correct UOM
            pkg_type, uom = map_packaging_type(
                row.get("ohfy__Packaging_Type__c", ""),
                row.get("ohfy__Package_Type__c", ""),
            )
            # Validate against dependent picklist config
            pkg_type = validate_packaging_for_uom(pkg_type, uom)
            row["ohfy__Packaging_Type__c"] = pkg_type
            row["ohfy__UOM__c"] = uom
            writer.writerow(row)

    written = len(source_rows) - skipped
    print(f"  Generated {csv_path} with {written} records ({skipped} skipped)")

    if written > 0:
        run_sf_upsert("ohfy__Item__c", csv_path, "ohfy__External_ID__c")

    return written


# ---------------------------------------------------------------------------
# Step 5: Validate
# ---------------------------------------------------------------------------
def step5_validate(item_line_ids):
    """Validate loaded data counts."""
    print("\n=== Step 5: Validate ===")

    ids_str = ",".join(f"'{v}'" for v in item_line_ids.values())

    # Item_Lines
    codes_str = ",".join(f"'{c}'" for c in SUPPLIER_CODES)
    records = run_sf_query(f"SELECT COUNT(Id) cnt FROM ohfy__Item_Line__c WHERE ohfy__Key__c IN ({codes_str})")
    il_count = records[0]["cnt"]
    print(f"  Item_Lines: {il_count} (expected 5)")

    # Item_Types
    records = run_sf_query(f"SELECT COUNT(Id) cnt FROM ohfy__Item_Type__c WHERE ohfy__Item_Line__c IN ({ids_str})")
    it_count = records[0]["cnt"]
    print(f"  Item_Types: {it_count} (expected 198)")

    # Items
    records = run_sf_query(f"SELECT COUNT(Id) cnt FROM ohfy__Item__c WHERE ohfy__Item_Line__c IN ({ids_str})")
    item_count = records[0]["cnt"]
    print(f"  Items: {item_count} (expected ~1806)")

    # Spot-check a sample item to verify lookups
    sample = run_sf_query(
        f"SELECT Name, ohfy__Item_Number__c, ohfy__Item_Type__r.Name, "
        f"ohfy__Item_Line__r.Name "
        f"FROM ohfy__Item__c "
        f"WHERE ohfy__Item_Line__c IN ({ids_str}) LIMIT 3"
    )
    for s in sample:
        print(
            f"  Sample: {s.get('Name', '?')[:40]}  "
            f"Type={s.get('ohfy__Item_Type__r', {}).get('Name', '?')}  "
            f"Line={s.get('ohfy__Item_Line__r', {}).get('Name', '?')}"
        )

    print("\n=== Done ===")


def main():
    print("=" * 60)
    print("Load Products for 5 Suppliers")
    print("=" * 60)

    suppliers = step1_verify_suppliers()
    item_line_ids = step2_load_item_lines(suppliers)
    item_type_ids = step3_load_item_types(item_line_ids)
    step3b_ensure_transformation_settings()
    step4_load_items(item_line_ids, item_type_ids)
    step5_validate(item_line_ids)


if __name__ == "__main__":
    main()
