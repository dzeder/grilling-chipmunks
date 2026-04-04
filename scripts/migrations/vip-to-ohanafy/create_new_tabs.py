#!/usr/bin/env python3
"""
Create new Google Sheets tabs for objects identified in the data coverage audit.

New tabs:
  - Promotion_Items      (from DISCOUTT — item-level promo linkage)
  - Promotion_Item_Types (from DISCOUTT × ITEMT — brand-level promo linkage)
  - Promotion_Item_Lines (from DISCOUTT × ITEMT — supplier-level promo linkage)
  - Display_Runs         (VIP has no source data — creates empty template)
  - Displays             (VIP has no source data — creates empty template)
  - Display_Items        (VIP has no source data — creates empty template)
  - Billbacks            (VIP has no explicit billback table — creates empty template)

Usage:
    python3 create_new_tabs.py                # Write to Google Sheets + CSV
    python3 create_new_tabs.py --csv-only     # CSV only
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from decimal import Decimal

import gspread
import psycopg2
import psycopg2.extras
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Configuration (mirrors vip_to_ohanafy.py)
# ---------------------------------------------------------------------------
CONFIG_DIR = Path("/Users/danielzeder/conductor/repos/VIP to Ohanafy")
DEFAULT_SHEET_ID = "108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE"
SERVICE_ACCOUNT_PATH = CONFIG_DIR / "service-account.json"

DB_CONFIG = {
    "host": os.getenv("PGHOST", "gulfstream-db2-data.postgres.database.azure.com"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "gulfstream"),
    "user": os.getenv("PGUSER", "ohanafy"),
    "password": os.getenv("PGPASSWORD", "Xq7!mR#2vK$9pLw@nZ"),
    "sslmode": "require",
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

OUTPUT_DIR = Path(__file__).parent / "migration_output"


# ---------------------------------------------------------------------------
# Helpers (copied from vip_to_ohanafy.py for standalone use)
# ---------------------------------------------------------------------------
def safe_str(val):
    if val is None:
        return ""
    if isinstance(val, Decimal):
        if val == int(val):
            return str(int(val))
        return str(val)
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    return str(val).strip()


def vip_date_to_sf(numeric_date):
    if not numeric_date or numeric_date == 0:
        return ""
    try:
        d = str(int(numeric_date))
        if len(d) == 8:
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    except (ValueError, TypeError):
        pass
    return ""


def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def run_query(conn, sql):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql)
        return cur.fetchall()


def get_sheets_client():
    sa_paths = [
        SERVICE_ACCOUNT_PATH,
        Path(__file__).parent / "service-account.json",
    ]
    for p in sa_paths:
        if p.exists():
            creds = Credentials.from_service_account_file(str(p), scopes=SCOPES)
            return gspread.authorize(creds)
    raise FileNotFoundError(f"Service account not found: {[str(p) for p in sa_paths]}")


def write_tab(spreadsheet, tab_name, headers, friendly_headers, data_rows, retries=3):
    """Write headers + data to a sheet tab."""
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=tab_name,
            rows=max(len(data_rows) + 10, 100),
            cols=len(headers) + 2,
        )

    header_rows = 2 if friendly_headers else 1
    needed_rows = len(data_rows) + header_rows + 1
    needed_cols = len(headers) + 1
    if ws.row_count < needed_rows or ws.col_count < needed_cols:
        ws.resize(rows=max(needed_rows, 100), cols=max(needed_cols, 20))

    if friendly_headers:
        all_data = [friendly_headers, headers] + data_rows
    else:
        all_data = [headers] + data_rows

    batch_size = 1000
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i : i + batch_size]
        start_row = i + 1
        for attempt in range(retries):
            try:
                ws.update(range_name=f"A{start_row}", values=batch)
                break
            except gspread.exceptions.APIError as e:
                if "RATE_LIMIT" in str(e) or "429" in str(e):
                    wait = (attempt + 1) * 30
                    print(f"    Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        if i + batch_size < len(all_data):
            time.sleep(1)

    print(f"    {tab_name}: {len(data_rows)} rows written")
    return ws


def export_csv(tab_name, headers, data_rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / f"{tab_name}.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)
    print(f"    {filepath.name}: {len(data_rows)} rows")


# ---------------------------------------------------------------------------
# Tab definitions
# ---------------------------------------------------------------------------
TABS = []


def register_tab(name, headers, friendly_headers=None, sql=None, transform=None, template_only=False):
    TABS.append(
        {
            "name": name,
            "headers": headers,
            "friendly_headers": friendly_headers,
            "sql": sql,
            "transform": transform,
            "template_only": template_only,
        }
    )


# ===== 1. Promotion_Items =====
# Each DISCOUTT row already has an item. This creates the Promotion_Item child records
# linking each Promotion to its Item with discount pricing from DSINDT.
register_tab(
    name="Promotion_Items",
    sql="""
        SELECT
            d."IDENTITY"                      AS promo_identity,
            TRIM(d."PRODID")                  AS item_code,
            TRIM(d."DISCCODE")                AS discount_code,
            TRIM(d."CODEID")                  AS price_code,
            TRIM(d."TYPEID")                  AS discount_type,
            -- Get pricing from DSINDT if available
            ds."DIPRI1"                       AS price_tier1,
            ds."DIPRI2"                       AS price_tier2
        FROM staging."DISCOUTT" d
        LEFT JOIN staging."DSINDT" ds
            ON TRIM(d."PRODID") = TRIM(ds."DIITEM")
           AND TRIM(d."DISCCODE") = TRIM(ds."DIDSCD")
        WHERE d.import_is_deleted = false
        ORDER BY d."DISCCODE", d."PRODID"
    """,
    headers=[
        "ohfy__Promotion__c",
        "ohfy__Item__c",
        "ohfy__Discount_Dollars__c",
        "ohfy__Discount_Percent__c",
        "ohfy__Discounted_Case_Price__c",
        "ohfy__Type__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Promotion (lookup by Key)",
        "Item (lookup by External_ID)",
        "Discount $",
        "Discount %",
        "Discounted Case Price",
        "Type",
        "Key (External ID)",
    ],
    transform="promotion_items",
)

# ===== 2. Promotion_Item_Types =====
# Group promotions by Item Type (brand) — one record per unique promotion × item_type.
register_tab(
    name="Promotion_Item_Types",
    sql="""
        SELECT DISTINCT
            TRIM(d."DISCCODE")                AS discount_code,
            TRIM(d."CODEID")                  AS price_code,
            TRIM(d."TYPEID")                  AS discount_type,
            TRIM(i."BRAND_CODE")              AS brand_code,
            d."STARTDATE"                     AS start_date,
            d."ENDDATE"                       AS end_date
        FROM staging."DISCOUTT" d
        JOIN staging."ITEMT" i
            ON TRIM(d."PRODID") = TRIM(i."ITEM_CODE")
           AND i.import_is_deleted = false
        WHERE d.import_is_deleted = false
          AND TRIM(i."BRAND_CODE") <> ''
        ORDER BY discount_code, brand_code
    """,
    headers=[
        "ohfy__Promotion__c",
        "ohfy__Item_Type__c",
        "ohfy__Case_Quantity__c",
        "ohfy__Packaging_Type__c",
        "ohfy__Type__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Promotion (lookup — uses first item's promo Key)",
        "Item Type (lookup by Key)",
        "Case Quantity",
        "Packaging Type",
        "Type",
        "Key (External ID)",
    ],
    transform="promotion_item_types",
)

# ===== 3. Promotion_Item_Lines =====
# Group promotions by Item Line (supplier) — one record per unique promotion × supplier.
register_tab(
    name="Promotion_Item_Lines",
    sql="""
        SELECT DISTINCT
            TRIM(d."DISCCODE")                AS discount_code,
            TRIM(d."CODEID")                  AS price_code,
            TRIM(d."TYPEID")                  AS discount_type,
            TRIM(i."SUPPLIER_CODE")           AS supplier_code,
            d."STARTDATE"                     AS start_date,
            d."ENDDATE"                       AS end_date
        FROM staging."DISCOUTT" d
        JOIN staging."ITEMT" i
            ON TRIM(d."PRODID") = TRIM(i."ITEM_CODE")
           AND i.import_is_deleted = false
        WHERE d.import_is_deleted = false
          AND TRIM(i."SUPPLIER_CODE") <> ''
        ORDER BY discount_code, supplier_code
    """,
    headers=[
        "ohfy__Promotion__c",
        "ohfy__Item_Line__c",
        "ohfy__Case_Quantity__c",
        "ohfy__Packaging_Type__c",
        "ohfy__Type__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Promotion (lookup — uses first item's promo Key)",
        "Item Line (lookup by Key)",
        "Case Quantity",
        "Packaging Type",
        "Type",
        "Key (External ID)",
    ],
    transform="promotion_item_lines",
)

# ===== 4-6. Display templates (no VIP source data) =====
register_tab(
    name="Display_Runs",
    headers=[
        "Name",
        "ohfy__Chain_Banner__c",
        "ohfy__Start_Date__c",
        "ohfy__End_Date__c",
        "ohfy__Track_Days_Before__c",
        "ohfy__Track_Days_After__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Display Run Name",
        "Chain Banner (lookup)",
        "Start Date",
        "End Date",
        "Track Days Before",
        "Track Days After",
        "Key (External ID)",
    ],
    template_only=True,
)

register_tab(
    name="Displays",
    headers=[
        "Name",
        "ohfy__Account__c",
        "ohfy__Display_Run__c",
        "ohfy__Status__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Display Name",
        "Account (lookup)",
        "Display Run (lookup)",
        "Status",
        "Key (External ID)",
    ],
    template_only=True,
)

register_tab(
    name="Display_Items",
    headers=[
        "ohfy__Display__c",
        "ohfy__Item__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Display (lookup)",
        "Item (lookup)",
        "Key (External ID)",
    ],
    template_only=True,
)

# ===== 7. Billbacks template (no explicit VIP source) =====
register_tab(
    name="Billbacks",
    headers=[
        "Name",
        "ohfy__Incentive__c",
        "ohfy__Is_Active__c",
        "ohfy__Revenue_Amount__c",
        "ohfy__Total_Cases__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Billback Name",
        "Incentive (lookup)",
        "Active?",
        "Revenue Amount",
        "Total Cases",
        "Key (External ID)",
    ],
    template_only=True,
)


# ---------------------------------------------------------------------------
# Transform functions
# ---------------------------------------------------------------------------
def transform_promotion_items(rows):
    """Transform DISCOUTT × DSINDT → Promotion_Item rows."""
    type_map = {"P": "Post-Off", "F": "Front-Line", "S": "Special", "I": "Individual"}
    result = []
    for r in rows:
        item = safe_str(r.get("item_code", ""))
        disc_code = safe_str(r.get("discount_code", ""))
        price_code = safe_str(r.get("price_code", ""))
        promo_key = f"{disc_code}-{item}-{price_code}"
        dtype = safe_str(r.get("discount_type", ""))
        promo_type = type_map.get(dtype.upper(), "Discount")

        # Use DSINDT price tier 1 as the discounted case price if available
        price_tier1 = safe_str(r.get("price_tier1", ""))

        result.append(
            [
                promo_key,  # ohfy__Promotion__c (lookup by Key__c)
                item,  # ohfy__Item__c (lookup by External_ID)
                "",  # ohfy__Discount_Dollars__c (not in VIP source)
                "",  # ohfy__Discount_Percent__c (not in VIP source)
                price_tier1,  # ohfy__Discounted_Case_Price__c
                promo_type,  # ohfy__Type__c
                f"PI-{promo_key}",  # ohfy__Key__c
            ]
        )
    return result


def transform_promotion_item_types(rows):
    """Transform DISCOUTT × ITEMT → Promotion_Item_Type rows (brand-level)."""
    type_map = {"P": "Post-Off", "F": "Front-Line", "S": "Special", "I": "Individual"}
    result = []
    seen = set()
    for r in rows:
        disc_code = safe_str(r.get("discount_code", ""))
        price_code = safe_str(r.get("price_code", ""))
        brand_code = safe_str(r.get("brand_code", ""))
        dtype = safe_str(r.get("discount_type", ""))

        # Use the first item's promo key as the Promotion lookup
        # Promotions are keyed as {disc_code}-{item}-{price_code}
        # For type-level, we reference the discount code as the parent
        dedup_key = (disc_code, brand_code, price_code)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        promo_type = type_map.get(dtype.upper(), "Discount")
        result.append(
            [
                disc_code,  # ohfy__Promotion__c (needs resolution — discount code level)
                brand_code,  # ohfy__Item_Type__c (lookup by Key__c)
                "",  # ohfy__Case_Quantity__c
                "",  # ohfy__Packaging_Type__c
                promo_type,  # ohfy__Type__c
                f"PIT-{disc_code}-{brand_code}-{price_code}",  # ohfy__Key__c
            ]
        )
    return result


def transform_promotion_item_lines(rows):
    """Transform DISCOUTT × ITEMT → Promotion_Item_Line rows (supplier-level)."""
    type_map = {"P": "Post-Off", "F": "Front-Line", "S": "Special", "I": "Individual"}
    result = []
    seen = set()
    for r in rows:
        disc_code = safe_str(r.get("discount_code", ""))
        price_code = safe_str(r.get("price_code", ""))
        supplier_code = safe_str(r.get("supplier_code", ""))
        dtype = safe_str(r.get("discount_type", ""))

        dedup_key = (disc_code, supplier_code, price_code)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        promo_type = type_map.get(dtype.upper(), "Discount")
        result.append(
            [
                disc_code,  # ohfy__Promotion__c (needs resolution)
                supplier_code,  # ohfy__Item_Line__c (lookup by Key__c)
                "",  # ohfy__Case_Quantity__c
                "",  # ohfy__Packaging_Type__c
                promo_type,  # ohfy__Type__c
                f"PIL-{disc_code}-{supplier_code}-{price_code}",  # ohfy__Key__c
            ]
        )
    return result


TRANSFORM_MAP = {
    "Promotion_Items": transform_promotion_items,
    "Promotion_Item_Types": transform_promotion_item_types,
    "Promotion_Item_Lines": transform_promotion_item_lines,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Create new Ohanafy migration tabs")
    parser.add_argument("--csv-only", action="store_true", help="Export CSVs only")
    parser.add_argument("--sheet-id", default=DEFAULT_SHEET_ID, help="Google Sheet ID")
    args = parser.parse_args()

    print("=" * 60)
    print("Creating New Migration Tabs")
    print("=" * 60)

    # Connect to VIP database (needed for promo tabs)
    print("\n[1/3] Connecting to VIP database...")
    try:
        conn = get_db_connection()
        print("  Connected!")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # Extract and transform
    print("\n[2/3] Extracting data...")
    all_tab_data = []

    for tab in TABS:
        tab_name = tab["name"]
        print(f"\n  Processing: {tab_name}")

        if tab["template_only"]:
            print("    Template only (no VIP source data)")
            all_tab_data.append((tab_name, tab["headers"], tab.get("friendly_headers"), []))
            continue

        try:
            raw_rows = run_query(conn, tab["sql"])
            print(f"    Extracted {len(raw_rows)} raw rows")

            transform_fn = TRANSFORM_MAP.get(tab_name)
            if transform_fn:
                transformed = transform_fn(raw_rows)
            else:
                transformed = [[safe_str(v) for v in r.values()] for r in raw_rows]

            all_tab_data.append((tab_name, tab["headers"], tab.get("friendly_headers"), transformed))
            print(f"    Transformed to {len(transformed)} rows")

        except Exception as e:
            conn.rollback()
            print(f"    ERROR: {e}")
            all_tab_data.append((tab_name, tab["headers"], tab.get("friendly_headers"), []))

    conn.close()

    # Output
    print("\n[3/3] Writing output...")
    for tab_name, headers, friendly, data_rows in all_tab_data:
        export_csv(tab_name, headers, data_rows)

    if not args.csv_only:
        print("\n  Writing to Google Sheet...")
        gc = get_sheets_client()
        spreadsheet = gc.open_by_key(args.sheet_id)
        print(f"  Opened: {spreadsheet.title}")

        for tab_name, headers, friendly, data_rows in all_tab_data:
            write_tab(spreadsheet, tab_name, headers, friendly, data_rows)
            time.sleep(2)

        print(f"\n  Sheet: https://docs.google.com/spreadsheets/d/{args.sheet_id}")

    print("\n  Done!")
    print("\n  NOTE: Display_Runs, Displays, Display_Items, and Billbacks are")
    print("  empty templates — VIP has no source data for these objects.")
    print("  They'll need to be populated manually or from another source.")


if __name__ == "__main__":
    main()
