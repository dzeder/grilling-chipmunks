#!/usr/bin/env python3
"""Load Keg Shell Items + Item Components into Gulf sandbox.

Step 1: Resolve Item_Line and Item_Type SF IDs
Step 2: Load Keg_Shell_Items as ohfy__Item__c (upsert on External_ID__c)
Step 3: Query all Item SF IDs (including new keg shells)
Step 4: Build Item_Components CSV with resolved SF IDs
Step 5: Load Item_Components as ohfy__Item_Component__c (insert)
Step 6: Validate
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")


# ---------------------------------------------------------------------------
# Salesforce helpers (same pattern as load_5_supplier_products.py)
# ---------------------------------------------------------------------------
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
            "--line-ending",
            "CRLF",
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

    job_id = (
        data.get("result", {}).get("jobId")
        or data.get("result", {}).get("jobInfo", {}).get("id")
        or data.get("data", {}).get("jobId", "")
    )

    if "FailedRecordDetailsError" in data.get("name", ""):
        msg = data.get("message", "")
        print(f"  {msg}")
        if job_id:
            _show_bulk_errors(job_id)
        sys.exit(1)

    if "JobFailedError" in data.get("name", ""):
        print(f"  Job failed: {data.get('message', '')}", file=sys.stderr)
        sys.exit(1)

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


def run_sf_import(sobject, csv_path):
    """Bulk import (insert) CSV into Salesforce."""
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
            "--line-ending",
            "CRLF",
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

    job_id = (
        data.get("result", {}).get("jobId")
        or data.get("result", {}).get("jobInfo", {}).get("id")
        or data.get("data", {}).get("jobId", "")
    )

    if "FailedRecordDetailsError" in data.get("name", ""):
        msg = data.get("message", "")
        print(f"  {msg}")
        if job_id:
            _show_bulk_errors(job_id)
        sys.exit(1)

    if "JobFailedError" in data.get("name", ""):
        print(f"  Job failed: {data.get('message', '')}", file=sys.stderr)
        sys.exit(1)

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


def _show_bulk_errors(job_id, max_errors=10):
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
# Step 1: Resolve lookup SF IDs for Keg Shell Items
# ---------------------------------------------------------------------------
def step1_resolve_lookups():
    """Query SF for Item_Line and Item_Type IDs needed by keg shell items."""
    print("\n=== Step 1: Resolve Lookup SF IDs ===")

    # Item_Lines: Key__c = supplier_code → SF ID
    print("  Querying Item_Lines...")
    il_records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Item_Line__c WHERE ohfy__Key__c != null")
    item_line_map = {r["ohfy__Key__c"]: r["Id"] for r in il_records}
    print(f"    {len(item_line_map)} Item_Lines found")

    # Item_Types: Key__c = brand_code → SF ID
    print("  Querying Item_Types...")
    it_records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Item_Type__c WHERE ohfy__Key__c != null")
    item_type_map = {r["ohfy__Key__c"]: r["Id"] for r in it_records}
    print(f"    {len(item_type_map)} Item_Types found")

    return item_line_map, item_type_map


# ---------------------------------------------------------------------------
# Step 2: Load Keg Shell Items
# ---------------------------------------------------------------------------
def step2_load_keg_shells(item_line_map, item_type_map):
    """Read Keg_Shell_Items.csv, resolve lookups, upsert as Item__c."""
    print("\n=== Step 2: Load Keg Shell Items ===")

    source_path = OUTPUT_DIR / "Keg_Shell_Items.csv"
    rows = []
    with open(source_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"  Read {len(rows)} keg shell items from CSV")

    # Keg Shell record type — granted via Migration_Item_RecordTypes permission set
    KEG_SHELL_RT_ID = "012al000005RF1mAAG"

    csv_path = OUTPUT_DIR / "load_Keg_Shell_Items.csv"
    skipped = 0
    out_headers = [h for h in rows[0].keys() if h != "RecordTypeId"]
    out_headers.insert(0, "RecordTypeId")  # add it back with Master value
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers, lineterminator="\r\n", extrasaction="ignore")
        writer.writeheader()

        for row in rows:
            brand_code = row["ohfy__Item_Type__c"]
            supplier_code = row["ohfy__Item_Line__c"]

            # Resolve lookups to SF IDs
            if supplier_code in item_line_map:
                row["ohfy__Item_Line__c"] = item_line_map[supplier_code]
            else:
                print(f"    WARNING: Item_Line not found for supplier_code={supplier_code}, skipping")
                skipped += 1
                continue

            if brand_code in item_type_map:
                row["ohfy__Item_Type__c"] = item_type_map[brand_code]
            else:
                # Item_Type is optional for keg shells — clear it
                row["ohfy__Item_Type__c"] = ""

            row["RecordTypeId"] = KEG_SHELL_RT_ID
            writer.writerow(row)

    written = len(rows) - skipped
    print(f"  Generated {csv_path} with {written} records ({skipped} skipped)")

    if written > 0:
        run_sf_upsert("ohfy__Item__c", csv_path, "ohfy__External_ID__c")

    return written


# ---------------------------------------------------------------------------
# Step 3: Query all Item SF IDs
# ---------------------------------------------------------------------------
def step3_query_item_ids():
    """Query all Item__c records to build Key__c → SF ID map."""
    print("\n=== Step 3: Query Item SF IDs ===")

    records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Item__c WHERE ohfy__Key__c != null")
    item_map = {r["ohfy__Key__c"]: r["Id"] for r in records}
    print(f"  {len(item_map)} Items found in org")

    # Check how many keg shells are in the map
    keg_shells = [k for k in item_map if k.startswith("KEG-SHELL-")]
    print(f"  {len(keg_shells)} keg shell items found")

    return item_map


# ---------------------------------------------------------------------------
# Step 4: Build Item Components CSV with resolved SF IDs
# ---------------------------------------------------------------------------
def step4_build_components(item_map):
    """Read Item_Components.csv, resolve parent/child to SF IDs, write load CSV."""
    print("\n=== Step 4: Build Item Components CSV ===")

    source_path = OUTPUT_DIR / "Item_Components.csv"
    rows = []
    with open(source_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"  Read {len(rows)} item component rows from CSV")

    # Build load CSV with SF IDs
    csv_path = OUTPUT_DIR / "load_Item_Components.csv"
    headers = ["ohfy__Parent_Item__c", "ohfy__Child_Item__c", "ohfy__Quantity__c", "ohfy__Key__c"]
    skipped_parent = 0
    skipped_child = 0
    written = 0

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\r\n")
        writer.writeheader()

        for row in rows:
            parent_key = row["ohfy__Parent_Item__c"]  # VIP item code
            child_key = row["ohfy__Child_Item__c"]  # KEG-SHELL-{code}-{container}

            parent_id = item_map.get(parent_key)
            child_id = item_map.get(child_key)

            if not parent_id:
                skipped_parent += 1
                continue
            if not child_id:
                skipped_child += 1
                continue

            writer.writerow(
                {
                    "ohfy__Parent_Item__c": parent_id,
                    "ohfy__Child_Item__c": child_id,
                    "ohfy__Quantity__c": row["ohfy__Quantity__c"],
                    "ohfy__Key__c": row["ohfy__Key__c"],
                }
            )
            written += 1

    print(f"  Generated {csv_path} with {written} records")
    if skipped_parent:
        print(f"  WARNING: {skipped_parent} skipped (parent item not in org)")
    if skipped_child:
        print(f"  WARNING: {skipped_child} skipped (child keg shell not in org)")

    return csv_path, written


# ---------------------------------------------------------------------------
# Step 5: Load Item Components
# ---------------------------------------------------------------------------
def step5_load_components(csv_path, count):
    """Insert Item_Component__c records into Salesforce."""
    print("\n=== Step 5: Load Item Components ===")

    if count == 0:
        print("  No components to load!")
        return

    run_sf_import("ohfy__Item_Component__c", csv_path)


# ---------------------------------------------------------------------------
# Step 6: Validate
# ---------------------------------------------------------------------------
def step6_validate():
    """Spot-check loaded records."""
    print("\n=== Step 6: Validate ===")

    # Count keg shell items
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Item__c WHERE ohfy__Type__c = 'Keg Shell'")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Keg Shell items in org: {count}")

    # Count item components
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Item_Component__c")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Item Components in org: {count}")

    # Spot check: Blue Moon 1/6 BBL
    samples = run_sf_query(
        "SELECT ohfy__Parent_Item__r.Name, ohfy__Child_Item__r.Name, "
        "ohfy__Quantity__c, ohfy__Key__c "
        "FROM ohfy__Item_Component__c "
        "ORDER BY ohfy__Parent_Item__r.Name LIMIT 5"
    )
    print("  Sample Item Components:")
    for s in samples:
        parent = s.get("ohfy__Parent_Item__r", {}).get("Name", "?") if s.get("ohfy__Parent_Item__r") else "?"
        child = s.get("ohfy__Child_Item__r", {}).get("Name", "?") if s.get("ohfy__Child_Item__r") else "?"
        qty = s.get("ohfy__Quantity__c", "?")
        print(f"    {parent} → {child} (qty={qty})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Keg Shell Items + Item Components")
    print("=" * 60)

    item_line_map, item_type_map = step1_resolve_lookups()
    step2_load_keg_shells(item_line_map, item_type_map)
    item_map = step3_query_item_ids()
    csv_path, count = step4_build_components(item_map)
    step5_load_components(csv_path, count)
    step6_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
