#!/usr/bin/env python3
"""Load Customer accounts for 14 routes × 11 Chain Banners into Gulf sandbox.

Sandbox validation batch: ~259 customers filtered to routes that are loaded
AND chain banners that are loaded. Verifies all lookups resolve before upserting.
"""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import psycopg2
import psycopg2.extras
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")
CUSTOMER_RT = "012al000005RF20AAG"  # Account RecordType: Customer
CHAIN_BANNER_RT = "012al000005RF21AAG"  # Account RecordType: Chain Banner

SHEET_ID = "108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE"
SERVICE_ACCOUNT_PATH = Path("/Users/danielzeder/Desktop/VIP to Ohanafy/service-account.json")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DB_CONFIG = {
    "host": "gulfstream-db2-data.postgres.database.azure.com",
    "port": 5432,
    "dbname": "gulfstream",
    "user": "ohanafy",
    "password": "Xq7!mR#2vK$9pLw@nZ",
    "sslmode": "require",
}

ROUTE_CODES = ["104", "105", "107", "108", "109", "110", "111", "112", "113", "114", "115", "116", "117", "118"]

WAREHOUSE_TO_TERRITORY = {
    "1": "Mobile",
    "2": "Milton / Pensacola",
    "5": "Jackson",
    "6": "Gulfport",
    "7": "Montgomery",
    "9": "Birmingham",
    "10": "Huntsville",
    "11": "ABC Board",
    "99": "AL Liquor Sales",
    "J": "Jackson (Legacy)",
}


# ---------------------------------------------------------------------------
# Salesforce helpers (from load_5_supplier_products.py pattern)
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


# ---------------------------------------------------------------------------
# Transform helpers (from vip_to_ohanafy.py)
# ---------------------------------------------------------------------------
def safe_str(val):
    if val is None:
        return ""
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    return str(val).strip()


def format_phone(phone_num):
    if not phone_num:
        return ""
    try:
        p = str(int(phone_num)).strip()
        if len(p) == 10:
            return f"({p[:3]}) {p[3:6]}-{p[6:]}"
        if len(p) == 11 and p[0] == "1":
            return f"({p[1:4]}) {p[4:7]}-{p[7:]}"
    except (ValueError, TypeError):
        pass
    return str(phone_num) if phone_num else ""


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


def is_active(status_val):
    if not status_val:
        return "TRUE"
    s = str(status_val).strip().upper()
    return "FALSE" if s in ("I", "D", "X", "CLR", "N") else "TRUE"


def map_premise_type(on_off):
    v = safe_str(on_off)
    if v == "1":
        return "On Premise"
    if v == "2":
        return "Off Premise"
    return ""


def map_payment_terms(term_code):
    """Map VIP CMTERM to Ohanafy Payment_Terms__c picklist.

    Valid values: Default, 10 Days, 15 Days, 20 Days, 30 Days, 60 Days,
                  90 Days, Custom, Due on Receipt
    """
    m = {
        "1": "Due on Receipt",  # COD → Due on Receipt
        "F": "15 Days",  # Net 15 → 15 Days
        "3": "30 Days",  # Net 30 → 30 Days
        "0": "Due on Receipt",  # Prepaid → Due on Receipt
        "E": "Custom",  # Net 45 → Custom (no 45 option)
        "2": "10 Days",  # Net 10 → 10 Days
        "5": "60 Days",  # Net 60 → 60 Days
        "9": "Custom",  # Net 7 → Custom (no 7 option)
        "8": "Custom",  # EOM → Custom
        "I": "Due on Receipt",  # In Advance → Due on Receipt
        "H": "20 Days",  # Net 21 → 20 Days (closest)
        "N": "",  # No Terms → blank
    }
    return m.get(safe_str(term_code), "")


def map_delivery_method(method_code):
    m = {
        "4": "Delivery",
        "W": "Customer Pickup",
        "2": "Customer Pickup",
        "M": "Delivery",
        "O": "Customer Pickup",
        "A": "Delivery",
        "B": "Delivery",
        "H": "Delivery",
    }
    return m.get(safe_str(method_code).strip(), "Delivery")


