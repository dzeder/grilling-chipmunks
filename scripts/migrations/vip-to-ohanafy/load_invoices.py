#!/usr/bin/env python3
"""Load Invoices (headers + line items) from VIP DAILYT for sandbox demo.

Reads VIP DAILYT (daily transaction ledger) type-1 records from 2025-03-01
onward, filters to customers and items already in the sandbox, and loads
Invoice headers and Invoice Items into Ohanafy.

Step 1: Pre-fetch SF lookup IDs (Customers, Items, Locations)
Step 2: Query VIP DAILYT for invoice data
Step 3: Filter, group, build Invoice Header CSV, and load
Step 4: Query back Invoice Header SF IDs
Step 5: Build Invoice Item CSV and load
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
ORDER_RECORD_TYPE_ID = "012al000005RF2BAAW"  # ohfy__Invoice__c → Order
CUSTOMER_RECORD_TYPE_ID = "012al000005RF20AAG"  # Account → Customer
MIN_INVOICE_DATE = 20250301  # YYYYMMDD — ~1 year of history

DB_CONFIG = {
    "host": os.getenv("PGHOST", "gulfstream-db2-data.postgres.database.azure.com"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "gulfstream"),
    "user": os.getenv("PGUSER", "ohanafy"),
    "password": os.getenv("PGPASSWORD", "Xq7!mR#2vK$9pLw@nZ"),
    "sslmode": "require",
}


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


def format_vip_date_display(numeric_date):
    """Convert VIP numeric date (YYYYMMDD) to M/D/YYYY for display."""
    if not numeric_date or int(numeric_date) <= 0:
        return ""
    s = str(int(numeric_date))
    if len(s) != 8:
        return ""
    return f"{int(s[4:6])}/{int(s[6:])}/{s[:4]}"


# ---------------------------------------------------------------------------
# Step 1: Pre-fetch SF Lookup IDs
# ---------------------------------------------------------------------------
def step1_prefetch_ids():
    """Query sandbox for Customer, Item, and Location SF IDs."""
    print("\n=== Step 1: Pre-fetch SF Lookup IDs ===")

    # Customer Accounts
    print("  Querying Customer accounts...")
    records = run_sf_query(
        f"SELECT Id, Name, ohfy__Customer_Number__c FROM Account WHERE RecordTypeId = '{CUSTOMER_RECORD_TYPE_ID}'"
    )
    customer_map = {}
    customer_name_map = {}
    for r in records:
        code = r.get("ohfy__Customer_Number__c")
        if code:
            key = code.strip()
            customer_map[key] = r["Id"]
            customer_name_map[key] = r.get("Name", "")
    print(f"  {len(customer_map)} Customer accounts resolved")

    # Items (Key__c = VIP item code, must be active for lookup filter)
    print("  Querying Items...")
    records = run_sf_query(
        "SELECT Id, Name, ohfy__Key__c FROM ohfy__Item__c WHERE ohfy__Key__c != null AND ohfy__Is_Active__c = true"
    )
    item_map = {r["ohfy__Key__c"]: r["Id"] for r in records}
    item_name_map = {r["ohfy__Key__c"]: r.get("Name", "") for r in records}
    print(f"  {len(item_map)} active Items resolved")

    # Locations (Key__c = warehouse number)
    print("  Querying Locations...")
    records = run_sf_query("SELECT Id, Name, ohfy__Key__c FROM ohfy__Location__c WHERE ohfy__Key__c != null")
    location_map = {r["ohfy__Key__c"]: r["Id"] for r in records}
    print(f"  {len(location_map)} Locations resolved")

    return customer_map, customer_name_map, item_map, item_name_map, location_map


# ---------------------------------------------------------------------------
# Step 2: Query VIP DAILYT (server-side filtered to loaded customers+items)
# ---------------------------------------------------------------------------
def step2_query_vip(customer_map, item_map):
    """Query VIP DAILYT for type-1 records, filtered to loaded customers/items."""
    print("\n=== Step 2: Query VIP DAILYT ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Build IN-clause values for server-side filtering
    acct_codes = list(customer_map.keys())
    item_codes = list(item_map.keys())
    print(f"  Filtering to {len(acct_codes)} customers and {len(item_codes)} items")

    sql = """
        SELECT
            TRIM("DAINV#"::text)  AS invoice_number,
            TRIM("DAACCT")        AS account_code,
            TRIM("DAITEM")        AS item_code,
            "DAQTY"               AS case_qty,
            "DAUNIT"              AS unit_qty,
            "DAPRIC"              AS unit_price,
            "DADAMT"              AS line_amount,
            "DAFLPR"              AS frontline_price,
            "DAICOS"              AS item_cost,
            "DAIDAT"              AS invoice_date,
            "DASDAT"              AS ship_date,
            TRIM("DAWHSE")        AS warehouse,
            TRIM("DADR#")         AS route_number,
            TRIM("DALOAD")        AS load_id,
            TRIM("DAORD#")        AS order_number,
            TRIM("DATXCD")        AS tax_code,
            "DADEPO"              AS deposit_amount,
            "DALIN#"              AS line_number
        FROM staging."DAILYT"
        WHERE "DATYPE" = '1'
          AND "DAIDAT" >= %s
          AND import_is_deleted = false
          AND TRIM("DAACCT") = ANY(%s)
          AND TRIM("DAITEM") = ANY(%s)
        ORDER BY "DAINV#", "DALIN#"
    """
    cur.execute(sql, (MIN_INVOICE_DATE, acct_codes, item_codes))
    rows = cur.fetchall()
    print(f"  Fetched {len(rows):,} matching DAILYT rows (invoices since {MIN_INVOICE_DATE})")

    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Step 3: Filter, Group, Build Invoice Headers, Load
# ---------------------------------------------------------------------------
def step3_build_and_load_headers(vip_rows, customer_map, customer_name_map, item_map, location_map):
    """Group by invoice and build header CSV. Rows already filtered in SQL."""
    print("\n=== Step 3: Group & Load Invoice Headers ===")

    if not vip_rows:
        print("  ERROR: No matching rows found. Check customer/item overlap.")
        sys.exit(1)

    # Group by invoice_number
    invoice_groups = defaultdict(list)
    for row in vip_rows:
        invoice_groups[row["invoice_number"]].append(row)

    print(f"  {len(invoice_groups):,} unique invoices to create")

    # Build header records
    headers = []
    for inv_num, lines in sorted(invoice_groups.items()):
        first = lines[0]

        # Warehouse: most common across lines
        whse_counts = defaultdict(int)
        for l in lines:
            if l["warehouse"]:
                whse_counts[l["warehouse"]] += 1
        predominant_whse = max(whse_counts, key=whse_counts.get) if whse_counts else ""
        location_id = location_map.get(predominant_whse, "")

        # Compute invoice Name: "{Customer Name} {M/D/YYYY} - ${subtotal}"
        acct_code = first["account_code"]
        cust_name = customer_name_map.get(acct_code, acct_code)
        display_date = format_vip_date_display(first["invoice_date"])
        subtotal = sum(float(l["line_amount"]) if l["line_amount"] else 0.0 for l in lines)
        invoice_name = f"{cust_name} {display_date} - ${subtotal:,.2f}"
        if len(invoice_name) > 80:
            invoice_name = invoice_name[:80]

        headers.append(
            {
                "Name": invoice_name,
                "RecordTypeId": ORDER_RECORD_TYPE_ID,
                "ohfy__Customer__c": customer_map[first["account_code"]],
                "ohfy__Invoice_Date__c": format_vip_date(first["invoice_date"]),
                "ohfy__Status__c": "Complete",
                "ohfy__Payment_Status__c": "Paid",
                "ohfy__Fulfillment_Location__c": location_id,
                "ohfy__Delivery_Method__c": "Delivery",
                "ohfy__Is_External_Invoice__c": "TRUE",
                "ohfy__Delivery_Pickup_Date__c": format_vip_date(first["ship_date"]),
                "ohfy__Date_Completed__c": format_vip_date(first["invoice_date"]),
                "ohfy__Accounting_System_ID__c": inv_num,
                "ohfy__External_ID__c": f"INV-{inv_num}",
            }
        )

    # Write CSV
    csv_path = OUTPUT_DIR / "Invoices.csv"
    fieldnames = list(headers[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(headers)

    print(f"  Generated {csv_path} with {len(headers):,} records")

    # Load into SF
    run_sf_upsert("ohfy__Invoice__c", csv_path, "ohfy__External_ID__c")

    return invoice_groups


# ---------------------------------------------------------------------------
# Step 4: Query back Invoice Header SF IDs
# ---------------------------------------------------------------------------
def step4_fetch_invoice_ids():
    """Query all Invoice headers we just loaded and build External_ID → SF ID map."""
    print("\n=== Step 4: Fetch Invoice Header SF IDs ===")
    time.sleep(3)  # Brief wait for indexing

    invoice_id_map = {}  # External_ID → SF ID
    records = run_sf_query(
        "SELECT Id, ohfy__External_ID__c FROM ohfy__Invoice__c WHERE ohfy__External_ID__c LIKE 'INV-%'"
    )
    for r in records:
        invoice_id_map[r["ohfy__External_ID__c"]] = r["Id"]

    print(f"  {len(invoice_id_map):,} Invoice headers resolved")
    return invoice_id_map


# ---------------------------------------------------------------------------
# Step 5: Build Invoice Items and load
# ---------------------------------------------------------------------------
def step5_build_and_load_items(invoice_groups, invoice_id_map, item_map, item_name_map):
    """Build Invoice Item CSV with resolved SF IDs and load."""
    print("\n=== Step 5: Build & Load Invoice Items ===")

    csv_path = OUTPUT_DIR / "Invoice_Items.csv"
    fieldnames = [
        "Name",
        "ohfy__Invoice__c",
        "ohfy__Item__c",
        "ohfy__Invoiced_Case_Quantity__c",
        "ohfy__Invoiced_Unit_Quantity__c",
        "ohfy__Ordered_Case_Quantity__c",
        "ohfy__Ordered_Unit_Quantity__c",
        "ohfy__Case_Price__c",
        "ohfy__Is_New__c",
        "ohfy__Sort_Order__c",
        "ohfy__External_ID__c",
    ]

    written = 0
    skipped_no_invoice = 0
    skipped_no_item = 0

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()

        for inv_num, lines in sorted(invoice_groups.items()):
            ext_id = f"INV-{inv_num}"
            invoice_sf_id = invoice_id_map.get(ext_id)

            if not invoice_sf_id:
                skipped_no_invoice += len(lines)
                continue

            for line in lines:
                item_sf_id = item_map.get(line["item_code"])
                if not item_sf_id:
                    skipped_no_item += 1
                    continue

                case_qty = int(line["case_qty"]) if line["case_qty"] else 0
                unit_qty = int(line["unit_qty"]) if line["unit_qty"] else 0
                price = float(line["unit_price"]) if line["unit_price"] else 0
                line_num = int(line["line_number"]) if line["line_number"] else 0

                item_name = item_name_map.get(line["item_code"], line["item_code"])
                if len(item_name) > 80:
                    item_name = item_name[:80]

                writer.writerow(
                    {
                        "Name": item_name,
                        "ohfy__Invoice__c": invoice_sf_id,
                        "ohfy__Item__c": item_sf_id,
                        "ohfy__Invoiced_Case_Quantity__c": case_qty,
                        "ohfy__Invoiced_Unit_Quantity__c": unit_qty,
                        "ohfy__Ordered_Case_Quantity__c": case_qty,
                        "ohfy__Ordered_Unit_Quantity__c": unit_qty,
                        "ohfy__Case_Price__c": f"{price:.4f}",
                        "ohfy__Is_New__c": "FALSE",
                        "ohfy__Sort_Order__c": line_num,
                        "ohfy__External_ID__c": f"INV-{inv_num}-{line_num}",
                    }
                )
                written += 1

    print(f"  Generated {csv_path} with {written:,} records")
    if skipped_no_invoice:
        print(f"  WARNING: {skipped_no_invoice:,} lines skipped (invoice header not in SF)")
    if skipped_no_item:
        print(f"  WARNING: {skipped_no_item:,} lines skipped (item not in SF)")

    if written > 0:
        run_sf_upsert("ohfy__Invoice_Item__c", csv_path, "ohfy__External_ID__c")

    return written


# ---------------------------------------------------------------------------
# Step 6: Validate
# ---------------------------------------------------------------------------
def step6_validate():
    """Spot-check loaded records."""
    print("\n=== Step 6: Validate ===")

    # Count Invoice headers
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Invoice__c WHERE ohfy__External_ID__c LIKE 'INV-%'")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Invoice headers in org: {count}")

    # Count Invoice items
    records = run_sf_query("SELECT COUNT(Id) cnt FROM ohfy__Invoice_Item__c WHERE ohfy__External_ID__c LIKE 'INV-%'")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Invoice items in org: {count}")

    # Spot-check sample invoices
    samples = run_sf_query(
        "SELECT Name, ohfy__Invoice_Date__c, ohfy__Status__c, "
        "ohfy__Customer__r.Name, ohfy__Subtotal__c, "
        "ohfy__Total_Invoice_Items__c, ohfy__Fulfillment_Location__r.Name "
        "FROM ohfy__Invoice__c "
        "WHERE ohfy__External_ID__c LIKE 'INV-%' "
        "ORDER BY ohfy__Invoice_Date__c DESC LIMIT 5"
    )
    print("  Sample invoices:")
    for s in samples:
        cust = s.get("ohfy__Customer__r", {}).get("Name", "?") if s.get("ohfy__Customer__r") else "?"
        loc = (
            s.get("ohfy__Fulfillment_Location__r", {}).get("Name", "?")
            if s.get("ohfy__Fulfillment_Location__r")
            else "?"
        )
        print(
            f"    {s.get('Name', '?')}: date={s.get('ohfy__Invoice_Date__c', '?')} "
            f"status={s.get('ohfy__Status__c', '?')} customer={cust} "
            f"subtotal=${s.get('ohfy__Subtotal__c', '?')} "
            f"items={s.get('ohfy__Total_Invoice_Items__c', '?')} "
            f"location={loc}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Invoices — Sandbox Demo (DAILYT since 2025-03-01)")
    print("=" * 60)

    customer_map, customer_name_map, item_map, item_name_map, location_map = step1_prefetch_ids()
    vip_rows = step2_query_vip(customer_map, item_map)
    invoice_groups = step3_build_and_load_headers(vip_rows, customer_map, customer_name_map, item_map, location_map)
    invoice_id_map = step4_fetch_invoice_ids()
    step5_build_and_load_items(invoice_groups, invoice_id_map, item_map, item_name_map)
    step6_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
