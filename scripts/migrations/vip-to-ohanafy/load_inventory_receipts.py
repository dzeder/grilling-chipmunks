#!/usr/bin/env python3
"""Load Inventory Receipts + IR Items mirroring the loaded Purchase Orders.

For historical data, each PO gets exactly one IR, and each PO Item gets
exactly one IR Item with matching quantities and costs.

Step 1: Query PO headers and items from SF
Step 2: Build and load IR Header CSV (1 IR per PO)
Step 3: Query back IR SF IDs
Step 4: Build and load IR Item CSV (1 IR Item per PO Item)
Step 5: Validate
"""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")
SUPPLIER_CODES = ["3M", "3N", "2F", "2U", "1C"]
IR_RECORD_TYPE_ID = "012al000005RF2DAAW"


# ---------------------------------------------------------------------------
# Salesforce helpers
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
# Step 1: Query PO data from SF
# ---------------------------------------------------------------------------
def step1_query_po_data():
    """Query all PO headers and PO items from the sandbox."""
    print("\n=== Step 1: Query PO Data from SF ===")

    # PO headers — query by supplier to handle volume
    po_headers = {}  # PO SF Id → {name, supplier_id, date, receipt_date, location_id}
    for code in SUPPLIER_CODES:
        records = run_sf_query(
            f"SELECT Id, Name, ohfy__Supplier__c, "
            f"ohfy__Purchase_Order_Date__c, ohfy__Expected_Delivery_Date__c, "
            f"ohfy__Fulfillment_Location__c "
            f"FROM ohfy__Purchase_Order__c "
            f"WHERE ohfy__Supplier__r.ohfy__Customer_Number__c = '{code}'"
        )
        for r in records:
            po_headers[r["Id"]] = {
                "name": r["Name"],
                "supplier_id": r["ohfy__Supplier__c"],
                "po_date": r["ohfy__Purchase_Order_Date__c"],
                "receipt_date": r["ohfy__Expected_Delivery_Date__c"],
                "location_id": r["ohfy__Fulfillment_Location__c"],
            }
        print(f"  {code}: {len(records):,} PO headers")
    print(f"  Total: {len(po_headers):,} PO headers")

    # PO items — query by supplier in batches
    po_items = []  # list of {po_id, item_id, ordered_qty, received_qty, case_price, sort_order}
    for code in SUPPLIER_CODES:
        records = run_sf_query(
            f"SELECT Id, ohfy__Purchase_Order__c, ohfy__Item__c, "
            f"ohfy__Ordered_Case_Quantity__c, ohfy__Received_Case_Quantity__c, "
            f"ohfy__Case_Price__c, ohfy__Sort_Order__c "
            f"FROM ohfy__Purchase_Order_Item__c "
            f"WHERE ohfy__Purchase_Order__r.ohfy__Supplier__r.ohfy__Customer_Number__c = '{code}'"
        )
        for r in records:
            po_items.append(
                {
                    "po_id": r["ohfy__Purchase_Order__c"],
                    "item_id": r["ohfy__Item__c"],
                    "ordered_qty": r.get("ohfy__Ordered_Case_Quantity__c") or 0,
                    "received_qty": r.get("ohfy__Received_Case_Quantity__c") or 0,
                    "case_price": r.get("ohfy__Case_Price__c") or 0,
                    "sort_order": r.get("ohfy__Sort_Order__c") or 0,
                }
            )
        print(f"  {code}: {len(records):,} PO items")
    print(f"  Total: {len(po_items):,} PO items")

    return po_headers, po_items