def map_market_type(market_desc):
    if not market_desc:
        return ""
    d = safe_str(market_desc).upper().strip()
    mapping = {
        "ADULT ENTERTAIN": "Adult Entertainment",
        "AIRLINES": "Airlines / Transportation",
        "BAR/TAVERN": "Bars/Clubs/Taverns",
        "BOWLING CENTER": "Bowling Center",
        "CASINO/GAMING": "Casinos",
        "CHAIN C-STORE": "Convenience",
        "CHAIN DRUG STOR": "Drug Store",
        "CHN RESTAURANT": "Restaurants",
        "CONCESSIONAIRE": "Concessions / Stadiums",
        "DOLLAR STORE": "Grocery Store",
        "EMPLOYEES": "Employee / Special Account",
        "GOLF/COUNTRY CL": "Recreational",
        "HOTEL/MOTEL": "Hotel / Motel / Resort",
        "IND C-STORES": "Convenience",
        "IND DRUG STORE": "Drug Store",
        "IND RESTAURANT": "Restaurants",
        "IND LIQUOR": "Liquor",
        "MILITARY OFF": "Grocery Store",
        "MILITARY ON": "Recreational",
        "MUSIC/DANCE": "Bars/Clubs/Taverns",
        "SMALL GROCERY": "Grocery Store",
        "NON TRADITIONAL": "Special Events",
        "PRIVATE CLUB": "Private Club",
        "SPEC EVENT/TEMP": "Special Events",
        "SPECIALACCT OFF": "Employee / Special Account",
        "SPECIALACCT ON": "Employee / Special Account",
        "SPORTS BAR": "Sports Bar",
        "SUB-DISTRIBUTOR": "Sub Distributor",
        "SUPERCNTR/MASS": "Supercenter",
        "CHAIN GROCERY": "Grocery Store",
        "SUPPLIERS": "Distributor House Account",
        "CHAIN LIQUOR": "Liquor",
        "WHOLESALE CLUB": "Club Mass Merchandiser",
        "IND GROCERY": "Grocery Store",
        "TOBACCO STORE": "Convenience",
        "IRISH PUB": "Bars/Clubs/Taverns",
        "RECREATION/ENT": "Recreational",
        "SCHOOLS": "Concessions / Stadiums",
        "HEALTH/HOSPITAL": "Concessions / Stadiums",
    }
    return mapping.get(d, "")


def map_retail_type(chain_code, market_desc):
    if market_desc:
        d = safe_str(market_desc).upper().strip()
        if d.startswith("CHAIN") or d.startswith("CHN"):
            return "Chain"
        if d in ("WHOLESALE CLUB", "SUPERCNTR/MASS", "DOLLAR STORE"):
            return "Chain"
        if d.startswith("IND ") or d == "SMALL GROCERY":
            return "Independent"
        if d in ("SUB-DISTRIBUTOR", "SUPPLIERS", "TRANSFERS"):
            return "Distributor"
    return "Independent"


# ---------------------------------------------------------------------------
# Step 1: Resolve lookup SF IDs
# ---------------------------------------------------------------------------
def step1_resolve_lookups():
    """Query SF for all lookup IDs needed by customer records."""
    print("\n=== Step 1: Resolve Lookup SF IDs ===")

    # Territories (by Name)
    print("  Querying Territories...")
    territory_records = run_sf_query("SELECT Id, Name FROM ohfy__Territory__c")
    territory_map = {r["Name"]: r["Id"] for r in territory_records}
    print(f"    {len(territory_map)} territories found")

    # Chain Banners (by Customer_Number__c)
    print("  Querying Chain Banners...")
    chain_records = run_sf_query(
        f"SELECT Id, ohfy__Customer_Number__c FROM Account WHERE RecordTypeId = '{CHAIN_BANNER_RT}'"
    )
    chain_map = {r["ohfy__Customer_Number__c"]: r["Id"] for r in chain_records}
    print(f"    {len(chain_map)} chain banners found: {list(chain_map.keys())}")

    # Pricelists (by Key__c — chain pricelists use CHP-{chain_num})
    print("  Querying Pricelists...")
    pl_records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Pricelist__c WHERE ohfy__Key__c LIKE 'CHP-%'")
    pricelist_map = {}  # chain_code (with leading zeros) → pricelist SF ID
    for r in pl_records:
        key = r["ohfy__Key__c"]  # e.g. CHP-735
        chain_num = key.replace("CHP-", "")
        # Pad back to 4 digits to match chain_code format from BRATTT
        padded = chain_num.zfill(4)
        pricelist_map[padded] = r["Id"]
    print(f"    {len(pricelist_map)} chain pricelists found")

    # Locations (by Key__c)
    print("  Querying Locations...")
    loc_records = run_sf_query("SELECT Id, ohfy__Key__c FROM ohfy__Location__c WHERE ohfy__Key__c != null")
    location_map = {r["ohfy__Key__c"]: r["Id"] for r in loc_records}
    print(f"    {len(location_map)} locations found")

    return territory_map, chain_map, location_map, pricelist_map


