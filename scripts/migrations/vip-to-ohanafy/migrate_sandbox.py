#!/usr/bin/env python3
"""Sandbox-to-sandbox data migration for Ohanafy orgs.

Extracts foundational/master data from a source Salesforce sandbox,
transforms lookup IDs and RecordTypeIds for a target org, and loads
via Bulk API in dependency order.

Usage:
    python3 migrate_sandbox.py                          # full migration
    python3 migrate_sandbox.py --dry-run                # generate CSVs only
    python3 migrate_sandbox.py --start-wave 6           # resume from wave 6
    python3 migrate_sandbox.py --waves 1,2              # run specific waves
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_SOURCE = "gulf-partial-copy-sandbox"
DEFAULT_TARGET = "gulf-cam-sandbox"
OUTPUT_DIR = Path("migration_output/sandbox_transfer")
CAM_USER_ID = "005WE00000dU2BHYA0"  # Cam Koorangi — default owner in target

# Fields to always exclude from extraction (system-managed, not creatable in practice)
SKIP_FIELDS = {
    "Id",
    "IsDeleted",
    "CreatedDate",
    "CreatedById",
    "LastModifiedDate",
    "LastModifiedById",
    "SystemModstamp",
    "LastActivityDate",
    "LastViewedDate",
    "LastReferencedDate",
    "MasterRecordId",
    "Jigsaw",
    "JigsawCompanyId",
    "PhotoUrl",
    "CleanStatus",
    "DandbCompanyId",
}

# Fields that are User lookups — set to Cam or clear
USER_LOOKUP_FIELDS = {
    "OwnerId",
    "ohfy__Driver__c",
    "ohfy__Sales_Rep__c",
    "ohfy__Created_By_User__c",
    "ohfy__Last_Modified_By_User__c",
}

# Valid Packaging_Type__c values for Finished_Good RT in CAM sandbox
VALID_PACKAGING_TYPES_CAM = {
    "1/2 Barrel(s)",
    "1/4 Barrel(s)",
    "1/6 Barrel(s)",
    "Barrel(s)",
    "Each",
    "Gallon(s)",
    "Hectoliter(s)",
    "Liter(s)",
    "Proof Gallon(s)",
    "Case - 4x6 - 12oz - Can",
    "Case - 6x4 - 16oz - Can",
    "Case - 4x4 - 16oz - Can",
    "Case - 20x - 22oz - Bottle",
    "Case - 12x - 500mL - Bottle",
    "6pk - .75L - Bottle",
    "4pk - 2.25L - Bottle",
    "6x4 - 250mL - Bottle",
    "4pk - 600mL - Bottle",
    "12pk - 200mL - Bottle",
    "20 Liter(s)",
    "40 Liter(s)",
    "50 Liter(s)",
}


# ── Salesforce Helpers ────────────────────────────────────────────────────────


def run_sf_query(soql, org):
    """Run SOQL query and return records list."""
    result = subprocess.run(
        ["sf", "data", "query", "--query", soql, "--target-org", org, "--json"],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  SOQL parse error. stderr: {result.stderr[:500]}", file=sys.stderr)
        return []
    if data.get("status") != 0:
        msg = data.get("message", data.get("result", {}).get("message", "unknown"))
        print(f"  SOQL error: {msg}", file=sys.stderr)
        return []
    return data["result"]["records"]


def run_sf_upsert(sobject, csv_path, external_id, org):
    """Bulk upsert CSV into Salesforce. Returns (processed, failed)."""
    print(f"  Upserting {csv_path.name} into {sobject} on {external_id}...")
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
            org,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    return _handle_bulk_result(result, org)


def run_sf_import(sobject, csv_path, org):
    """Bulk import (insert) CSV into Salesforce. Returns (processed, failed)."""
    print(f"  Importing {csv_path.name} into {sobject}...")
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
            org,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    return _handle_bulk_result(result, org)


def _handle_bulk_result(result, org):
    """Parse bulk API result, show errors, return (processed, failed)."""
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  Bulk API parse error. stderr: {result.stderr[:500]}", file=sys.stderr)
        return (0, 0)

    job_id = (
        data.get("result", {}).get("jobId")
        or data.get("result", {}).get("jobInfo", {}).get("id")
        or data.get("data", {}).get("jobId", "")
    )

    if "FailedRecordDetailsError" in data.get("name", ""):
        print(f"  {data.get('message', '')}")
        if job_id:
            _show_bulk_errors(job_id, org)
        return (0, -1)

    if "JobFailedError" in data.get("name", ""):
        print(f"  Job failed: {data.get('message', '')}", file=sys.stderr)
        return (0, -1)

    job_info = data.get("result", {}).get("jobInfo", {})
    processed = int(job_info.get("numberRecordsProcessed", 0))
    failed = int(job_info.get("numberRecordsFailed", 0))
    print(f"  Processed: {processed}, Failed: {failed}")

    if failed > 0 and job_id:
        _show_bulk_errors(job_id, org)

    return (processed, failed)


def _show_bulk_errors(job_id, org, max_errors=10):
    """Fetch and display errors from a bulk job."""
    subprocess.run(
        ["sf", "data", "bulk", "results", "--job-id", job_id, "--target-org", org],
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


# ── IdResolver ────────────────────────────────────────────────────────────────


class IdResolver:
    """Maps source SF IDs → key values → target SF IDs across waves."""

    def __init__(self):
        self.source_id_to_key = {}  # {name: {source_sf_id: key_value}}
        self.key_to_target_id = {}  # {name: {key_value: target_sf_id}}

    def register_source(self, name, source_id, key_value):
        self.source_id_to_key.setdefault(name, {})[source_id] = key_value

    def register_target(self, name, key_value, target_id):
        self.key_to_target_id.setdefault(name, {})[key_value] = target_id

    def resolve(self, name, source_id):
        """Resolve source SF ID → target SF ID via key bridge."""
        if not source_id:
            return ""
        key = self.source_id_to_key.get(name, {}).get(source_id)
        if key is None:
            return ""
        return self.key_to_target_id.get(name, {}).get(key, "")

    def source_count(self, name):
        return len(self.source_id_to_key.get(name, {}))

    def target_count(self, name):
        return len(self.key_to_target_id.get(name, {}))


# ── Field Discovery ──────────────────────────────────────────────────────────

_field_cache = {}


def get_creatable_fields(sobject, org):
    """Query EntityParticle to get creatable field names for an object."""
    cache_key = f"{sobject}:{org}"
    if cache_key in _field_cache:
        return _field_cache[cache_key]

    records = run_sf_query(
        f"SELECT QualifiedApiName FROM EntityParticle WHERE EntityDefinitionId = '{sobject}' AND IsCreatable = true",
        org,
    )
    fields = sorted(r["QualifiedApiName"] for r in records if r["QualifiedApiName"] not in SKIP_FIELDS)
    _field_cache[cache_key] = fields
    return fields


def get_common_fields(sobject, source_org, target_org):
    """Get fields creatable in BOTH source and target orgs."""
    source_fields = set(get_creatable_fields(sobject, source_org))
    target_fields = set(get_creatable_fields(sobject, target_org))
    common = sorted(source_fields & target_fields)
    if not common:
        print(f"  WARNING: No common creatable fields for {sobject}!")
    return common


# ── Extract / Transform / Load ───────────────────────────────────────────────


def extract_records(sobject, fields, org, where=None):
    """Extract all records from an org via SOQL. Always includes Id."""
    select_fields = ["Id"] + [f for f in fields if f != "Id"]
    soql = f"SELECT {', '.join(select_fields)} FROM {sobject}"
    if where:
        soql += f" WHERE {where}"
    records = run_sf_query(soql, org)
    # Clean: strip attributes, convert None/bool
    cleaned = []
    for rec in records:
        row = {}
        for f in select_fields:
            val = rec.get(f)
            if val is None:
                row[f] = ""
            elif isinstance(val, bool):
                row[f] = "true" if val else "false"
            else:
                row[f] = str(val)
        cleaned.append(row)
    return cleaned


def write_csv(records, fields, path):
    """Write records to CSV with CRLF line endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    print(f"  Wrote {len(records)} records to {path.name}")
    return path


