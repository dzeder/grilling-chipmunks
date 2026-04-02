#!/usr/bin/env python3
"""Load Contacts for existing Customer accounts in the Gulf sandbox.

Reads migration_output/Contacts.csv, filters to accounts already loaded in
the sandbox, removes contacts with bad name data, resolves AccountId to SF
record IDs, and bulk-inserts into Salesforce.
"""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TARGET_ORG = "gulf-partial-copy-sandbox"
OUTPUT_DIR = Path("migration_output")
INPUT_CSV = OUTPUT_DIR / "Contacts.csv"
OUTPUT_CSV = OUTPUT_DIR / "load_contacts.csv"

SHEET_ID = "108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE"
SERVICE_ACCOUNT_PATH = Path("/Users/danielzeder/Desktop/VIP to Ohanafy/service-account.json")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ---------------------------------------------------------------------------
# Salesforce helpers (reused from load_route_customers.py)
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
    """Bulk insert CSV into Salesforce."""
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
            "10",
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
# Name quality filter
# ---------------------------------------------------------------------------
def is_good_name(first_name, last_name):
    """Return True if the contact has a usable person name."""
    ln = last_name.strip()
    fn = first_name.strip()

    # Reject empty or purely numeric last names
    if not ln or ln.isdigit():
        return False

    # Reject if combined name has fewer than 3 alpha chars
    combined = fn + " " + ln
    alpha_count = sum(1 for c in combined if c.isalpha())
    if alpha_count < 3:
        return False

    return True


# ---------------------------------------------------------------------------
# Step 1: Build AccountId lookup from sandbox
# ---------------------------------------------------------------------------
def step1_build_account_map():
    """Query all loaded accounts and build Customer_Number__c → SF Id map."""
    print("\n=== Step 1: Build Account Lookup Map ===")

    records = run_sf_query("SELECT Id, ohfy__Customer_Number__c FROM Account WHERE ohfy__Customer_Number__c != null")
    acct_map = {}
    for r in records:
        cust_num = r.get("ohfy__Customer_Number__c", "")
        if cust_num:
            acct_map[cust_num] = r["Id"]

    print(f"  {len(acct_map)} accounts with Customer_Number__c found in sandbox")
    return acct_map


# ---------------------------------------------------------------------------
# Step 2: Read and filter contacts
# ---------------------------------------------------------------------------
def step2_filter_contacts(acct_map):
    """Read Contacts.csv, filter to loaded accounts + good names."""
    print("\n=== Step 2: Filter Contacts ===")

    headers = [
        "FirstName",
        "LastName",
        "AccountId",
        "Phone",
        "Fax",
        "Title",
        "ohfy__Level__c",
        "ohfy__Is_Billing_Contact__c",
        "ohfy__Is_Delivery_Contact__c",
    ]

    contacts = []
    total = 0
    matched = 0
    good_names = 0
    bad_names = 0

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            vip_acct = row["AccountId"].strip()

            # Filter: only contacts for loaded accounts
            if vip_acct not in acct_map:
                continue
            matched += 1

            fn = row["FirstName"].strip()
            ln = row["LastName"].strip()

            # Filter: skip bad name data
            if not is_good_name(fn, ln):
                bad_names += 1
                continue
            good_names += 1

            contacts.append(
                [
                    fn,  # FirstName
                    ln,  # LastName
                    acct_map[vip_acct],  # AccountId (SF ID)
                    row.get("Phone", "").strip(),  # Phone
                    row.get("Fax", "").strip(),  # Fax
                    row.get("Title", "Buyer").strip(),  # Title
                    row.get("ohfy__Level__c", "Primary").strip(),
                    row.get("ohfy__Is_Billing_Contact__c", "TRUE").strip(),
                    row.get("ohfy__Is_Delivery_Contact__c", "TRUE").strip(),
                ]
            )

    print(f"  Total contacts in CSV: {total}")
    print(f"  Matched to loaded accounts: {matched}")
    print(f"  Good names (to load): {good_names}")
    print(f"  Bad names (skipped): {bad_names}")

    return headers, contacts


# ---------------------------------------------------------------------------
# Step 3: Write CSV + Google Sheets
# ---------------------------------------------------------------------------
def step3_output(headers, contacts):
    """Write load CSV and push to Google Sheets."""
    print("\n=== Step 3: Generate CSV + Google Sheets ===")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(contacts)
    print(f"  CSV: {OUTPUT_CSV} ({len(contacts)} rows)")

    # Google Sheets
    print("  Pushing to Google Sheets...")
    try:
        creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_PATH), scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(SHEET_ID)

        tab_name = "Contacts"
        try:
            ws = spreadsheet.worksheet(tab_name)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(
                title=tab_name,
                rows=max(len(contacts) + 10, 100),
                cols=len(headers) + 2,
            )

        needed_rows = len(contacts) + 3
        needed_cols = len(headers) + 1
        if ws.row_count < needed_rows or ws.col_count < needed_cols:
            ws.resize(rows=max(needed_rows, 100), cols=max(needed_cols, 20))

        all_data = [headers] + contacts
        batch_size = 1000
        for i in range(0, len(all_data), batch_size):
            batch = all_data[i : i + batch_size]
            ws.update(range_name=f"A{i + 1}", values=batch)
            if i + batch_size < len(all_data):
                time.sleep(1)

        print(f"  Google Sheets: {len(contacts)} rows written to '{tab_name}' tab")
    except Exception as e:
        print(f"  WARNING: Google Sheets failed: {e}")
        print("  CSV was still generated — proceeding with SF load.")

    return OUTPUT_CSV


# ---------------------------------------------------------------------------
# Step 4: Bulk insert to Salesforce
# ---------------------------------------------------------------------------
def step4_load(csv_path):
    """Bulk insert contacts into Salesforce."""
    print("\n=== Step 4: Load Contacts into Salesforce ===")
    run_sf_import("Contact", csv_path)


# ---------------------------------------------------------------------------
# Step 5: Validate
# ---------------------------------------------------------------------------
def step5_validate():
    """Verify contacts loaded correctly."""
    print("\n=== Step 5: Validate ===")

    records = run_sf_query("SELECT COUNT(Id) cnt FROM Contact")
    count = records[0].get("cnt", records[0].get("expr0", "?"))
    print(f"  Total Contacts in org: {count}")

    samples = run_sf_query(
        "SELECT FirstName, LastName, Account.Name, Phone, Title FROM Contact ORDER BY LastName LIMIT 5"
    )
    print("  Sample records:")
    for s in samples:
        acct_name = s.get("Account", {}).get("Name", "?") if s.get("Account") else "?"
        print(
            f"    {(s.get('FirstName') or ''):<15} {s['LastName']:<20} Acct={acct_name:<25} Phone={s.get('Phone', '')}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Load Contacts for Existing Sandbox Accounts")
    print("=" * 60)

    acct_map = step1_build_account_map()
    headers, contacts = step2_filter_contacts(acct_map)

    if not contacts:
        print("\nNo contacts to load! Check that accounts are loaded.")
        sys.exit(1)

    csv_path = step3_output(headers, contacts)
    step4_load(csv_path)
    step5_validate()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