# ---------------------------------------------------------------------------
# Step 2: Query customers from PostgreSQL
# ---------------------------------------------------------------------------
def step2_query_customers():
    """Query BRATTT for customers on the 14 routes + 11 chain banners."""
    print("\n=== Step 2: Query Customers from PostgreSQL ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    route_list = ",".join(f"'{r}'" for r in ROUTE_CODES)

    # We filter by route codes. Chain banner filtering happens after we get
    # the chain_map so we know exactly which chains are in the org.
    sql = f"""
        SELECT
            TRIM(b."CMACCT")        AS account_number,
            TRIM(b."CMDBA")         AS dba_name,
            TRIM(b."CMLNAM")        AS legal_name,
            TRIM(b."CMSTR")         AS street,
            TRIM(c."CITYNAME")      AS city,
            TRIM(c."STATE")         AS state_code,
            TRIM(b."POSTALCODE")    AS zip_code,
            TRIM(b."CMCNTY")        AS county,
            b."CMPHON"              AS phone,
            b."CMFAX#"              AS fax,
            TRIM(b."CMBRT")         AS beer_route,
            TRIM(b."CMZONE")        AS zone,
            TRIM(b."CMBSM1")       AS beer_salesman,
            TRIM(b."CMWSM1")       AS wine_salesman,
            TRIM(b."CMBUYR")        AS buyer_contact,
            TRIM(b."CMLIC#")        AS license_number,
            b."CMAR$"               AS ar_balance,
            TRIM(b."CMTERM")        AS payment_term,
            TRIM(b."CMTXCD")        AS tax_code,
            TRIM(b."CMCHN")         AS chain_code,
            TRIM(b."CMCLAS")        AS customer_class,
            TRIM(b."CMSTS")         AS status,
            CAST(b."CMONOF" AS TEXT) AS on_off_premise,
            TRIM(b."CMCOMP")        AS company,
            TRIM(b."CMWHSE")        AS warehouse,
            TRIM(b."CMETHO")        AS delivery_method,
            TRIM(b."CMDCOD")        AS delete_code,
            TRIM(b."CMSCLS")        AS sub_class,
            TRIM(b."CMPGRP")        AS price_group,
            TRIM(b."CMTEXT")        AS notes,
            b."CMMTYP"              AS market_type,
            b."CMBOPN"              AS business_open_date,
            b."CMEXD1"              AS license_exp_date,
            TRIM(b."CMLIC1")        AS license_1,
            TRIM(b."CMTXID")        AS tax_id,
            TRIM(b."CMSPIN")        AS store_pin,
            TRIM(b."CMINST")        AS instructions,
            TRIM(m."DESCRIPTION")   AS market_desc,
            b."CMIDENTITY"          AS vip_identity
        FROM staging."BRATTT" b
        LEFT JOIN staging."CITYT" c ON b."ID_CITY" = c."IDENTITY"
        LEFT JOIN staging."HDRMKTT" m ON b."CMMTYP" = m."MARKETTYPE"
        WHERE b.import_is_deleted = false
          AND TRIM(b."CMBRT") IN ({route_list})
        ORDER BY TRIM(b."CMDBA")
    """

    cur.execute(sql)
    rows = cur.fetchall()
    print(f"  {len(rows)} customers on {len(ROUTE_CODES)} routes")

    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Step 3: Transform and build CSV
# ---------------------------------------------------------------------------
def step3_transform(rows, territory_map, chain_map, location_map, pricelist_map):
    """Transform VIP rows to Account records, filtering to loaded chain banners."""
    print("\n=== Step 3: Transform Customer Data ===")

    # CSV headers — only verified writable fields on Account
    headers = [
        "RecordTypeId",
        "Name",
        "ohfy__Legal_Name__c",
        "ohfy__Customer_Number__c",
        "Type",
        "ohfy__Premise_Type__c",
        "BillingStreet",
        "BillingCity",
        "BillingState",
        "BillingPostalCode",
        "BillingCountry",
        "ShippingStreet",
        "ShippingCity",
        "ShippingState",
        "ShippingPostalCode",
        "ShippingCountry",
        "Phone",
        "Fax",
        "ohfy__Territory__c",
        "ohfy__Chain_Banner__c",
        "ohfy__ABC_License_Number__c",
        "ohfy__ABC_License_Expiration_Date__c",
        "ohfy__Payment_Terms__c",
        "ohfy__Is_Tax_Exempt__c",
        "ohfy__Account_Balance__c",
        "ohfy__Delivery_Method__c",
        "ohfy__Fulfillment_Location__c",
        "ohfy__Pricelist__c",
        "ohfy__Market__c",
        "ohfy__Retail_Type__c",
        "ohfy__Customer_Since__c",
        "ohfy__Invoice_Notes__c",
        "ohfy__Store_Number__c",
        "ohfy__Is_Active__c",
        "ohfy__External_ID__c",
    ]

    friendly_headers = [
        "Record Type ID",
        "DBA Name",
        "Legal Name",
        "Account #",
        "Account Type",
        "Premise Type",
        "Street",
        "City",
        "State",
        "Zip",
        "Country",
        "Ship Street",
        "Ship City",
        "Ship State",
        "Ship Zip",
        "Ship Country",
        "Phone",
        "Fax",
        "Territory",
        "Chain/Banner",
        "ABC License #",
        "ABC License Exp",
        "Payment Terms",
        "Tax Exempt?",
        "AR Balance",
        "Delivery Method",
        "Warehouse",
        "Pricelist",
        "Market Type",
        "Retail Type",
        "Customer Since",
        "Invoice Notes",
        "Store #",
        "Active?",
        "External ID (VIP Identity)",
    ]

    result = []
    seen = set()
    skipped_chain = 0
    unresolved_territory = 0
    unresolved_location = 0

    for r in rows:
        acct = safe_str(r["account_number"])
        if acct in seen or not acct:
            continue
        seen.add(acct)

        dba = safe_str(r["dba_name"])
        legal = safe_str(r["legal_name"])
        if not dba and not legal:
            continue

        # Filter: only include customers whose chain is in the org
        chain_code = safe_str(r.get("chain_code", ""))
        if chain_code not in chain_map:
            skipped_chain += 1
            continue

        status = safe_str(r.get("status", ""))
        premise = map_premise_type(r.get("on_off_premise"))
        street = safe_str(r.get("street", ""))
        city = safe_str(r.get("city", ""))
        state = safe_str(r.get("state_code", ""))
        zip_code = safe_str(r.get("zip_code", ""))
        warehouse = safe_str(r.get("warehouse", ""))
        market_desc = safe_str(r.get("market_desc", ""))

        # Resolve Territory: warehouse → territory name → SF ID
        territory_name = WAREHOUSE_TO_TERRITORY.get(warehouse, "")
        territory_id = territory_map.get(territory_name, "")
        if territory_name and not territory_id:
            unresolved_territory += 1

        # Resolve Chain Banner → SF ID
        chain_banner_id = chain_map.get(chain_code, "")

        # Resolve Fulfillment Location → SF ID
        location_id = location_map.get(warehouse, "")
        if warehouse and not location_id:
            unresolved_location += 1

        # Resolve Pricelist → SF ID (chain's pricelist)
        pricelist_id = pricelist_map.get(chain_code, "")

        # Build invoice notes
        notes_parts = []
        if safe_str(r.get("notes")):
            notes_parts.append(safe_str(r["notes"]))
        if safe_str(r.get("instructions")):
            notes_parts.append(f"Instructions: {safe_str(r['instructions'])}")
        invoice_notes = "; ".join(notes_parts)

        result.append(
            [
                CUSTOMER_RT,  # RecordTypeId
                dba or legal,  # Name
                legal,  # Legal_Name__c
                acct,  # Customer_Number__c
                "Customer",  # Type
                premise,  # Premise_Type__c
                street,  # BillingStreet
                city,  # BillingCity
                state,  # BillingState
                zip_code,  # BillingPostalCode
                "US",  # BillingCountry
                street,  # ShippingStreet
                city,  # ShippingCity
                state,  # ShippingState
                zip_code,  # ShippingPostalCode
                "US",  # ShippingCountry
                format_phone(r.get("phone")),  # Phone
                format_phone(r.get("fax")),  # Fax
                territory_id,  # Territory__c (SF ID)
                chain_banner_id,  # Chain_Banner__c (SF ID)
                safe_str(r.get("license_1", "")),  # ABC_License_Number__c
                vip_date_to_sf(r.get("license_exp_date")),  # ABC_License_Expiration_Date__c
                map_payment_terms(r.get("payment_term")),  # Payment_Terms__c
                "TRUE" if safe_str(r.get("tax_code")).upper() == "Y" else "FALSE",
                safe_str(r.get("ar_balance", "")),  # Account_Balance__c
                map_delivery_method(r.get("delivery_method")),  # Delivery_Method__c
                location_id,  # Fulfillment_Location__c (SF ID)
                pricelist_id,  # Pricelist__c (SF ID)
                map_market_type(market_desc),  # Market__c
                map_retail_type(chain_code, market_desc),  # Retail_Type__c
                vip_date_to_sf(r.get("business_open_date")),  # Customer_Since__c
                invoice_notes,  # Invoice_Notes__c
                safe_str(r.get("store_pin", "")),  # Store_Number__c
                is_active(status),  # Is_Active__c
                safe_str(r.get("vip_identity", acct)),  # External_ID__c
            ]
        )

    print(f"  {len(result)} customers to load (filtered to loaded chain banners)")
    print(f"  {skipped_chain} skipped (chain banner not in org)")
    if unresolved_territory:
        print(f"  WARNING: {unresolved_territory} with unresolved territory")
    if unresolved_location:
        print(f"  WARNING: {unresolved_location} with unresolved location")

    return headers, friendly_headers, result


# ---------------------------------------------------------------------------
# Step 4: Write CSV + Google Sheets
# ---------------------------------------------------------------------------
def step4_output(headers, friendly_headers, data_rows):
    """Write CSV and push to Google Sheets."""
    print("\n=== Step 4: Generate CSV + Google Sheets ===")

    # CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "load_Customers_14routes.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)
    print(f"  CSV: {csv_path} ({len(data_rows)} rows)")

    # Google Sheets
    print("  Pushing to Google Sheets...")
    try:
        creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_PATH), scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(SHEET_ID)

        tab_name = "Customers"
        try:
            ws = spreadsheet.worksheet(tab_name)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(
                title=tab_name,
                rows=max(len(data_rows) + 10, 100),
                cols=len(headers) + 2,
            )

        needed_rows = len(data_rows) + 3
        needed_cols = len(headers) + 1
        if ws.row_count < needed_rows or ws.col_count < needed_cols:
            ws.resize(rows=max(needed_rows, 100), cols=max(needed_cols, 40))

        all_data = [friendly_headers, headers] + data_rows
        # Write in batches
        batch_size = 1000
        for i in range(0, len(all_data), batch_size):
            batch = all_data[i : i + batch_size]
            ws.update(range_name=f"A{i + 1}", values=batch)
            if i + batch_size < len(all_data):
                time.sleep(1)

        print(f"  Google Sheets: {len(data_rows)} rows written to '{tab_name}' tab")
    except Exception as e:
        print(f"  WARNING: Google Sheets failed: {e}")
        print("  CSV was still generated — proceeding with SF load.")

    return csv_path