def register_source_ids(name, records, key_field, resolver):
    """Register source Id → key mappings from extracted records."""
    for rec in records:
        source_id = rec.get("Id", "")
        key_val = rec.get(key_field, "")
        if source_id and key_val:
            resolver.register_source(name, source_id, key_val)


def register_target_ids(name, sobject, key_field, org, resolver):
    """Query target org and register key → target Id mappings."""
    records = run_sf_query(f"SELECT Id, {key_field} FROM {sobject} WHERE {key_field} != null", org)
    for rec in records:
        key_val = rec.get(key_field, "")
        target_id = rec.get("Id", "")
        if key_val and target_id:
            resolver.register_target(name, key_val, target_id)
    print(f"  Registered {len(records)} target IDs for {name}")


def transform_lookups(records, lookup_config, resolver, rt_map, owner_id):
    """Transform lookup SF IDs, RecordTypeId, and OwnerId in records."""
    for rec in records:
        # Swap RecordTypeId — clear if unmapped (would fail in target)
        if "RecordTypeId" in rec and rec["RecordTypeId"]:
            old_rt = rec["RecordTypeId"]
            new_rt = rt_map.get(old_rt)
            if new_rt:
                rec["RecordTypeId"] = new_rt
            else:
                rec["RecordTypeId"] = ""  # Let target use default

        # Resolve configured lookups
        for field, resolver_name in lookup_config.items():
            if field in rec and rec[field]:
                resolved = resolver.resolve(resolver_name, rec[field])
                rec[field] = resolved

        # Handle User lookup fields
        for uf in USER_LOOKUP_FIELDS:
            if uf in rec:
                if rec[uf]:  # Only set Cam if field was populated
                    rec[uf] = owner_id
                # If empty, leave empty

    return records


