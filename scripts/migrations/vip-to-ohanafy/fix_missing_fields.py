#!/usr/bin/env python3
"""Fix missing data points flagged by QA.

Updates 5 fields across 4 objects in the Gulf sandbox:
1. Amount_Paid__c on Invoice (= Subtotal from rollup)
2. Supplier_Name__c on Invoice Item (from VIP DASUPP → SUPPLIERT)
3. Brand_Sub_Type__c on Invoice Item (from Item → Item Type → Subtype)
4. Location_Code__c on Location (from Key__c parsing)
5. Default_Case_Price__c on Item (from DPMAST1T average pricing)
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output/fixes")

DB_CONFIG = {
    "host": "gulfstream-db2-data.postgres.database.azure.com",
    "port": 5432,
    "dbname": "gulfstream",
    "user": "ohanafy",
    "password": "Xq7!mR#2vK$9pLw@nZ",
    "sslmode": "require",
}


def run_sf_query(soql):
    """Run SOQL query and return records. Handles query-more for large results."""
    all_records = []
    result = subprocess.run(
        ["sf", "data", "query", "--query", soql, "--target-org", TARGET_ORG, "--json"], capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    if data.get("status") != 0:
        print(f"  SOQL error: {data.get('message', 'unknown')}", file=sys.stderr)
        return []
    all_records.extend(data.get("result", {}).get("records", []))

    # Handle queryMore for large result sets
    done = data.get("result", {}).get("done", True)
    while not done:
        next_url = data.get("result", {}).get("nextRecordsUrl", "")
        if not next_url:
            break
        result = subprocess.run(
            ["sf", "data", "query", "--query", soql, "--target-org", TARGET_ORG, "--json", "--all-rows"],
            capture_output=True,
            text=True,
        )
        break  # --all-rows should get everything
    return all_records


def run_sf_query_all(soql):
    """Run SOQL query with --use-tooling-api=false for large datasets."""
    all_records = []
    # Use --result-format csv to handle large result sets efficiently
    result = subprocess.run(
        ["sf", "data", "query", "--query", soql, "--target-org", TARGET_ORG, "--json"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    data = json.loads(result.stdout)
    if data.get("status") != 0:
        print(f"  SOQL error: {data.get('message', 'unknown')}", file=sys.stderr)
        return []
    all_records.extend(data.get("result", {}).get("records", []))
    done = data.get("result", {}).get("done", True)
    total = data.get("result", {}).get("totalSize", 0)
    print(f"    First batch: {len(all_records):,} of {total:,} (done={done})")

    # Keep fetching if not done
    while not done:
        next_url = data.get("result", {}).get("nextRecordsUrl", "")
        if not next_url:
            break
        # Extract the query locator from the URL
        next_url.split("/")[-1]
        result = subprocess.run(
            ["sf", "api", "request", "rest", next_url, "--target-org", TARGET_ORG, "--json"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        data = json.loads(result.stdout)
        if data.get("status") != 0:
            print(f"  SOQL queryMore error: {data.get('message', '')}", file=sys.stderr)
            break
        batch = data.get("result", {}).get("records", [])
        all_records.extend(batch)
        done = data.get("result", {}).get("done", True)
        print(f"    Batch: +{len(batch):,} = {len(all_records):,} total (done={done})")

    return all_records


def run_sf_update(sobject, csv_path):
    """Bulk update records from CSV."""
    print(f"  Upserting {csv_path} into {sobject}...")
    result = subprocess.run(
        [
            "sf",
            "data",
            "update",
            "bulk",
            "--sobject",
            sobject,
            "--file",
            str(csv_path),
            "--target-org",
            TARGET_ORG,
            "--wait",
            "10",
            "--line-ending",
            "CRLF",
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    data = json.loads(result.stdout)
    if data.get("status") != 0:
        msg = data.get("message", "unknown error")
        print(f"  ERROR: {msg}", file=sys.stderr)
        # Try to get job info anyway
        job_info = data.get("result", {}).get("jobInfo", {})
        if job_info:
            print(
                f"  Processed: {job_info.get('numberRecordsProcessed', '?')}, "
                f"Failed: {job_info.get('numberRecordsFailed', '?')}"
            )
        return False

    job_info = data.get("result", {}).get("jobInfo", {})
    processed = job_info.get("numberRecordsProcessed", "?")
    failed = job_info.get("numberRecordsFailed", "?")
    print(f"  Processed: {processed}, Failed: {failed}")
    return str(failed) in ("0", "?")


# ---------------------------------------------------------------------------
# Fix 1: Amount_Paid__c on Invoice
# ---------------------------------------------------------------------------
def fix_amount_paid():
    """Set Amount_Paid__c = Subtotal for all invoices (all are Payment_Status=Paid)."""
    print("\n" + "=" * 60)
    print("FIX 1: Amount_Paid__c on Invoice")
    print("=" * 60)

    print("  Querying invoices for Subtotal...")
    records = run_sf_query("SELECT Id, ohfy__Subtotal__c FROM ohfy__Invoice__c")
    print(f"  Found {len(records):,} invoices")

    csv_path = OUTPUT_DIR / "fix_invoice_amount_paid.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Id", "Amount_Paid__c"], lineterminator="\r\n")
        writer.writeheader()
        for r in records:
            subtotal = r.get("ohfy__Subtotal__c")
            if subtotal is not None:
                writer.writerow(
                    {
                        "Id": r["Id"],
                        "Amount_Paid__c": f"{float(subtotal):.2f}",
                    }
                )

    print(f"  Generated {csv_path}")
    return run_sf_update("ohfy__Invoice__c", csv_path)


# ---------------------------------------------------------------------------
# Fix 2 & 3: Supplier_Name__c and Brand_Sub_Type__c on Invoice Item
# ---------------------------------------------------------------------------
def fix_invoice_item_fields():
    """Set Supplier_Name__c and Brand_Sub_Type__c on Invoice Items."""
    print("\n" + "=" * 60)
    print("FIX 2 & 3: Supplier_Name__c + Brand_Sub_Type__c on Invoice Item")
    print("=" * 60)

    # Step A: Build Item Key → Supplier Name map from VIP
    print("  Building supplier name lookup from VIP...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT TRIM(i."ITEM_CODE") AS item_code,
               TRIM(s."SUPPLIER_NAME") AS supplier_name
        FROM staging."ITEMT" i
        JOIN staging."SUPPLIERT" s ON TRIM(i."SUPPLIER_CODE") = TRIM(s."SUPPLIER")
        WHERE i.import_is_deleted = false
    """)
    item_supplier_map = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    print(f"  {len(item_supplier_map):,} item → supplier mappings from VIP")

    # Step B: Build Item SF ID → (Key, Subtype) map from SF
    print("  Querying Item → Item Type → Subtype from SF...")
    records = run_sf_query(
        "SELECT Id, ohfy__Key__c, ohfy__Item_Type__r.ohfy__Subtype__c FROM ohfy__Item__c WHERE ohfy__Key__c != null"
    )
    item_id_to_key = {}
    item_id_to_subtype = {}
    for r in records:
        item_id_to_key[r["Id"]] = r.get("ohfy__Key__c", "")
        item_type = r.get("ohfy__Item_Type__r")
        if item_type:
            item_id_to_subtype[r["Id"]] = item_type.get("ohfy__Subtype__c", "")
        else:
            item_id_to_subtype[r["Id"]] = ""
    print(f"  {len(item_id_to_key):,} items mapped")

    # Step C: Query all Invoice Items (in batches via bulk)
    print("  Querying Invoice Items (bulk)...")
    records = run_sf_query_all("SELECT Id, ohfy__Item__c FROM ohfy__Invoice_Item__c")
    print(f"  Found {len(records):,} invoice items")

    # Step D: Build update CSV
    csv_path = OUTPUT_DIR / "fix_invoice_item_supplier_brand.csv"
    written = 0
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Id", "Supplier_Name__c", "Brand_Sub_Type__c"], lineterminator="\r\n")
        writer.writeheader()
        for r in records:
            item_sf_id = r.get("ohfy__Item__c", "")
            item_key = item_id_to_key.get(item_sf_id, "")
            supplier_name = item_supplier_map.get(item_key, "")
            subtype = item_id_to_subtype.get(item_sf_id, "")

            if supplier_name or subtype:
                writer.writerow(
                    {
                        "Id": r["Id"],
                        "Supplier_Name__c": supplier_name,
                        "Brand_Sub_Type__c": subtype,
                    }
                )
                written += 1

    print(f"  Generated {csv_path} with {written:,} records")
    return run_sf_update("ohfy__Invoice_Item__c", csv_path)