# ---------------------------------------------------------------------------
# Step 5: Upsert to Salesforce
# ---------------------------------------------------------------------------
def step5_upsert(csv_path):
    """Upsert customer accounts to Salesforce."""
    print("\n=== Step 5: Upsert to Salesforce ===")
    run_sf_upsert("Account", csv_path, "ohfy__External_ID__c")


# ---------------------------------------------------------------------------
# Step 6: Validate
# ---------------------------------------------------------------------------
def step6_validate():
    """Spot-check loaded records."""
    print("\n=== Step 6: Validate ===")

    records = run_sf_query(f"SELECT COUNT(Id) cnt FROM Account WHERE RecordTypeId = '{CUSTOMER_RT}'")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Total Customer accounts in org: {count}")

    # Spot check a few
    samples = run_sf_query(
        f"SELECT Name, ohfy__Customer_Number__c, ohfy__Territory__c, "
        f"ohfy__Chain_Banner__c, ohfy__Fulfillment_Location__c, ohfy__Premise_Type__c "
        f"FROM Account WHERE RecordTypeId = '{CUSTOMER_RT}' "
        f"ORDER BY Name LIMIT 5"
    )
    print("  Sample records:")
    for s in samples:
        print(
            f"    {s['Name']:<30} #{s['ohfy__Customer_Number__c']:<8} "
            f"Territory={s.get('ohfy__Territory__c', '')[:8]}... "
            f"Chain={s.get('ohfy__Chain_Banner__c', '')[:8]}... "
            f"Premise={s.get('ohfy__Premise_Type__c', '')}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Customer Accounts — 14 Routes × Loaded Chain Banners")
    print("=" * 60)

    territory_map, chain_map, location_map, pricelist_map = step1_resolve_lookups()
    rows = step2_query_customers()
    headers, friendly_headers, data_rows = step3_transform(rows, territory_map, chain_map, location_map, pricelist_map)

    if not data_rows:
        print("\nNo customers to load! Check filters.")
        sys.exit(1)

    csv_path = step4_output(headers, friendly_headers, data_rows)
    step5_upsert(csv_path)
    step6_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
