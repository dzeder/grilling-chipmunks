#!/usr/bin/env python3
"""Load Purchase Orders (headers + line items) for 5 pilot suppliers.

Reads VIP PODTLT (PO detail/line table) from 2025-01-01 onward,
reconstructs PO headers, and loads into Ohanafy sandbox.

Step 1: Pre-fetch SF lookup IDs (Supplier Accounts, Items, Locations)
Step 2: Query VIP PODTLT for 2025+ PO data
Step 3: Build PO Header CSV and load into SF
Step 4: Query back PO Header SF IDs
Step 5: Build PO Line Item CSV and load into SF
Step 6: Validate
"""

import csv
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import psycopg2
import psycopg2.extras

TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")
SUPPLIER_CODES = ["3M", "3N", "2F", "2U", "1C"]
PO_RECORD_TYPE_ID = "012al000005RF1vAAG"
MIN_PO_DATE = 20250101  # YYYYMMDD numeric format in VIP

# VIP status → Ohanafy status mapping
STATUS_MAP = {
    "0": "New",
    "1": "Scheduled",
    "3": "In Progress",
    "4": "Complete",
    "9": "Complete",
}
# Priority for deriving header status from lines (higher = takes precedence)
STATUS_PRIORITY = {"0": 0, "1": 1, "3": 2, "4": 3, "9": 4}

DB_CONFIG = {
    "host": os.getenv("PGHOST", "gulfstream-db2-data.postgres.database.azure.com"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "gulfstream"),
    "user": os.getenv("PGUSER", "ohanafy"),
    "password": os.getenv("PGPASSWORD", "Xq7!mR#2vK$9pLw@nZ"),
    "sslmode": "require",
}


# ---------------------------------------------------------------------------
# Salesforce helpers (same pattern as load_keg_shells_and_components.py)
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


def format_vip_date(numeric_date):
    """Convert VIP numeric date (YYYYMMDD) to YYYY-MM-DD string."""
    if not numeric_date or int(numeric_date) <= 0:
        return ""
    s = str(int(numeric_date))
    if len(s) != 8:
        return ""
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


# ---------------------------------------------------------------------------
# Step 1: Pre-fetch SF lookup IDs
# ---------------------------------------------------------------------------
def step1_prefetch_ids():
    """Query sandbox for Supplier, Item, and Location SF IDs."""
    print("\n=== Step 1: Pre-fetch SF Lookup IDs ===")

    # Supplier Accounts
    codes_str = ",".join(f"'{c}'" for c in SUPPLIER_CODES)
    records = run_sf_query(
        f"SELECT Id, Name, ohfy__Customer_Number__c "
        f"FROM Account "
        f"WHERE ohfy__Customer_Number__c IN ({codes_str}) AND Type = 'Supplier'"
    )
    supplier_map = {}
    for r in records:
        code = r["ohfy__Customer_Number__c"]
        supplier_map[code] = r["Id"]
        print(f"  Supplier: {r['Name']:30s} code={code} → {r['Id']}")

    missing = set(SUPPLIER_CODES) - set(supplier_map.keys())
    if missing:
        print(f"  MISSING suppliers: {missing}", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(supplier_map)} suppliers resolved")

    # Items (Key__c = VIP item code)
    print("  Querying Items...")
    records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Item__c WHERE ohfy__Key__c != null")
    item_map = {r["ohfy__Key__c"]: r["Id"] for r in records}
    print(f"  {len(item_map)} Items resolved")

    # Locations (Key__c = warehouse number)
    print("  Querying Locations...")
    records = run_sf_query("SELECT Id, Name, ohfy__Key__c FROM ohfy__Location__c WHERE ohfy__Key__c != null")
    location_map = {r["ohfy__Key__c"]: r["Id"] for r in records}
    for r in records:
        if r["ohfy__Key__c"] and not r["ohfy__Key__c"].startswith("1-"):  # Skip zones
            print(f"  Location: {r['Name']:30s} key={r['ohfy__Key__c']} → {r['Id']}")
    print(f"  {len(location_map)} Locations resolved")

    return supplier_map, item_map, location_map


