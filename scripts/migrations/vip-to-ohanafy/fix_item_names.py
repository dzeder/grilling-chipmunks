#!/usr/bin/env python3
"""Fix Item__c and Lot__c Names where the Name is just the SF record ID.

Queries the sandbox for records whose Name looks like a Salesforce ID
(starts with 'a0'), computes a display name from available fields, and
upserts the corrected Names.

Item Name priority:
  1. Packaging_Type_Short_Name__c (if non-blank)
  2. Item_Type.Name + Item_Number (brand name + item code)
  3. Item_Number__c alone (fallback)

Lot Name: Item name from lookup
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")


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
        return data

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


def fix_item_names():
    """Fix Item Names where Name is just the SF ID."""
    print("\n=== Fix Item Names ===")

    records = run_sf_query(
        "SELECT Name, ohfy__External_ID__c, ohfy__Item_Number__c, "
        "ohfy__Packaging_Type_Short_Name__c, "
        "ohfy__Item_Type__r.Name "
        "FROM ohfy__Item__c "
        "WHERE Name LIKE 'a0%'"
    )

    if not records:
        print("  No items with ID-like names. Nothing to fix!")
        return

    print(f"  Found {len(records)} items with ID-like names")

    rows = []
    for r in records:
        pkg_short = (r.get("ohfy__Packaging_Type_Short_Name__c") or "").strip()
        item_type_name = (r.get("ohfy__Item_Type__r") or {}).get("Name", "").strip()
        item_number = (r.get("ohfy__Item_Number__c") or "").strip()

        # Priority cascade
        if pkg_short:
            display_name = pkg_short
        elif item_type_name:
            display_name = f"{item_type_name} {item_number}"
        else:
            display_name = item_number

        if len(display_name) > 80:
            display_name = display_name[:80]

        rows.append(
            {
                "Name": display_name,
                "ohfy__External_ID__c": r["ohfy__External_ID__c"],
            }
        )

    rows.sort(key=lambda x: x["ohfy__External_ID__c"])

    csv_path = OUTPUT_DIR / "Item_Name_Fix.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "ohfy__External_ID__c"], lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Generated {csv_path} with {len(rows)} records")
    for row in rows[:5]:
        print(f"    {row['ohfy__External_ID__c']} -> {row['Name']}")

    run_sf_upsert("ohfy__Item__c", csv_path, "ohfy__External_ID__c")


def fix_lot_names():
    """Fix Lot Names where Name is just the SF ID.

    Lot__c has no External_ID field, so we update using the SF Id.
    Name format: '{Item Name} - {MM/DD/YYYY}' using the expiration date.
    """
    print("\n=== Fix Lot Names ===")

    records = run_sf_query(
        "SELECT Id, Name, ohfy__Lot_Identifier__c, ohfy__Item__r.Name, "
        "ohfy__Expiration_Date__c "
        "FROM ohfy__Lot__c "
        "WHERE Name LIKE 'a0%'"
    )

    if not records:
        print("  No lots with ID-like names. Nothing to fix!")
        return

    print(f"  Found {len(records)} lots with ID-like names")

    rows = []
    for r in records:
        item_name = (r.get("ohfy__Item__r") or {}).get("Name", "").strip()
        lot_id = (r.get("ohfy__Lot_Identifier__c") or "").strip()
        exp_date = (r.get("ohfy__Expiration_Date__c") or "").strip()

        # Format expiration date as MM/DD/YYYY
        exp_display = ""
        if exp_date:
            try:
                parts = exp_date.split("-")  # YYYY-MM-DD
                exp_display = f"{parts[1]}/{parts[2]}/{parts[0]}"
            except (IndexError, ValueError):
                exp_display = exp_date

        if item_name and exp_display:
            display_name = f"{item_name} - {exp_display}"
        elif item_name:
            display_name = item_name
        elif lot_id:
            display_name = lot_id
        else:
            display_name = r["Id"]

        if len(display_name) > 80:
            display_name = display_name[:80]

        rows.append(
            {
                "Id": r["Id"],
                "Name": display_name,
            }
        )

    rows.sort(key=lambda x: x["Id"])

    csv_path = OUTPUT_DIR / "Lot_Name_Fix.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Id", "Name"], lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Generated {csv_path} with {len(rows)} records")
    for row in rows[:5]:
        print(f"    {row['Id']} -> {row['Name']}")

    run_sf_upsert("ohfy__Lot__c", csv_path, "Id")


def main():
    print("=" * 60)
    print("Fix Names — Update ID-like Names Across Objects")
    print("=" * 60)

    fix_item_names()
    fix_lot_names()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
