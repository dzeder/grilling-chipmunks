#!/usr/bin/env python3
"""Fix Invoice and Invoice Item Names where the Name is just the SF record ID.

Queries the sandbox for Invoice and Invoice Item records whose Name looks like
a Salesforce ID (starts with 'a0'), computes the correct display name from
related data already in SF, and upserts the corrected Names.

Invoice Name pattern:  "{Customer Name} {M/D/YYYY} - ${Subtotal}"
Invoice Item Name:     Item display name

Handles >50k records by looping until all are fixed.
Sorts by External_ID to reduce lock contention on parent rollups.
"""

import csv
import json
import subprocess
import sys
import time
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
        return data  # Don't exit — let caller retry

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


def fix_invoice_names():
    """Fix Invoice header Names where Name is just the SF ID."""
    print("\n=== Fix Invoice Header Names ===")

    records = run_sf_query(
        "SELECT Name, ohfy__External_ID__c, ohfy__Invoice_Date__c, "
        "ohfy__Subtotal__c, ohfy__Customer__r.Name "
        "FROM ohfy__Invoice__c "
        "WHERE ohfy__External_ID__c LIKE 'INV-%' "
        "AND Name LIKE 'a0%'"
    )

    if not records:
        print("  No invoices with ID-like names. Nothing to fix!")
        return

    print(f"  Found {len(records):,} invoices with ID-like names")

    # Build update CSV, sorted by External_ID to group by invoice
    rows = []
    for r in records:
        cust_name = (r.get("ohfy__Customer__r") or {}).get("Name", "Unknown")
        inv_date = r.get("ohfy__Invoice_Date__c", "")
        subtotal = r.get("ohfy__Subtotal__c") or 0

        display_date = ""
        if inv_date:
            parts = inv_date.split("-")
            if len(parts) == 3:
                display_date = f"{int(parts[1])}/{int(parts[2])}/{parts[0]}"

        invoice_name = f"{cust_name} {display_date} - ${subtotal:,.2f}"
        if len(invoice_name) > 80:
            invoice_name = invoice_name[:80]

        rows.append(
            {
                "Name": invoice_name,
                "ohfy__External_ID__c": r["ohfy__External_ID__c"],
            }
        )

    rows.sort(key=lambda x: x["ohfy__External_ID__c"])

    csv_path = OUTPUT_DIR / "Invoice_Name_Fix.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "ohfy__External_ID__c"], lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Generated {csv_path} with {len(rows):,} records")
    print(f"  Sample: {rows[0]['ohfy__External_ID__c']} → {rows[0]['Name']}")

    run_sf_upsert("ohfy__Invoice__c", csv_path, "ohfy__External_ID__c")


def fix_invoice_item_names():
    """Fix Invoice Item Names where Name is just the SF ID.

    Loops to handle >50k records (SOQL governor limit).
    Sorts by External_ID to reduce lock contention on parent rollups.
    """
    print("\n=== Fix Invoice Item Names ===")

    batch = 0
    total_fixed = 0

    while True:
        batch += 1
        print(f"\n  --- Batch {batch} ---")
        print("  Querying invoice items with ID-like names...")

        records = run_sf_query(
            "SELECT Name, ohfy__External_ID__c, ohfy__Item__r.Name "
            "FROM ohfy__Invoice_Item__c "
            "WHERE ohfy__External_ID__c LIKE 'INV-%' "
            "AND Name LIKE 'a0%' "
            "ORDER BY ohfy__External_ID__c "
            "LIMIT 50000"
        )

        if not records:
            print("  No more invoice items with ID-like names!")
            break

        print(f"  Found {len(records):,} invoice items to fix")

        # Build update CSV, sorted by External_ID (already sorted by SOQL)
        rows = []
        for r in records:
            item_name = (r.get("ohfy__Item__r") or {}).get("Name", "Unknown")
            if len(item_name) > 80:
                item_name = item_name[:80]
            rows.append(
                {
                    "Name": item_name,
                    "ohfy__External_ID__c": r["ohfy__External_ID__c"],
                }
            )

        csv_path = OUTPUT_DIR / "Invoice_Item_Name_Fix.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "ohfy__External_ID__c"], lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)

        print(f"  Generated {csv_path} with {len(rows):,} records")
        print(f"  Sample: {rows[0]['ohfy__External_ID__c']} → {rows[0]['Name']}")

        run_sf_upsert("ohfy__Invoice_Item__c", csv_path, "ohfy__External_ID__c")
        total_fixed += len(rows)

        # If we got fewer than 50k, we're done
        if len(records) < 50000:
            break

        print("  Pausing 5s before next batch...")
        time.sleep(5)

    print(f"\n  Total invoice items processed: {total_fixed:,}")


def main():
    print("=" * 60)
    print("Fix Invoice Names — Update ID-like Names Only")
    print("=" * 60)

    fix_invoice_names()
    fix_invoice_item_names()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