def load_object(sobject, csv_path, org, upsert_field=None):
    """Load CSV via upsert or import. Returns (processed, failed)."""
    if upsert_field:
        return run_sf_upsert(sobject, csv_path, upsert_field, org)
    else:
        return run_sf_import(sobject, csv_path, org)


# ── Generic wave step ────────────────────────────────────────────────────────


def migrate_object(
    name,
    sobject,
    key_field,
    source_org,
    target_org,
    resolver,
    rt_map,
    owner_id,
    dry_run,
    upsert_field=None,
    lookup_config=None,
    where=None,
    extra_transform=None,
    field_overrides=None,
):
    """Generic extract-transform-load for one object.

    Args:
        name: resolver name for this object
        sobject: Salesforce API name
        key_field: field used as bridge key (Key__c, External_ID__c, Name)
        lookup_config: {field_name: resolver_name} for lookups to resolve
        upsert_field: external ID field for upsert, or None for insert
        extra_transform: optional function(records) for custom transforms
        field_overrides: optional list of fields to use instead of auto-discovery
    """
    print(f"\n── {name} ({sobject}) ──")

    # Discover fields
    if field_overrides:
        fields = field_overrides
    else:
        fields = get_common_fields(sobject, source_org, target_org)

    if not fields:
        print("  SKIPPING: object not found in one or both orgs")
        return 0

    # Extract from source
    records = extract_records(sobject, fields, source_org, where=where)
    print(f"  Extracted {len(records)} records from source")

    if not records:
        return 0

    # Register source ID → key mappings
    register_source_ids(name, records, key_field, resolver)

    # Idempotency: check if target already has records for this object
    if not dry_run:
        existing = run_sf_query(
            f"SELECT COUNT(Id) cnt FROM {sobject}" + (f" WHERE {where}" if where else ""),
            target_org,
        )
        existing_count = existing[0].get("cnt", 0) if existing else 0
        if existing_count >= len(records):
            print(f"  SKIP: target already has {existing_count} records (source has {len(records)})")
            register_target_ids(name, sobject, key_field, target_org, resolver)
            return existing_count

    # Transform
    output_fields = [f for f in fields if f != "Id"]
    transform_lookups(records, lookup_config or {}, resolver, rt_map, owner_id)

    if extra_transform:
        records = extra_transform(records)

    # Write CSV
    csv_path = write_csv(records, output_fields, OUTPUT_DIR / f"{name}.csv")

    # Load into target
    if not dry_run:
        processed, failed = load_object(sobject, csv_path, target_org, upsert_field)
        if failed == -1:
            print(f"  ERROR: {name} load failed completely")
            return 0
        # Register target IDs
        time.sleep(2)  # Brief wait for indexing
        register_target_ids(name, sobject, key_field, target_org, resolver)
        return processed - failed
    else:
        print(f"  DRY RUN: would load {len(records)} records")
        return len(records)


# ── Wave Functions ───────────────────────────────────────────────────────────