# ---------------------------------------------------------------------------
# Step 2: Query VIP PODTLT
# ---------------------------------------------------------------------------
def step2_query_vip():
    """Query VIP PO detail lines for 5 suppliers from 2025 onward."""
    print("\n=== Step 2: Query VIP PODTLT ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    codes_str = ",".join(f"'{c}'" for c in SUPPLIER_CODES)
    sql = f"""
        SELECT
            TRIM(p."PDPO#") as po_number,
            p."PDLINE" as line_seq,
            TRIM(p."PDITEM") as item_code,
            p."PDOQTY" as ordered_qty,
            p."PDRQTY" as received_qty,
            p."PDCST$" as cost,
            p."PDDATE" as po_date,
            p."PDRDAT" as receipt_date,
            TRIM(p."PDSTAT") as status,
            TRIM(p."PDWHSE") as warehouse,
            TRIM(i."SUPPLIER_CODE") as supplier_code
        FROM staging."PODTLT" p
        JOIN staging."ITEMT" i ON TRIM(p."PDITEM") = TRIM(i."ITEM_CODE")
        WHERE p."PDDATE" >= {MIN_PO_DATE}
          AND TRIM(i."SUPPLIER_CODE") IN ({codes_str})
        ORDER BY p."PDPO#", i."SUPPLIER_CODE", p."PDLINE"
    """
    cur.execute(sql)
    rows = cur.fetchall()
    print(f"  Fetched {len(rows):,} PO lines from VIP")

    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Step 3: Build PO Headers and load
# ---------------------------------------------------------------------------
def step3_build_and_load_headers(vip_rows, supplier_map, item_map, location_map):
    """Group VIP lines into PO headers, generate CSV, and load."""
    print("\n=== Step 3: Build & Load PO Headers ===")

    # Group lines by (po_number, supplier_code) to create headers
    po_groups = defaultdict(list)
    skipped_no_item = 0

    for row in vip_rows:
        item_code = row["item_code"]
        if item_code not in item_map:
            skipped_no_item += 1
            continue
        key = (row["po_number"], row["supplier_code"])
        po_groups[key].append(row)

    if skipped_no_item:
        print(f"  Skipped {skipped_no_item:,} lines (item not in SF)")
    print(f"  {len(po_groups):,} PO headers to create")

    # Build header records
    headers = []
    for (po_num, supp_code), lines in sorted(po_groups.items()):
        # Derive header fields from lines
        min_date = min(int(l["po_date"]) for l in lines if int(l["po_date"]) > 0)
        receipt_dates = [int(l["receipt_date"]) for l in lines if int(l["receipt_date"]) > 0]
        max_receipt = max(receipt_dates) if receipt_dates else 0

        # Status: use highest-priority status across lines
        line_statuses = [l["status"] for l in lines if l["status"]]
        if line_statuses:
            best_status = max(line_statuses, key=lambda s: STATUS_PRIORITY.get(s, -1))
            ohanafy_status = STATUS_MAP.get(best_status, "New")
        else:
            ohanafy_status = "New"

        # Warehouse: use most common across lines
        whse_counts = defaultdict(int)
        for l in lines:
            if l["warehouse"]:
                whse_counts[l["warehouse"]] += 1
        predominant_whse = max(whse_counts, key=whse_counts.get) if whse_counts else ""
        location_id = location_map.get(predominant_whse, "")

        # Name: composite key for uniqueness
        name = f"{po_num}-{supp_code}" if len(po_num) + len(supp_code) + 1 <= 80 else po_num[:77]

        headers.append(
            {
                "RecordTypeId": PO_RECORD_TYPE_ID,
                "Name": name,
                "ohfy__Supplier__c": supplier_map[supp_code],
                "ohfy__Purchase_Order_Date__c": format_vip_date(min_date),
                "ohfy__Expected_Delivery_Date__c": format_vip_date(max_receipt),
                "ohfy__Customer_Reference_Number__c": po_num,
                "ohfy__Fulfillment_Location__c": location_id,
                "ohfy__Status__c": ohanafy_status,
            }
        )

    # Write CSV
    csv_path = OUTPUT_DIR / "Purchase_Orders.csv"
    fieldnames = [
        "RecordTypeId",
        "Name",
        "ohfy__Supplier__c",
        "ohfy__Purchase_Order_Date__c",
        "ohfy__Expected_Delivery_Date__c",
        "ohfy__Customer_Reference_Number__c",
        "ohfy__Fulfillment_Location__c",
        "ohfy__Status__c",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(headers)

    print(f"  Generated {csv_path} with {len(headers):,} records")

    # Load into SF
    run_sf_import("ohfy__Purchase_Order__c", csv_path)

    return po_groups


# ---------------------------------------------------------------------------
# Step 4: Query back PO Header SF IDs
# ---------------------------------------------------------------------------
def step4_fetch_po_ids():
    """Query all PO headers we just inserted and build Name → SF ID map."""
    print("\n=== Step 4: Fetch PO Header SF IDs ===")
    time.sleep(3)  # Brief wait for indexing

    # Query by supplier to avoid large result set issues
    po_id_map = {}  # Name → SF ID
    for code in SUPPLIER_CODES:
        records = run_sf_query(
            f"SELECT Id, Name FROM ohfy__Purchase_Order__c WHERE ohfy__Supplier__r.ohfy__Customer_Number__c = '{code}'"
        )
        for r in records:
            po_id_map[r["Name"]] = r["Id"]
        print(f"  {code}: {len(records):,} PO headers found")

    print(f"  Total: {len(po_id_map):,} PO headers resolved")
    return po_id_map


# ---------------------------------------------------------------------------
# Step 5: Build PO Line Items and load
# ---------------------------------------------------------------------------
def step5_build_and_load_items(po_groups, po_id_map, item_map):
    """Build PO line item CSV with resolved SF IDs and load."""
    print("\n=== Step 5: Build & Load PO Line Items ===")

    csv_path = OUTPUT_DIR / "Purchase_Order_Items.csv"
    fieldnames = [
        "ohfy__Purchase_Order__c",
        "ohfy__Item__c",
        "ohfy__Ordered_Case_Quantity__c",
        "ohfy__Received_Case_Quantity__c",
        "ohfy__Case_Price__c",
        "ohfy__Sort_Order__c",
    ]

    written = 0
    skipped_no_po = 0
    skipped_no_item = 0

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()

        for (po_num, supp_code), lines in sorted(po_groups.items()):
            po_name = f"{po_num}-{supp_code}" if len(po_num) + len(supp_code) + 1 <= 80 else po_num[:77]
            po_sf_id = po_id_map.get(po_name)

            if not po_sf_id:
                skipped_no_po += len(lines)
                continue

            for line in lines:
                item_sf_id = item_map.get(line["item_code"])
                if not item_sf_id:
                    skipped_no_item += 1
                    continue

                cost = float(line["cost"]) if line["cost"] else 0
                writer.writerow(
                    {
                        "ohfy__Purchase_Order__c": po_sf_id,
                        "ohfy__Item__c": item_sf_id,
                        "ohfy__Ordered_Case_Quantity__c": int(line["ordered_qty"]) if line["ordered_qty"] else 0,
                        "ohfy__Received_Case_Quantity__c": int(line["received_qty"]) if line["received_qty"] else 0,
                        "ohfy__Case_Price__c": f"{cost:.4f}",
                        "ohfy__Sort_Order__c": int(line["line_seq"]) if line["line_seq"] else 0,
                    }
                )
                written += 1

    print(f"  Generated {csv_path} with {written:,} records")
    if skipped_no_po:
        print(f"  WARNING: {skipped_no_po:,} lines skipped (PO header not found in SF)")
    if skipped_no_item:
        print(f"  WARNING: {skipped_no_item:,} lines skipped (item not in SF)")

    if written > 0:
        run_sf_import("ohfy__Purchase_Order_Item__c", csv_path)

    return written


# ---------------------------------------------------------------------------
# Step 6: Validate
# ---------------------------------------------------------------------------
def step6_validate():
    """Spot-check loaded records."""
    print("\n=== Step 6: Validate ===")

    # Count PO headers
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Purchase_Order__c")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  PO Headers in org: {count}")

    # Count PO line items
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Purchase_Order_Item__c")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  PO Line Items in org: {count}")

    # Breakdown by supplier
    records = run_sf_query(
        "SELECT ohfy__Supplier__r.Name suppName, COUNT(Id) cnt "
        "FROM ohfy__Purchase_Order__c "
        "GROUP BY ohfy__Supplier__r.Name "
        "ORDER BY COUNT(Id) DESC"
    )
    print("  PO headers by supplier:")
    for r in records:
        name = r.get("suppName", r.get("ohfy__Supplier__r", {}).get("Name", "?"))
        print(f"    {name}: {r.get('cnt', r.get('expr0', '?'))}")

    # Spot-check a sample PO
    samples = run_sf_query(
        "SELECT Name, ohfy__Customer_Reference_Number__c, "
        "ohfy__Purchase_Order_Date__c, ohfy__Status__c, "
        "ohfy__Supplier__r.Name, ohfy__Fulfillment_Location__r.Name, "
        "ohfy__Ordered_Case_Quantity__c, ohfy__Subtotal__c "
        "FROM ohfy__Purchase_Order__c "
        "ORDER BY ohfy__Purchase_Order_Date__c DESC LIMIT 3"
    )
    print("  Sample PO headers:")
    for s in samples:
        supp = s.get("ohfy__Supplier__r", {}).get("Name", "?") if s.get("ohfy__Supplier__r") else "?"
        loc = (
            s.get("ohfy__Fulfillment_Location__r", {}).get("Name", "?")
            if s.get("ohfy__Fulfillment_Location__r")
            else "?"
        )
        print(
            f"    {s.get('Name', '?')}: date={s.get('ohfy__Purchase_Order_Date__c', '?')} "
            f"status={s.get('ohfy__Status__c', '?')} supplier={supp} "
            f"location={loc} qty={s.get('ohfy__Ordered_Case_Quantity__c', '?')} "
            f"subtotal={s.get('ohfy__Subtotal__c', '?')}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Purchase Orders — 5 Pilot Suppliers (2025+)")
    print("=" * 60)

    supplier_map, item_map, location_map = step1_prefetch_ids()
    vip_rows = step2_query_vip()
    po_groups = step3_build_and_load_headers(vip_rows, supplier_map, item_map, location_map)
    po_id_map = step4_fetch_po_ids()
    step5_build_and_load_items(po_groups, po_id_map, item_map)
    step6_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