# ---------------------------------------------------------------------------
# Step 2: Build and load IR Headers
# ---------------------------------------------------------------------------
def step2_build_and_load_ir_headers(po_headers):
    """Create one IR per PO, write CSV, and load."""
    print("\n=== Step 2: Build & Load IR Headers ===")

    csv_path = OUTPUT_DIR / "Inventory_Receipts.csv"
    fieldnames = [
        "RecordTypeId",
        "ohfy__Purchase_Order__c",
        "ohfy__Supplier__c",
        "ohfy__Inventory_Receipt_Date__c",
        "ohfy__Status__c",
        "ohfy__Payment_Status__c",
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()

        for po_id, po in sorted(po_headers.items(), key=lambda x: x[1]["name"]):
            # Use receipt date if available, fall back to PO date
            ir_date = po["receipt_date"] or po["po_date"] or ""

            writer.writerow(
                {
                    "RecordTypeId": IR_RECORD_TYPE_ID,
                    "ohfy__Purchase_Order__c": po_id,
                    "ohfy__Supplier__c": po["supplier_id"],
                    "ohfy__Inventory_Receipt_Date__c": ir_date,
                    "ohfy__Status__c": "Complete",
                    "ohfy__Payment_Status__c": "Paid",
                }
            )

    print(f"  Generated {csv_path} with {len(po_headers):,} records")
    run_sf_import("ohfy__Inventory_Receipt__c", csv_path)

    return csv_path


# ---------------------------------------------------------------------------
# Step 3: Query back IR SF IDs
# ---------------------------------------------------------------------------
def step3_fetch_ir_ids():
    """Query all IR headers and build PO SF ID → IR SF ID map."""
    print("\n=== Step 3: Fetch IR SF IDs ===")
    time.sleep(3)

    # Query IRs by supplier
    ir_map = {}  # PO SF ID → IR SF ID
    for code in SUPPLIER_CODES:
        records = run_sf_query(
            f"SELECT Id, ohfy__Purchase_Order__c "
            f"FROM ohfy__Inventory_Receipt__c "
            f"WHERE ohfy__Purchase_Order__r.ohfy__Supplier__r.ohfy__Customer_Number__c = '{code}'"
        )
        for r in records:
            ir_map[r["ohfy__Purchase_Order__c"]] = r["Id"]
        print(f"  {code}: {len(records):,} IR headers")

    print(f"  Total: {len(ir_map):,} IR headers resolved")
    return ir_map


# ---------------------------------------------------------------------------
# Step 4: Build and load IR Items
# ---------------------------------------------------------------------------
def step4_build_and_load_ir_items(po_items, ir_map):
    """Create one IR Item per PO Item, write CSV, and load."""
    print("\n=== Step 4: Build & Load IR Items ===")

    csv_path = OUTPUT_DIR / "Inventory_Receipt_Items.csv"
    fieldnames = [
        "ohfy__Inventory_Receipt__c",
        "ohfy__Item__c",
        "ohfy__Case_Quantity__c",
        "ohfy__Case_Price__c",
        "ohfy__Sort_Order__c",
    ]

    written = 0
    skipped_no_ir = 0

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()

        for poi in po_items:
            ir_id = ir_map.get(poi["po_id"])
            if not ir_id:
                skipped_no_ir += 1
                continue

            # For historicals: IR quantity = PO ordered quantity (fully received)
            qty = poi["ordered_qty"]
            price = poi["case_price"]

            writer.writerow(
                {
                    "ohfy__Inventory_Receipt__c": ir_id,
                    "ohfy__Item__c": poi["item_id"],
                    "ohfy__Case_Quantity__c": qty,
                    "ohfy__Case_Price__c": f"{float(price):.4f}" if price else "0.0000",
                    "ohfy__Sort_Order__c": int(poi["sort_order"]) if poi["sort_order"] else 0,
                }
            )
            written += 1

    print(f"  Generated {csv_path} with {written:,} records")
    if skipped_no_ir:
        print(f"  WARNING: {skipped_no_ir:,} items skipped (IR header not found)")

    if written > 0:
        run_sf_import("ohfy__Inventory_Receipt_Item__c", csv_path)

    return written


# ---------------------------------------------------------------------------
# Step 5: Validate
# ---------------------------------------------------------------------------
def step5_validate():
    """Spot-check loaded records."""
    print("\n=== Step 5: Validate ===")

    # Count IR headers
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Inventory_Receipt__c")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  IR Headers in org: {count}")

    # Count IR items
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Inventory_Receipt_Item__c")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  IR Items in org: {count}")

    # Breakdown by supplier
    records = run_sf_query(
        "SELECT ohfy__Supplier__r.Name suppName, COUNT(Id) cnt "
        "FROM ohfy__Inventory_Receipt__c "
        "GROUP BY ohfy__Supplier__r.Name "
        "ORDER BY COUNT(Id) DESC"
    )
    print("  IR headers by supplier:")
    for r in records:
        name = r.get("suppName", r.get("ohfy__Supplier__r", {}).get("Name", "?"))
        print(f"    {name}: {r.get('cnt', r.get('expr0', '?'))}")

    # Spot-check: compare a PO to its IR
    samples = run_sf_query(
        "SELECT Name, ohfy__Purchase_Order__r.Name, "
        "ohfy__Inventory_Receipt_Date__c, ohfy__Status__c, "
        "ohfy__Case_Quantity_Received__c, ohfy__Subtotal__c "
        "FROM ohfy__Inventory_Receipt__c "
        "ORDER BY ohfy__Inventory_Receipt_Date__c DESC LIMIT 3"
    )
    print("  Sample IR headers:")
    for s in samples:
        po_name = s.get("ohfy__Purchase_Order__r", {}).get("Name", "?") if s.get("ohfy__Purchase_Order__r") else "?"
        print(
            f"    {s.get('Name', '?')}: PO={po_name} "
            f"date={s.get('ohfy__Inventory_Receipt_Date__c', '?')} "
            f"status={s.get('ohfy__Status__c', '?')} "
            f"qty={s.get('ohfy__Case_Quantity_Received__c', '?')} "
            f"subtotal={s.get('ohfy__Subtotal__c', '?')}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Inventory Receipts — Mirroring POs (Historicals)")
    print("=" * 60)

    po_headers, po_items = step1_query_po_data()
    step2_build_and_load_ir_headers(po_headers)
    ir_map = step3_fetch_ir_ids()
    step4_build_and_load_ir_items(po_items, ir_map)
    step5_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