def wave_1(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 1: Independent objects — Territory, Fee, Pricelist, Transformation_Setting."""
    print("\n" + "=" * 60)
    print("WAVE 1: Independent Objects")
    print("=" * 60)

    migrate_object(
        "Territory",
        "ohfy__Territory__c",
        "Name",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
    )

    migrate_object(
        "Fee",
        "ohfy__Fee__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
    )

    migrate_object(
        "Pricelist",
        "ohfy__Pricelist__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
    )

    migrate_object(
        "Transformation_Setting",
        "ohfy__Transformation_Setting__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
    )


def wave_2(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 2: Non-customer Accounts (Suppliers, Chain Banners, etc.)."""
    print("\n" + "=" * 60)
    print("WAVE 2: Non-Customer Accounts")
    print("=" * 60)

    # We need to know source RT IDs to filter by record type
    # Query source for Account RecordType breakdown
    rt_counts = run_sf_query(
        "SELECT RecordType.DeveloperName, COUNT(Id) cnt FROM Account GROUP BY RecordType.DeveloperName",
        source,
    )
    print("  Source Account breakdown:")
    for r in rt_counts:
        dev_name = r.get("RecordType", {}).get("DeveloperName", "?") if r.get("RecordType") else "?"
        print(f"    {dev_name}: {r.get('cnt', r.get('expr0', '?'))}")

    # Get all accounts from source in one query
    fields = get_common_fields("Account", source, target)
    if not fields:
        print("  SKIPPING: Account not found")
        return

    all_accounts = extract_records("Account", fields, source)
    print(f"  Extracted {len(all_accounts)} total Accounts from source")

    # Register ALL source Account IDs → External_ID__c
    for rec in all_accounts:
        source_id = rec.get("Id", "")
        ext_id = rec.get("ohfy__External_ID__c", "")
        if source_id and ext_id:
            resolver.register_source("Account", source_id, ext_id)
        # Also register by Customer_Number for Chain Banner lookups
        cust_num = rec.get("ohfy__Customer_Number__c", "")
        if source_id and cust_num:
            resolver.register_source("Account_by_CustNum", source_id, cust_num)

    # Split by RecordType — load non-customers first
    # Build RT ID → DeveloperName from our rt_map data
    source_rts = run_sf_query(
        "SELECT Id, DeveloperName FROM RecordType WHERE SobjectType = 'Account' AND IsActive = true",
        source,
    )
    rt_id_to_name = {r["Id"]: r["DeveloperName"] for r in source_rts}

    customer_rt_names = {"Customer", "Retailer"}  # Load these in Wave 6
    non_customer_groups = {}

    for rec in all_accounts:
        rt_id = rec.get("RecordTypeId", "")
        dev_name = rt_id_to_name.get(rt_id, "Unknown")
        if dev_name in customer_rt_names:
            continue  # Skip customers for Wave 6
        non_customer_groups.setdefault(dev_name, []).append(rec)

    output_fields = [f for f in fields if f != "Id"]

    # Lookup config for non-customer accounts
    # Suppliers and Chain Banners generally don't have Territory/Location lookups populated
    # but we handle them just in case
    lookup_config = {
        "ohfy__Territory__c": "Territory",
    }

    for dev_name, records in sorted(non_customer_groups.items()):
        print(f"\n  ── Account/{dev_name} ({len(records)} records) ──")

        transform_lookups(records, lookup_config, resolver, rt_map, owner_id)

        csv_path = write_csv(
            records,
            output_fields,
            OUTPUT_DIR / f"Account_{dev_name}.csv",
        )

        if not dry_run:
            load_object("Account", csv_path, target, "ohfy__External_ID__c")
            time.sleep(2)

    # Register ALL target Account IDs (including any that existed before)
    if not dry_run:
        register_target_ids(
            "Account",
            "Account",
            "ohfy__External_ID__c",
            target,
            resolver,
        )


def wave_3(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 3: Locations (parent warehouses first, then child zones)."""
    print("\n" + "=" * 60)
    print("WAVE 3: Locations")
    print("=" * 60)

    fields = get_common_fields("ohfy__Location__c", source, target)
    if not fields:
        print("  SKIPPING: Location not found")
        return

    # 3a: Parent Locations (no parent)
    print("\n  ── Parent Locations ──")
    parents = extract_records(
        "ohfy__Location__c",
        fields,
        source,
        where="ohfy__Parent_Location__c = null",
    )
    print(f"  Extracted {len(parents)} parent locations")
    register_source_ids("Location", parents, "ohfy__Key__c", resolver)

    output_fields = [f for f in fields if f != "Id"]
    transform_lookups(parents, {}, resolver, rt_map, owner_id)
    csv_path = write_csv(parents, output_fields, OUTPUT_DIR / "Location_Parents.csv")

    if not dry_run:
        load_object("ohfy__Location__c", csv_path, target)
        time.sleep(2)
        register_target_ids(
            "Location",
            "ohfy__Location__c",
            "ohfy__Key__c",
            target,
            resolver,
        )

    # 3b: Child Locations (have parent)
    print("\n  ── Child Locations ──")
    children = extract_records(
        "ohfy__Location__c",
        fields,
        source,
        where="ohfy__Parent_Location__c != null",
    )
    print(f"  Extracted {len(children)} child locations")
    register_source_ids("Location", children, "ohfy__Key__c", resolver)

    lookup_config = {"ohfy__Parent_Location__c": "Location"}
    transform_lookups(children, lookup_config, resolver, rt_map, owner_id)
    csv_path = write_csv(children, output_fields, OUTPUT_DIR / "Location_Children.csv")

    if not dry_run:
        load_object("ohfy__Location__c", csv_path, target)
        time.sleep(2)
        # Re-register to include children
        register_target_ids(
            "Location",
            "ohfy__Location__c",
            "ohfy__Key__c",
            target,
            resolver,
        )


def wave_4(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 4: Equipment + Item Lines."""
    print("\n" + "=" * 60)
    print("WAVE 4: Equipment + Item Lines")
    print("=" * 60)

    migrate_object(
        "Equipment",
        "ohfy__Equipment__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Fulfillment_Location__c": "Location",
        },
    )

    migrate_object(
        "Item_Line",
        "ohfy__Item_Line__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Supplier__c": "Account",
        },
    )