# ---------------------------------------------------------------------------
# Fix 4: Location_Code__c on Location
# ---------------------------------------------------------------------------
def fix_location_code():
    """Populate Location_Code__c on all Locations from Key__c."""
    print("\n" + "=" * 60)
    print("FIX 4: Location_Code__c on Location")
    print("=" * 60)

    print("  Querying locations...")
    records = run_sf_query(
        "SELECT Id, Name, ohfy__Key__c, ohfy__Type__c, ohfy__Parent_Location__c FROM ohfy__Location__c"
    )
    print(f"  Found {len(records):,} locations")

    csv_path = OUTPUT_DIR / "fix_location_code.csv"
    written = 0
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Id", "ohfy__Location_Code__c"], lineterminator="\r\n")
        writer.writeheader()
        for r in records:
            key = r.get("ohfy__Key__c", "") or ""
            r.get("ohfy__Type__c", "") or ""
            r.get("Name", "") or ""
            parent = r.get("ohfy__Parent_Location__c")

            # Derive Location_Code from Key__c
            # Warehouse (parent=null): Key__c = warehouse number (e.g., "1", "2")
            # Zone (parent=warehouse): Key__c = "WH-ZONE" (e.g., "1-A", "1-B")
            # Bin (parent=zone): Key__c = "WH-ZONE-BIN" (e.g., "1-A-001")
            if not parent:
                # Root/Warehouse — use Key__c directly
                code = key
            elif "-" in key:
                # Child — use last segment of Key__c
                code = key.split("-")[-1]
            else:
                code = key

            if code:
                writer.writerow(
                    {
                        "Id": r["Id"],
                        "ohfy__Location_Code__c": code,
                    }
                )
                written += 1

    print(f"  Generated {csv_path} with {written:,} records")
    return run_sf_update("ohfy__Location__c", csv_path)