def wave_5(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 5: Routes + Item Types."""
    print("\n" + "=" * 60)
    print("WAVE 5: Routes + Item Types")
    print("=" * 60)

    migrate_object(
        "Route",
        "ohfy__Route__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Vehicle__c": "Equipment",
            "ohfy__Fulfillment_Location__c": "Location",
        },
    )

    migrate_object(
        "Item_Type",
        "ohfy__Item_Type__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Item_Line__c": "Item_Line",
            "ohfy__Supplier__c": "Account",
        },
    )


def wave_6(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 6: Customer Accounts + Items."""
    print("\n" + "=" * 60)
    print("WAVE 6: Customers + Items")
    print("=" * 60)

    # 6a: Customer Accounts
    print("\n  ── Customer Accounts ──")
    fields = get_common_fields("Account", source, target)

    # Get source RT IDs for customer types
    source_rts = run_sf_query(
        "SELECT Id, DeveloperName FROM RecordType "
        "WHERE SobjectType = 'Account' AND DeveloperName IN ('Customer', 'Retailer') "
        "AND IsActive = true",
        source,
    )
    customer_rt_ids = [r["Id"] for r in source_rts]

    if customer_rt_ids:
        rt_filter = ", ".join(f"'{rid}'" for rid in customer_rt_ids)
        customers = extract_records(
            "Account",
            fields,
            source,
            where=f"RecordTypeId IN ({rt_filter})",
        )
        print(f"  Extracted {len(customers)} customer accounts")

        # Register source IDs (some may already be registered from Wave 2)
        for rec in customers:
            source_id = rec.get("Id", "")
            ext_id = rec.get("ohfy__External_ID__c", "")
            if source_id and ext_id:
                resolver.register_source("Account", source_id, ext_id)

        output_fields = [f for f in fields if f != "Id"]
        lookup_config = {
            "ohfy__Territory__c": "Territory",
            "ohfy__Chain_Banner__c": "Account",
            "ohfy__Fulfillment_Location__c": "Location",
            "ohfy__Pricelist__c": "Pricelist",
            "ParentId": "Account",
        }
        transform_lookups(customers, lookup_config, resolver, rt_map, owner_id)
        csv_path = write_csv(customers, output_fields, OUTPUT_DIR / "Account_Customer.csv")

        if not dry_run:
            load_object("Account", csv_path, target, "ohfy__External_ID__c")
            time.sleep(2)
            # Re-register all target Account IDs
            register_target_ids(
                "Account",
                "Account",
                "ohfy__External_ID__c",
                target,
                resolver,
            )
    else:
        print("  No customer record types found in source")

    # 6b: Items
    migrate_object(
        "Item",
        "ohfy__Item__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        upsert_field="ohfy__External_ID__c",
        lookup_config={
            "ohfy__Item_Type__c": "Item_Type",
            "ohfy__Item_Line__c": "Item_Line",
        },
    )


def wave_7(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 7: Child objects — Contact, Item_Component, Lot, Inventory, Pricelist_Item, Promotion."""
    print("\n" + "=" * 60)
    print("WAVE 7: Child Objects")
    print("=" * 60)

    # 7a: Contacts — two-pass to work around managed trigger bug
    # The ContactTrigger crashes with "Duplicate id in list" when both
    # Is_Billing_Contact and Is_Delivery_Contact are true in the same insert.
    # Pass 1: insert without Is_Delivery_Contact
    # Pass 2: update Is_Delivery_Contact via CSV
    print("\n── Contact (Contact) ──")
    contact_fields = get_common_fields("Contact", source, target)
    if contact_fields:
        records = extract_records("Contact", contact_fields, source)
        print(f"  Extracted {len(records)} records from source")
        if records and not dry_run:
            existing = run_sf_query("SELECT COUNT(Id) cnt FROM Contact", target)
            existing_count = existing[0].get("cnt", 0) if existing else 0
            if existing_count >= len(records):
                print(f"  SKIP: target already has {existing_count} contacts")
            else:
                register_source_ids("Contact", records, "Email", resolver)
                # Save delivery flag, strip it for pass 1
                delivery_flags = {r.get("Email"): r.get("ohfy__Is_Delivery_Contact__c", "") for r in records}
                output_fields = [f for f in contact_fields if f not in ("Id", "ohfy__Is_Delivery_Contact__c")]
                transform_lookups(records, {"AccountId": "Account"}, resolver, rt_map, owner_id)
                # Write pass-1 CSV without delivery flag
                csv_path = write_csv(records, output_fields, OUTPUT_DIR / "Contact.csv")
                processed, failed = load_object("Contact", csv_path, target)
                time.sleep(2)

                # Pass 2: update delivery flag on inserted contacts
                target_contacts = run_sf_query("SELECT Id, Email FROM Contact", target)
                update_rows = []
                for tc in target_contacts:
                    email = tc.get("Email", "")
                    dflag = delivery_flags.get(email, "")
                    if dflag:
                        update_rows.append({"Id": tc["Id"], "ohfy__Is_Delivery_Contact__c": dflag})
                if update_rows:
                    up_path = OUTPUT_DIR / "Contact_update_delivery.csv"
                    up_fields = ["Id", "ohfy__Is_Delivery_Contact__c"]
                    write_csv(update_rows, up_fields, up_path)
                    print(f"  Pass 2: updating delivery flag on {len(update_rows)} contacts")
                    run_sf_upsert("Contact", up_path, "Id", target)
                print(f"  Loaded {len(records)} contacts (two-pass)")

    # 7b: Item Components
    migrate_object(
        "Item_Component",
        "ohfy__Item_Component__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Parent_Item__c": "Item",
            "ohfy__Child_Item__c": "Item",
        },
    )

    # 7c: Lots (uses Lot_Identifier__c, not Key__c)
    migrate_object(
        "Lot",
        "ohfy__Lot__c",
        "ohfy__Lot_Identifier__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Item__c": "Item",
            "ohfy__Location__c": "Location",
            "ohfy__Supplier__c": "Account",
        },
    )

    # 7d: Inventory
    print("\n── Inventory (ohfy__Inventory__c) ──")
    inv_fields = get_common_fields("ohfy__Inventory__c", source, target)
    if inv_fields:
        inv_records = extract_records("ohfy__Inventory__c", inv_fields, source)
        print(f"  Extracted {len(inv_records)} inventory records")

        # Register source IDs using composite key (Item Key + Location Key)
        # First, build source Item ID → Key and Location ID → Key maps from resolver
        for rec in inv_records:
            source_id = rec.get("Id", "")
            # Build composite key: item_key|location_key
            item_source_id = rec.get("ohfy__Item__c", "")
            loc_source_id = rec.get("ohfy__Location__c", "")
            item_key = resolver.source_id_to_key.get("Item", {}).get(item_source_id, "")
            loc_key = resolver.source_id_to_key.get("Location", {}).get(loc_source_id, "")
            composite_key = f"{item_key}|{loc_key}"
            if source_id and item_key and loc_key:
                resolver.register_source("Inventory", source_id, composite_key)

        output_fields = [f for f in inv_fields if f != "Id"]
        transform_lookups(
            inv_records,
            {"ohfy__Item__c": "Item", "ohfy__Location__c": "Location"},
            resolver,
            rt_map,
            owner_id,
        )
        csv_path = write_csv(inv_records, output_fields, OUTPUT_DIR / "Inventory.csv")

        if not dry_run:
            load_object("ohfy__Inventory__c", csv_path, target)
            time.sleep(3)

            # Register target Inventory IDs using composite key
            target_inv = run_sf_query(
                "SELECT Id, ohfy__Item__r.ohfy__Key__c, ohfy__Location__r.ohfy__Key__c FROM ohfy__Inventory__c",
                target,
            )
            for rec in target_inv:
                item_key = (rec.get("ohfy__Item__r") or {}).get("ohfy__Key__c", "")
                loc_key = (rec.get("ohfy__Location__r") or {}).get("ohfy__Key__c", "")
                composite_key = f"{item_key}|{loc_key}"
                if composite_key != "|":
                    resolver.register_target("Inventory", composite_key, rec["Id"])
            print(f"  Registered {len(target_inv)} target Inventory IDs")

    # 7e: Pricelist Items
    print("\n── Pricelist_Item (ohfy__Pricelist_Item__c) ──")
    pli_fields = get_common_fields("ohfy__Pricelist_Item__c", source, target)
    if pli_fields:
        pli_records = extract_records("ohfy__Pricelist_Item__c", pli_fields, source)
        print(f"  Extracted {len(pli_records)} pricelist item records")

        # Register source IDs
        register_source_ids("Pricelist_Item", pli_records, "ohfy__Key__c", resolver)

        output_fields = [f for f in pli_fields if f != "Id"]
        transform_lookups(
            pli_records,
            {"ohfy__Pricelist__c": "Pricelist", "ohfy__Item__c": "Item"},
            resolver,
            rt_map,
            owner_id,
        )
        csv_path = write_csv(pli_records, output_fields, OUTPUT_DIR / "Pricelist_Item.csv")

        if not dry_run:
            # Pricelist Items can have lock contention — retry pattern
            processed, failed = load_object("ohfy__Pricelist_Item__c", csv_path, target)
            time.sleep(2)
            register_target_ids(
                "Pricelist_Item",
                "ohfy__Pricelist_Item__c",
                "ohfy__Key__c",
                target,
                resolver,
            )

    # 7f: Promotions
    migrate_object(
        "Promotion",
        "ohfy__Promotion__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Customer__c": "Account",
            "ohfy__Territory__c": "Territory",
        },
    )


def wave_8(source, target, resolver, rt_map, owner_id, dry_run):
    """Wave 8: Junction/grandchild objects — Account_Route, Lot_Inventory."""
    print("\n" + "=" * 60)
    print("WAVE 8: Junction Objects")
    print("=" * 60)

    # 8a: Account Routes
    migrate_object(
        "Account_Route",
        "ohfy__Account_Route__c",
        "ohfy__Key__c",
        source,
        target,
        resolver,
        rt_map,
        owner_id,
        dry_run,
        lookup_config={
            "ohfy__Route__c": "Route",
            "ohfy__Customer__c": "Account",
            "ohfy__Fulfillment_Location__c": "Location",
        },
    )

    # 8b: Lot Inventory
    print("\n── Lot_Inventory (ohfy__Lot_Inventory__c) ──")
    li_fields = get_common_fields("ohfy__Lot_Inventory__c", source, target)
    if li_fields:
        li_records = extract_records("ohfy__Lot_Inventory__c", li_fields, source)
        print(f"  Extracted {len(li_records)} lot inventory records")

        output_fields = [f for f in li_fields if f != "Id"]

        # Resolve Lot__c and Inventory__c lookups
        # Lot: resolve via Lot Key__c
        # Inventory: resolve via composite key
        for rec in li_records:
            # RecordTypeId
            if "RecordTypeId" in rec and rec["RecordTypeId"]:
                rec["RecordTypeId"] = rt_map.get(rec["RecordTypeId"], rec["RecordTypeId"])

            # Lot lookup (Lot uses Lot_Identifier__c as bridge key)
            if "ohfy__Lot__c" in rec and rec["ohfy__Lot__c"]:
                rec["ohfy__Lot__c"] = resolver.resolve("Lot", rec["ohfy__Lot__c"])

            # Inventory lookup — need composite key resolution
            if "ohfy__Inventory__c" in rec and rec["ohfy__Inventory__c"]:
                rec["ohfy__Inventory__c"] = resolver.resolve("Inventory", rec["ohfy__Inventory__c"])

            # OwnerId
            for uf in USER_LOOKUP_FIELDS:
                if uf in rec and rec[uf]:
                    rec[uf] = owner_id

        csv_path = write_csv(li_records, output_fields, OUTPUT_DIR / "Lot_Inventory.csv")

        if not dry_run:
            load_object("ohfy__Lot_Inventory__c", csv_path, target)


# ── Pre-flight & Validation ──────────────────────────────────────────────────


def preflight(source, target):
    """Verify both orgs are connected."""
    print("Pre-flight checks...")
    for org_alias in [source, target]:
        result = subprocess.run(
            ["sf", "org", "display", "--target-org", org_alias, "--json"],
            capture_output=True,
            text=True,
        )
        try:
            data = json.loads(result.stdout)
            status = data.get("result", {}).get("connectedStatus", "Unknown")
            print(f"  {org_alias}: {status}")
            if status != "Connected":
                print(f"  ERROR: {org_alias} not connected!", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError:
            print(f"  ERROR: Cannot parse response for {org_alias}", file=sys.stderr)
            sys.exit(1)


def build_record_type_map(source, target):
    """Build source RT ID → target RT ID mapping via DeveloperName."""
    print("\nBuilding RecordType mapping...")
    source_rts = run_sf_query(
        "SELECT Id, SobjectType, DeveloperName FROM RecordType WHERE IsActive = true",
        source,
    )
    target_rts = run_sf_query(
        "SELECT Id, SobjectType, DeveloperName FROM RecordType WHERE IsActive = true",
        target,
    )

    # Target lookup by (SobjectType, DeveloperName)
    target_lookup = {}
    for r in target_rts:
        key = (r["SobjectType"], r["DeveloperName"])
        target_lookup[key] = r["Id"]

    # Build mapping
    rt_map = {}
    missing = []
    for r in source_rts:
        key = (r["SobjectType"], r["DeveloperName"])
        if key in target_lookup:
            rt_map[r["Id"]] = target_lookup[key]
        else:
            missing.append(f"{r['SobjectType']}/{r['DeveloperName']}")

    print(f"  Mapped {len(rt_map)} record types")
    if missing:
        print(f"  Missing in target: {', '.join(missing)}")

    return rt_map


def validate(source, target):
    """Compare record counts between source and target."""
    print("\n" + "=" * 60)
    print("VALIDATION: Source vs Target Record Counts")
    print("=" * 60)

    objects = [
        ("Account", "Account"),
        ("Contact", "Contact"),
        ("Territory", "ohfy__Territory__c"),
        ("Fee", "ohfy__Fee__c"),
        ("Pricelist", "ohfy__Pricelist__c"),
        ("Trans. Setting", "ohfy__Transformation_Setting__c"),
        ("Location", "ohfy__Location__c"),
        ("Equipment", "ohfy__Equipment__c"),
        ("Item_Line", "ohfy__Item_Line__c"),
        ("Item_Type", "ohfy__Item_Type__c"),
        ("Route", "ohfy__Route__c"),
        ("Item", "ohfy__Item__c"),
        ("Item_Component", "ohfy__Item_Component__c"),
        ("Lot", "ohfy__Lot__c"),
        ("Inventory", "ohfy__Inventory__c"),
        ("Pricelist_Item", "ohfy__Pricelist_Item__c"),
        ("Promotion", "ohfy__Promotion__c"),
        ("Account_Route", "ohfy__Account_Route__c"),
        ("Lot_Inventory", "ohfy__Lot_Inventory__c"),
    ]

    print(f"  {'Object':<20s} {'Source':>8s} {'Target':>8s} {'Match':>6s}")
    print(f"  {'─' * 20} {'─' * 8} {'─' * 8} {'─' * 6}")

    for label, sobject in objects:
        s_recs = run_sf_query(f"SELECT COUNT(Id) cnt FROM {sobject}", source)
        t_recs = run_sf_query(f"SELECT COUNT(Id) cnt FROM {sobject}", target)
        s_count = s_recs[0].get("cnt", "?") if s_recs else "ERR"
        t_count = t_recs[0].get("cnt", "?") if t_recs else "ERR"
        match = "OK" if str(s_count) == str(t_count) else "DIFF"
        print(f"  {label:<20s} {str(s_count):>8s} {str(t_count):>8s} {match:>6s}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Sandbox-to-sandbox Ohanafy migration")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source org alias")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target org alias")
    parser.add_argument("--dry-run", action="store_true", help="Generate CSVs only, don't load")
    parser.add_argument("--start-wave", type=int, default=1, help="Start from wave N")
    parser.add_argument("--waves", type=str, help="Comma-separated wave numbers to run (e.g., 1,2,3)")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation")
    args = parser.parse_args()

    source = args.source
    target = args.target
    dry_run = args.dry_run
    start_wave = args.start_wave

    if args.waves:
        waves_to_run = set(int(w) for w in args.waves.split(","))
    else:
        waves_to_run = set(range(start_wave, 9))

    print("=" * 60)
    print("Ohanafy Sandbox-to-Sandbox Migration")
    print("=" * 60)
    print(f"  Source: {source}")
    print(f"  Target: {target}")
    print(f"  Dry run: {dry_run}")
    print(f"  Waves: {sorted(waves_to_run)}")
    print(f"  Output: {OUTPUT_DIR}")

    # Pre-flight
    preflight(source, target)

    if args.validate_only:
        validate(source, target)
        return

    # Build RT map
    rt_map = build_record_type_map(source, target)
    owner_id = CAM_USER_ID

    # Initialize resolver
    resolver = IdResolver()

    # When resuming from a later wave, we need the ID mappings from earlier waves.
    # Pre-populate resolver from both orgs for all objects.
    if start_wave > 1 or (args.waves and min(waves_to_run) > 1):
        print("\nPre-populating ID resolver from existing data...")
        preload_objects = [
            ("Territory", "ohfy__Territory__c", "Name"),
            ("Fee", "ohfy__Fee__c", "ohfy__Key__c"),
            ("Pricelist", "ohfy__Pricelist__c", "ohfy__Key__c"),
            ("Transformation_Setting", "ohfy__Transformation_Setting__c", "ohfy__Key__c"),
            ("Account", "Account", "ohfy__External_ID__c"),
            ("Location", "ohfy__Location__c", "ohfy__Key__c"),
            ("Equipment", "ohfy__Equipment__c", "ohfy__Key__c"),
            ("Item_Line", "ohfy__Item_Line__c", "ohfy__Key__c"),
            ("Item_Type", "ohfy__Item_Type__c", "ohfy__Key__c"),
            ("Route", "ohfy__Route__c", "ohfy__Key__c"),
            ("Item", "ohfy__Item__c", "ohfy__Key__c"),
            ("Lot", "ohfy__Lot__c", "ohfy__Lot_Identifier__c"),
        ]
        for name, sobject, key_field in preload_objects:
            # Source
            src_recs = run_sf_query(f"SELECT Id, {key_field} FROM {sobject} WHERE {key_field} != null", source)
            for r in src_recs:
                resolver.register_source(name, r["Id"], r[key_field])
            # Target
            tgt_recs = run_sf_query(f"SELECT Id, {key_field} FROM {sobject} WHERE {key_field} != null", target)
            for r in tgt_recs:
                resolver.register_target(name, r[key_field], r["Id"])
            print(f"  {name}: {len(src_recs)} source, {len(tgt_recs)} target")

        # Pre-populate Inventory composite keys if needed for wave 8
        if 8 in waves_to_run:
            src_inv = run_sf_query(
                "SELECT Id, ohfy__Item__r.ohfy__Key__c, ohfy__Location__r.ohfy__Key__c FROM ohfy__Inventory__c", source
            )
            for r in src_inv:
                ik = (r.get("ohfy__Item__r") or {}).get("ohfy__Key__c", "")
                lk = (r.get("ohfy__Location__r") or {}).get("ohfy__Key__c", "")
                ck = f"{ik}|{lk}"
                if ck != "|":
                    resolver.register_source("Inventory", r["Id"], ck)
            tgt_inv = run_sf_query(
                "SELECT Id, ohfy__Item__r.ohfy__Key__c, ohfy__Location__r.ohfy__Key__c FROM ohfy__Inventory__c", target
            )
            for r in tgt_inv:
                ik = (r.get("ohfy__Item__r") or {}).get("ohfy__Key__c", "")
                lk = (r.get("ohfy__Location__r") or {}).get("ohfy__Key__c", "")
                ck = f"{ik}|{lk}"
                if ck != "|":
                    resolver.register_target("Inventory", ck, r["Id"])
            print(f"  Inventory: {len(src_inv)} source, {len(tgt_inv)} target")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run waves
    wave_funcs = {
        1: wave_1,
        2: wave_2,
        3: wave_3,
        4: wave_4,
        5: wave_5,
        6: wave_6,
        7: wave_7,
        8: wave_8,
    }

    for wave_num in sorted(waves_to_run):
        if wave_num in wave_funcs:
            wave_funcs[wave_num](source, target, resolver, rt_map, owner_id, dry_run)

    # Final validation
    if not dry_run:
        validate(source, target)

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