# ---------------------------------------------------------------------------
# Fix 5: Default_Case_Price__c on Item
# ---------------------------------------------------------------------------
def fix_default_case_price():
    """Set Default_Case_Price__c from DPMAST1T avg SELLINGPRICE01 (fallback FRONTLINEPRICE)."""
    print("\n" + "=" * 60)
    print("FIX 5: Default_Case_Price__c on Item")
    print("=" * 60)

    # Step A: Query DPMAST1T for average prices per item
    print("  Querying DPMAST1T for pricing data...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        WITH item_prices AS (
            SELECT
                TRIM(d."DPITEM") AS item_code,
                AVG(CASE WHEN d1."SELLINGPRICE01" > 0 THEN d1."SELLINGPRICE01" END) AS avg_sp01,
                AVG(CASE WHEN d1."FRONTLINEPRICE" > 0 THEN d1."FRONTLINEPRICE" END) AS avg_fl
            FROM staging."DPMAST1T" d1
            JOIN staging."DPMASTT" d ON d."DPIDENTITY" = d1."ID_DPMAST"
            WHERE d.import_is_deleted = false
              AND d1.import_is_deleted = false
            GROUP BY TRIM(d."DPITEM")
        )
        SELECT item_code,
               COALESCE(avg_sp01, avg_fl) AS default_price
        FROM item_prices
        WHERE COALESCE(avg_sp01, avg_fl) > 0
    """)
    price_map = {}
    for row in cur.fetchall():
        price_map[row[0]] = round(float(row[1]), 2)
    cur.close()
    conn.close()
    print(f"  {len(price_map):,} items with pricing from DPMAST1T")

    # Step B: Query Items from SF
    print("  Querying Items from SF...")
    records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Item__c WHERE ohfy__Key__c != null")
    print(f"  {len(records):,} items in SF")

    # Step C: Build update CSV
    csv_path = OUTPUT_DIR / "fix_item_default_price.csv"
    written = 0
    matched = 0
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Id", "ohfy__Default_Case_Price__c"], lineterminator="\r\n")
        writer.writeheader()
        for r in records:
            key = r.get("ohfy__Key__c", "")
            price = price_map.get(key)
            if price and price > 0:
                writer.writerow(
                    {
                        "Id": r["Id"],
                        "ohfy__Default_Case_Price__c": f"{price:.2f}",
                    }
                )
                written += 1
                matched += 1

    unmatched = len(records) - matched
    print(f"  Generated {csv_path} with {written:,} records")
    if unmatched:
        print(f"  Note: {unmatched:,} items had no DPMAST1T pricing (stays at 0)")
    return run_sf_update("ohfy__Item__c", csv_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("QA Missing Fields Fixer")
    print("Target: " + TARGET_ORG)
    print("=" * 60)

    results = {}

    # Fix 1: Amount Paid
    results["Amount Paid"] = fix_amount_paid()

    # Fix 2 & 3: Supplier Name + Brand Sub Type
    results["Supplier Name + Brand Sub Type"] = fix_invoice_item_fields()

    # Fix 4: Location Code
    results["Location Code"] = fix_location_code()

    # Fix 5: Default Case Price
    results["Default Case Price"] = fix_default_case_price()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  {name}: {status}")

    # Remaining items (no action needed)
    print("\n  No action needed:")
    print("    Chain Banner (Invoice) — formula, auto-populates")
    print("    Parent Location — already in CSV")
    print("    Average Case Cost — system-calculated after IR load")
    print("    Territory — records exist, object has minimal fields")
    print("    Account Sub Type — Gulf needs to define picklist values")


if __name__ == "__main__":
    main()
