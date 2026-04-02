#!/usr/bin/env python3
"""
VIP-to-Ohanafy Migration Script
================================
Connects to a VIP PostgreSQL database, extracts and transforms data,
and pushes it to a Google Sheet with tabs for each Ohanafy object.

Headers use Ohanafy API field names. A Loading Guide tab explains
load order, dependencies, and instructions.

Usage:
    python3 vip_to_ohanafy.py
    python3 vip_to_ohanafy.py --csv-only   # Generate CSVs without Google Sheets
    python3 vip_to_ohanafy.py --sheet-id <ID>  # Override target sheet
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import gspread
import psycopg2
import psycopg2.extras
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONFIG_DIR = Path("/Users/danielzeder/conductor/repos/VIP to Ohanafy")

DEFAULT_SHEET_ID = "108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE"
SERVICE_ACCOUNT_PATH = CONFIG_DIR / "service-account.json"

# DB connection defaults (overridable via env vars)
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

# ---------------------------------------------------------------------------
# Record Type IDs — loaded from migration_output/record_types.csv
# Keyed by (SobjectType, Name) → Id
# ---------------------------------------------------------------------------
RECORD_TYPE_IDS = {}


def load_record_types():
    """Load record type IDs from CSV into RECORD_TYPE_IDS dict."""
    rt_path = Path(__file__).parent / "migration_output" / "record_type_ids.csv"
    if rt_path.exists():
        with open(rt_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["SobjectType"], row["Name"])
                RECORD_TYPE_IDS[key] = row["Id"]


def get_record_type_id(sobject, name):
    """Look up a RecordTypeId. Returns empty string if not found."""
    if not RECORD_TYPE_IDS:
        load_record_types()
    return RECORD_TYPE_IDS.get((sobject, name), "")


# ---------------------------------------------------------------------------
# Supplier → AP Vendor Override Mappings
# Loaded from migration_output/supplier_vendor_overrides.csv
# These are human-reviewed fuzzy matches for suppliers that couldn't be
# auto-matched to APVENT records via the SQL join paths.
# ---------------------------------------------------------------------------
SUPPLIER_OVERRIDES = {}


def load_supplier_overrides():
    """Load supplier→vrvend overrides from CSV."""
    ov_path = Path(__file__).parent / "migration_output" / "supplier_vendor_overrides.csv"
    if ov_path.exists():
        with open(ov_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                SUPPLIER_OVERRIDES[row["supplier_code"].strip()] = row["vrvend"].strip()
        print(f"  Loaded {len(SUPPLIER_OVERRIDES)} supplier→vendor overrides")


def get_supplier_override_sql():
    """Build a VALUES clause for supplier overrides to inject into the query."""
    if not SUPPLIER_OVERRIDES:
        load_supplier_overrides()
    if not SUPPLIER_OVERRIDES:
        return ""
    values = ", ".join(f"('{code}', {vrvend})" for code, vrvend in SUPPLIER_OVERRIDES.items())
    return f"""
        UNION ALL
        -- Path 5: Human-reviewed fuzzy match overrides
        SELECT DISTINCT ON (s."SUPPLIER")
            TRIM(s."SUPPLIER") AS supplier_code,
            TRIM(s."SUPPLIER_NAME") AS supplier_name,
            TRIM(s."EDI_TRADING_PARTNER_ID") AS edi_id,
            s."IDENTITY" AS supplier_identity,
            ov.vrvend AS vrvend
        FROM staging."SUPPLIERT" s
        JOIN (VALUES {values}) AS ov(supplier_code, vrvend)
            ON TRIM(s."SUPPLIER") = ov.supplier_code
        WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
        ORDER BY s."SUPPLIER"
    """


# ---------------------------------------------------------------------------
# Tab definitions: ordered list of (tab_name, description, sql, headers)
# headers = list of Ohanafy API field names
# ---------------------------------------------------------------------------

TABS = []

# Friendly-name headers (Row 1 display name → Row 2 API name)
# If a tab has an entry here, Sheet gets two header rows.
FRIENDLY_HEADERS = {}


def register_tab(name, description, sql, headers, notes="", friendly_headers=None, load_order=99):
    """Register a migration tab."""
    TABS.append(
        {
            "name": name,
            "description": description,
            "sql": sql,
            "headers": headers,
            "notes": notes,
            "load_order": load_order,
        }
    )
    if friendly_headers:
        FRIENDLY_HEADERS[name] = friendly_headers


# ===== 1. Item Lines (Brand Families / Suppliers) =====
register_tab(
    name="Item_Lines",
    description="Brand families mapped from VIP Suppliers. Load FIRST - these are the top of the product hierarchy.",
    sql="""
        SELECT DISTINCT
            TRIM(s."SUPPLIER")        AS supplier_code,
            TRIM(s."SUPPLIER_NAME")   AS supplier_name,
            TRIM(s."SUPPLIER")        AS key_val,
            s."IDENTITY"              AS supplier_identity,
            (SELECT TRIM(i."PRODUCT_CLASS")
             FROM staging."ITEMT" i
             WHERE i.import_is_deleted = false
               AND TRIM(i."SUPPLIER_CODE") = TRIM(s."SUPPLIER")
             GROUP BY TRIM(i."PRODUCT_CLASS")
             ORDER BY COUNT(*) DESC
             LIMIT 1)                 AS dominant_product_class
        FROM staging."SUPPLIERT" s
        WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
        ORDER BY supplier_name
    """,
    headers=["Name", "ohfy__Supplier__r.ohfy__External_ID__c", "ohfy__Key__c", "ohfy__Type__c", "ohfy__External_ID__c"],
    notes="Name = SUPPLIER_NAME, Supplier__r = lookup via SUPPLIERT.IDENTITY → Account.External_ID__c. Key = SUPPLIER code. Type derived from dominant PRODUCT_CLASS of items.",
    load_order=2,
)


# ===== 2. Item Types (Brands) =====
register_tab(
    name="Item_Types",
    description="Brands mapped from VIP BRANDT. Requires Item_Lines loaded first.",
    sql="""
        SELECT DISTINCT
            TRIM(b."BRAND")                AS brand_code,
            TRIM(b."BRAND_NAME")           AS brand_name,
            TRIM(b."SUPPLIER")             AS supplier_code,
            TRIM(b."BRAND_FAMILY_XREF")    AS brand_family,
            TRIM(b."SELL_BY_BOTTLE")       AS sell_by_bottle,
            TRIM(b."QUOTA_TYPE")           AS quota_type,
            TRIM(b."PRICE_BOOK_DESCRIPTION") AS pb_desc,
            b."IDENTITY"                   AS vip_identity,
            (SELECT TRIM(i."PRODUCT_CLASS")
             FROM staging."ITEMT" i
             WHERE i.import_is_deleted = false
               AND TRIM(i."BRAND_CODE") = TRIM(b."BRAND")
             GROUP BY TRIM(i."PRODUCT_CLASS")
             ORDER BY COUNT(*) DESC
             LIMIT 1)                      AS dominant_product_class,
            (SELECT ROUND(AVG(i."ALCOHOL_PERCENT")::numeric, 1)
             FROM staging."ITEMT" i
             WHERE i.import_is_deleted = false
               AND TRIM(i."BRAND_CODE") = TRIM(b."BRAND")
               AND i."ALCOHOL_PERCENT" > 0) AS avg_abv,
            (SELECT STRING_AGG(DISTINCT TRIM(CAST(i."CONTAINER_TYPE_CODE" AS TEXT)), ','
                               ORDER BY TRIM(CAST(i."CONTAINER_TYPE_CODE" AS TEXT)))
             FROM staging."ITEMT" i
             WHERE i.import_is_deleted = false
               AND TRIM(i."BRAND_CODE") = TRIM(b."BRAND")
               AND TRIM(CAST(i."CONTAINER_TYPE_CODE" AS TEXT)) <> '') AS container_types
        FROM staging."BRANDT" b
        WHERE COALESCE(TRIM(b."DELETE_FLAG"), '') <> 'Y'
        ORDER BY brand_name
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Key__c",
        "ohfy__Item_Line__c",
        "ohfy__Subtype__c",
        "ohfy__Type__c",
        "ohfy__Short_Name__c",
        "ohfy__Supplier_Number__c",
        "ohfy__ABV__c",
        "ohfy__Packaging_Styles__c",
        "ohfy__External_ID__c",
    ],
    notes="Item_Line__c = lookup via VIP SUPPLIER code → Item_Line Key__c. Type/Subtype derived from dominant PRODUCT_CLASS. ABV = avg ALCOHOL_PERCENT across items. Packaging_Styles derived from CONTAINER_TYPE_CODE.",
    load_order=3,
)


# ===== 3. Suppliers (Account records) =====
register_tab(
    name="Suppliers",
    description="Supplier accounts from VIP SUPPLIERT + APVENT. Load BEFORE Items.",
    sql="""
        WITH supplier_vrvend AS (
            -- Map each SUPPLIERT to its best APVENT.VRVEND via multiple paths
            SELECT DISTINCT ON (s."SUPPLIER")
                TRIM(s."SUPPLIER") AS supplier_code,
                TRIM(s."SUPPLIER_NAME") AS supplier_name,
                TRIM(s."EDI_TRADING_PARTNER_ID") AS edi_id,
                s."IDENTITY" AS supplier_identity,
                v."VRVEND" AS vrvend
            FROM staging."SUPPLIERT" s
            LEFT JOIN staging."APVENT" v ON v.import_is_deleted = false
                AND (
                    -- Path 1: AP_VENDOR -> VRVEND
                    (TRIM(s."AP_VENDOR") <> '0' AND TRIM(s."AP_VENDOR") = CAST(v."VRVEND" AS TEXT))
                    OR
                    -- Path 2: bidirectional fuzzy name
                    (
                        LENGTH(REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g')) >= 3
                        AND (
                            REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g')
                                LIKE REGEXP_REPLACE(UPPER(TRIM(s."SUPPLIER_NAME")), '[^A-Z0-9]', '', 'g') || '%'
                            OR REGEXP_REPLACE(UPPER(TRIM(s."SUPPLIER_NAME")), '[^A-Z0-9]', '', 'g')
                                LIKE REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g') || '%'
                        )
                    )
                    OR
                    -- Path 3: AP_VENDOR -> VRIDENTITY
                    (TRIM(s."AP_VENDOR") <> '0' AND TRIM(s."AP_VENDOR") = CAST(v."VRIDENTITY" AS TEXT))
                    OR
                    -- Path 4: ORDERVENDORS AP_VENDOR_NUMBER -> VRVEND
                    EXISTS (
                        SELECT 1 FROM staging."ORDERVENDORS" o
                        WHERE TRIM(o."SUPPLIER") = TRIM(s."SUPPLIER")
                        AND COALESCE(o."DELETE_CODE", '') <> 'Y'
                        AND o."AP_VENDOR_NUMBER" <> 0
                        AND o."AP_VENDOR_NUMBER" = v."VRVEND"
                    )
                )
            WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
            ORDER BY s."SUPPLIER", v."VRADD1" IS NULL, v."VRVEND" NULLS LAST
        )
        SELECT
            COALESCE(sv.supplier_code, CAST(v."VRVEND" AS TEXT)) AS supplier_code,
            COALESCE(sv.supplier_name, TRIM(v."VRNAME"))    AS supplier_name,
            TRIM(v."VRADD1")            AS address1,
            TRIM(v."VRADD2")            AS address2,
            TRIM(c."CITYNAME")          AS city,
            TRIM(c."STATE")             AS state_code,
            v."VRPHON"                  AS phone,
            TRIM(v."VREMAIL")           AS email,
            v."VRFAX"                   AS fax,
            TRIM(v."POSTALCODE")        AS postal_code,
            TRIM(v."VRNAME")            AS vendor_name,
            TRIM(v."VRSSTAT")           AS status,
            TRIM(v."VRDESC")            AS vendor_desc,
            v."VRVEND"                  AS vendor_id,
            TRIM(v."VRSALESTX")         AS sales_tax_flag,
            COALESCE(sv.edi_id, '')     AS edi_id,
            v."VRDUEC"                  AS due_code,
            v."VRDUED"                  AS due_days,
            v."VRIDENTITY"              AS vip_identity,
            COALESCE(sv.supplier_identity::bigint, v."VRIDENTITY") AS supplier_identity,
            CASE WHEN sv.supplier_code IS NOT NULL THEN 'Supplier' ELSE 'Vendor' END AS vendor_type
        FROM staging."APVENT" v
        LEFT JOIN staging."CITYT" c ON v."ID_CITY" = c."IDENTITY"
        LEFT JOIN supplier_vrvend sv ON sv.vrvend = v."VRVEND"
        WHERE v.import_is_deleted = false

        UNION ALL

        -- Unmatched SUPPLIERT records (no APVENT match at all)
        SELECT
            sv.supplier_code, sv.supplier_name,
            NULL::character, NULL::character, NULL::character, NULL::character,
            NULL::numeric, NULL::character, NULL::numeric, NULL::character,
            NULL::character, NULL::character, NULL::character, NULL::numeric,
            NULL::character, COALESCE(sv.edi_id, ''),
            NULL::character, NULL::numeric, NULL::bigint,
            sv.supplier_identity::bigint, 'Supplier'
        FROM supplier_vrvend sv
        WHERE sv.vrvend IS NULL

        ORDER BY vendor_type, supplier_name
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Legal_Name__c",
        "ohfy__Customer_Number__c",
        "Type",
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
        "Website",
        "Description",
        "ohfy__Payment_Terms__c",
        "ohfy__Distributor_Vendor_ID_Number__c",
        "ohfy__GS1_Prefix__c",
        "ohfy__QuickBooks_Customer_ID__c",
        "ohfy__Is_Tax_Exempt__c",
        "ohfy__Is_Active__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Record Type ID",
        "Supplier Name",
        "Legal/Vendor Name",
        "Supplier Code",
        "Account Type",
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
        "Email/Website",
        "Description",
        "Payment Terms",
        "Supplier Code (Vendor ID)",
        "GS1/EDI ID",
        "AP Vendor # (QB ID)",
        "Tax Exempt?",
        "Active?",
        "External ID (VIP Identity)",
    ],
    notes="Type = 'Supplier'. Is_Active = true unless VRSSTAT = 'I'. External_ID__c = SUPPLIERT.IDENTITY. City/State from APVENT→CITYT join.",
    load_order=1,
)


# ===== 4. Chain Banners (Parent Account records) =====
register_tab(
    name="Chain_Banners",
    description="Chain/banner groupings from VIP HDRCHAINT. Load BEFORE Customers (Chain_Banner__c lookup).",
    sql="""
        WITH chain_addresses AS (
            SELECT
                TRIM(b."CMCHN") AS chain_code,
                TRIM(b."CMSTR") AS street,
                TRIM(c."CITYNAME") AS city,
                TRIM(c."STATE") AS state,
                TRIM(b."POSTALCODE") AS zip,
                b."CMPHON" AS phone,
                COUNT(*) AS addr_count,
                ROW_NUMBER() OVER (
                    PARTITION BY TRIM(b."CMCHN")
                    ORDER BY COUNT(*) DESC, TRIM(c."CITYNAME") NULLS LAST
                ) AS rn
            FROM staging."BRATTT" b
            LEFT JOIN staging."CITYT" c ON b."ID_CITY" = c."IDENTITY"
            WHERE COALESCE(TRIM(b."CMDELD"), '') <> 'Y'
              AND TRIM(b."CMCHN") <> ''
              AND TRIM(COALESCE(c."CITYNAME", '')) <> ''
            GROUP BY 1, 2, 3, 4, 5, 6
        )
        SELECT
            TRIM(h."CHAIN")         AS chain_code,
            TRIM(h."DESCRIPTION")   AS chain_name,
            h."IDENTITY"            AS vip_identity,
            TRIM(h."DELETEFLAG")    AS delete_flag,
            a.street                AS street,
            a.city                  AS city,
            a.state                 AS state,
            a.zip                   AS zip,
            a.phone                 AS phone,
            (SELECT COUNT(*) FROM staging."BRATTT" b2
             WHERE TRIM(b2."CMCHN") = TRIM(h."CHAIN")
             AND COALESCE(TRIM(b2."CMDELD"), '') <> 'Y') AS customer_count
        FROM staging."HDRCHAINT" h
        LEFT JOIN chain_addresses a ON a.chain_code = TRIM(h."CHAIN") AND a.rn = 1
        WHERE h.import_is_deleted = false
            AND COALESCE(TRIM(h."DELETEFLAG"), '') <> 'Y'
        ORDER BY TRIM(h."DESCRIPTION")
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Customer_Number__c",
        "Type",
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
        "ohfy__Is_Active__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Record Type ID",
        "Chain/Banner Name",
        "Chain Code",
        "Account Type",
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
        "Active?",
        "External ID (VIP Identity)",
    ],
    notes="Type = 'Chain Banner'. RecordTypeId = Chain Banner. Loaded before Customers so Chain_Banner__c lookup resolves.",
    load_order=1.5,
)


# ===== 5. Customers (Account records) =====
register_tab(
    name="Customers",
    description="Customer accounts from VIP BRATTT (master account table). Load BEFORE Invoices.",
    sql="""
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
            b."CMLATD"              AS latitude,
            b."CMLOND"              AS longitude,
            b."CMAR$"               AS ar_balance,
            b."CMCLIM"              AS credit_limit,
            TRIM(b."CMTERM")        AS payment_term,
            TRIM(b."CMTXCD")        AS tax_code,
            TRIM(b."CMCHN")         AS chain_code,
            TRIM(b."CMCLAS")        AS customer_class,
            TRIM(b."CMSTS")         AS status,
            CAST(b."CMONOF" AS TEXT) AS on_off_premise,
            TRIM(b."CMCOMP")        AS company,
            TRIM(b."CMWHSE")        AS warehouse,
            TRIM(b."CMETHO")        AS delivery_method,
            CAST(b."CMCDAY" AS TEXT) AS delivery_day,
            TRIM(b."CMDCOD")        AS delete_code,
            TRIM(b."CMSCLS")        AS sub_class,
            TRIM(b."CMLIFE")        AS lifestyle,
            TRIM(b."CMPGRP")        AS price_group,
            b."CMGLN"               AS gln,
            TRIM(b."CMCYCL")        AS delivery_cycle,
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
        ORDER BY dba_name
    """,
    headers=[
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
        "ohfy__Route__c",
        "ohfy__Sales_Rep__c",
        "ohfy__Chain_Banner__c",
        "ohfy__Customer_Class__c",
        "ohfy__License_Number__c",
        "ohfy__ABC_License_Number__c",
        "ohfy__ABC_License_Expiration_Date__c",
        "ohfy__Payment_Terms__c",
        "ohfy__Is_Tax_Exempt__c",
        "ohfy__Credit_Limit__c",
        "ohfy__Account_Balance__c",
        "ohfy__Latitude__c",
        "ohfy__Longitude__c",
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
    ],
    friendly_headers=[
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
        "Route",
        "Sales Rep",
        "Chain/Banner",
        "Customer Class",
        "License #",
        "ABC License #",
        "ABC License Exp",
        "Payment Terms",
        "Tax Exempt?",
        "Credit Limit",
        "AR Balance",
        "Latitude",
        "Longitude",
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
    ],
    notes="Type = 'Customer'. Source: BRATTT (28K+ rows). RecordType based on CMONOF (On/Off Premise). External_ID__c = CMIDENTITY.",
    load_order=10,
)


# ===== 5. Items (Products) =====
register_tab(
    name="Items",
    description="Products from VIP ITEMT. Requires Item_Types and Suppliers loaded first.",
    sql="""
        SELECT
            TRIM(i."ITEM_CODE")            AS item_code,
            TRIM(i."PACKAGE_DESCRIPTION")  AS pkg_desc,
            TRIM(i."PACKAGE_SHORT")        AS pkg_short,
            TRIM(i."BRAND_CODE")           AS brand_code,
            TRIM(i."SUPPLIER_CODE")        AS supplier_code,
            TRIM(i."PRODUCT_CLASS")        AS product_class,
            TRIM(i."ITEM_STATUS")          AS item_status,
            i."ALCOHOL_PERCENT"            AS abv,
            i."PROOF"                      AS proof,
            i."UNITS_CASE"                 AS units_per_case,
            i."MILLILITERS_PER_BOTTLE"     AS ml_per_bottle,
            i."OZ_CASE"                    AS oz_case,
            i."SUGGESTED_SELLING_PRICE"    AS ssp,
            i."CASE_WEIGHT"                AS case_weight,
            i."CASE_HEIGHT"                AS case_height,
            i."CASE_LENGTH"                AS case_length,
            i."CASE_WIDTH"                 AS case_width,
            i."CASES_KEGS_PER_PALLET"      AS per_pallet,
            i."BOTTLE_UPC"                 AS bottle_upc,
            i."CASE_UPC"                   AS case_upc,
            i."RETAIL_UPC"                 AS retail_upc,
            i."BOTTLE_GTIN"                AS bottle_gtin,
            i."CASE_GTIN"                  AS case_gtin,
            i."RETAIL_GTIN"                AS retail_gtin,
            TRIM(i."SUPPLIER_SKU")         AS supplier_sku,
            TRIM(i."PACKAGE_SIZE")         AS package_size,
            TRIM(i."COUNTRY_OF_ORIGIN_CODE") AS country,
            i."TAXABLE_FLAG"               AS taxable,
            i."SELLABLE_BY_UNIT"           AS sell_by_unit,
            TRIM(i."CONTAINER_TYPE_CODE")  AS container_type,
            i."DEPOSIT_ORIGIN"             AS deposit_origin,
            i."CUBE_VOLUME"                AS cube_volume,
            i."CASE_HEIGHT"                AS case_height,
            i."CASE_LENGTH"                AS case_length,
            i."CASE_WIDTH"                 AS case_width,
            i."MILLILITERS_PER_BOTTLE"     AS ml_per_bottle,
            i."OZ_CASE"                    AS oz_case,
            i."HANDLING_CHARGE"            AS handling_charge,
            i."COOPERAGE"                  AS cooperage,
            TRIM(i."COUNTRY_OF_ORIGIN_CODE") AS country,
            TRIM(i."STYLE_TYPE_CODE")      AS style_code,
            TRIM(i."REGION_CODE")          AS region_code,
            TRIM(i."APPELLATION_CODE")     AS appellation,
            TRIM(i."FOREIGN_DOMESTIC_FLAG") AS foreign_domestic,
            TRIM(i."PRODUCT_CODE")         AS product_code,
            i."COMMISSION_RATE"            AS commission_rate,
            i."PALLET_UPC"                 AS pallet_upc,
            i."RETAIL_SELL_UNITS_CASE"  AS retail_units_case,
            i."IDENTITY"                   AS vip_identity,
            TRIM(i."UNIT_OF_MEASURE_CODE") AS uom_code,
            (SELECT MAX(d."DPDEPO") FROM staging."DEPOSITST" d
             WHERE TRIM(d."DPITEM") = TRIM(i."ITEM_CODE")
               AND d."DPDEPTYP" = 'K')  AS deposit_amount
        FROM staging."ITEMT" i
        WHERE i.import_is_deleted = false
        ORDER BY pkg_desc
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Item_Number__c",
        "ohfy__Item_Type__c",
        "ohfy__Item_Line__c",
        "ohfy__Type__c",
        "ohfy__Package_Type__c",
        "ohfy__Packaging_Type__c",
        "ohfy__Packaging_Type_Short_Name__c",
        "ohfy__UOM__c",
        "ohfy__Units_Per_Case__c",
        "ohfy__Weight__c",
        "ohfy__Weight_UOM__c",
        "ohfy__Cases_Per_Pallet__c",
        "ohfy__Default_Case_Price__c",
        "ohfy__Case_UPC__c",
        "ohfy__Case_GTIN__c",
        "ohfy__Unit_UPC__c",
        "ohfy__Unit_GTIN__c",
        "ohfy__Retailer_UPC__c",
        "ohfy__UPC__c",
        "ohfy__Supplier_Number__c",
        "ohfy__SKU_Number__c",
        "ohfy__State_Item_Code__c",
        "ohfy__Short_Name__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Tax_Exempt__c",
        "ohfy__Is_Sold_In_Units__c",
        "ohfy__Can_Credit_In_Units__c",
        "ohfy__Keg_Deposit__c",
        "ohfy__Carrier_UPC__c",
        "ohfy__Pack_GTIN__c",
        "ohfy__UOM_In_Fluid_Ounces__c",
        "ohfy__Retail_Units_Per_Case__c",
        "ohfy__Item_Purposes__c",
        "ohfy__Is_Lot_Tracked__c",
        "ohfy__Credit_Type__c",
        "ohfy__VIP_External_ID__c",
        "ohfy__External_ID__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Product Name",
        "Item Code",
        "Brand (Item Type)",
        "Supplier (Item Line)",
        "Type",
        "Package Type",
        "Packaging Type",
        "Pkg Type Short",
        "UOM",
        "Units/Case",
        "Weight",
        "Weight UOM",
        "Cases/Pallet",
        "Default Price",
        "Case UPC",
        "Case GTIN",
        "Unit UPC",
        "Unit GTIN",
        "Retail UPC",
        "Universal Product Code",
        "Supplier Number",
        "SKU Number",
        "State Item Code",
        "Short Name",
        "Active?",
        "Tax Exempt?",
        "Sold in Units?",
        "Credit in Units?",
        "Keg Deposit",
        "Carrier UPC",
        "Pack GTIN",
        "Fluid Oz/Case",
        "Retail Units/Case",
        "Item Purpose(s)",
        "Lot Tracked?",
        "Credit Type",
        "VIP External ID",
        "External ID",
        "Key",
    ],
    notes=(
        "Item_Type__c = lookup via BRAND_CODE → Item_Type Key__c. "
        "Item_Line__c = lookup via SUPPLIER_CODE → Item_Line Key__c. "
        "Type__c = Ohanafy record type from VIP PRODUCT_CLASS (Finished Good / Merchandise / Overhead). "
        "Package_Type__c = Kegged (container codes 700-730,590) or Packaged. "
        "Packaging_Type__c = mapped to Ohanafy picklist (1/6 Barrel(s), 1/2 Barrel(s), etc.). "
        "Keg_Deposit__c = VIP COOPERAGE value (deposit code for keg shells). "
        "Removed fields not on target org: ABV__c, Container_Type__c, Country_of_Origin__c, Style__c, UOM_Sub_Type__c, vipid__c."
    ),
    load_order=11,
)


# ===== 5b. Keg Shell Items (Empty keg deposits per supplier/size) =====
register_tab(
    name="Keg_Shell_Items",
    description="Empty keg shell items (Dunnage) — one per supplier per keg size. Load AFTER Items.",
    sql="""
        SELECT DISTINCT
            TRIM(i."SUPPLIER_CODE")        AS supplier_code,
            TRIM(s."SUPPLIER_NAME")        AS supplier_name,
            TRIM(i."CONTAINER_TYPE_CODE")  AS container_code,
            TRIM(ct."CONTAINERNAME")       AS container_name,
            -- Pick one brand code per supplier to use as Item_Type lookup
            (SELECT TRIM(b2."BRAND")
             FROM staging."ITEMT" i2
             JOIN staging."BRANDT" b2 ON TRIM(i2."BRAND_CODE") = TRIM(b2."BRAND")
             WHERE TRIM(i2."SUPPLIER_CODE") = TRIM(i."SUPPLIER_CODE")
               AND TRIM(i2."CONTAINER_TYPE_CODE") = TRIM(i."CONTAINER_TYPE_CODE")
               AND i2.import_is_deleted = false
             GROUP BY b2."BRAND"
             ORDER BY COUNT(*) DESC
             LIMIT 1)                      AS brand_code
        FROM staging."ITEMT" i
        JOIN staging."CONTTYPET" ct ON TRIM(i."CONTAINER_TYPE_CODE") = TRIM(ct."CONTAINERID")
        JOIN staging."SUPPLIERT" s ON TRIM(i."SUPPLIER_CODE") = TRIM(s."SUPPLIER")
        WHERE i.import_is_deleted = false
          AND TRIM(i."CONTAINER_TYPE_CODE") IN ('710','720','730','700','705','706','707','590')
          AND COALESCE(TRIM(i."PRODUCT_CLASS"), '') NOT IN ('09','40')
        ORDER BY supplier_name, container_name
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Item_Number__c",
        "ohfy__Item_Type__c",
        "ohfy__Item_Line__c",
        "ohfy__Type__c",
        "ohfy__Package_Type__c",
        "ohfy__UOM__c",
        "ohfy__Packaging_Type__c",
        "ohfy__Weight_UOM__c",
        "ohfy__Is_Active__c",
        "ohfy__Item_Purposes__c",
        "ohfy__Is_Tax_Exempt__c",
        "ohfy__Keg_Deposit__c",
        "ohfy__Credit_Type__c",
        "ohfy__Units_Per_Case__c",
        "ohfy__VIP_External_ID__c",
        "ohfy__External_ID__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Record Type",
        "Name",
        "Item Number",
        "Brand (Item Type)",
        "Supplier (Item Line)",
        "Type",
        "Package Type",
        "UOM",
        "Packaging Type",
        "Weight UOM",
        "Active?",
        "Item Purpose(s)",
        "Tax Exempt?",
        "Keg Deposit",
        "Credit Type",
        "Units/Case",
        "VIP External ID",
        "External ID",
        "Key",
    ],
    notes=(
        "Derived: one empty keg shell per supplier + keg size combo. "
        "These are Dunnage items representing returnable keg shells for deposit tracking. "
        "Key = KEG-SHELL-{SUPPLIER_CODE}-{CONTAINER_CODE}."
    ),
    load_order=12,
)


# ===== 5c. Item Components (Keg deposit links) =====
register_tab(
    name="Item_Components",
    description="Links keg products to their empty keg shell (deposit item). Load AFTER Keg_Shell_Items.",
    sql="""
        SELECT
            TRIM(i."ITEM_CODE")            AS item_code,
            TRIM(i."SUPPLIER_CODE")        AS supplier_code,
            TRIM(i."CONTAINER_TYPE_CODE")  AS container_code
        FROM staging."ITEMT" i
        WHERE i.import_is_deleted = false
          AND TRIM(i."CONTAINER_TYPE_CODE") IN ('710','720','730','700','705','706','707','590')
          AND COALESCE(TRIM(i."PRODUCT_CLASS"), '') NOT IN ('09','40')
        ORDER BY i."ITEM_CODE"
    """,
    headers=[
        "ohfy__Parent_Item__c",
        "ohfy__Child_Item__c",
        "ohfy__Quantity__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Parent Item (Key__c)",
        "Child Item (Key__c)",
        "Quantity",
        "Key",
    ],
    notes=(
        "One row per kegged item → matching empty keg shell. "
        "Parent_Item__c and Child_Item__c contain Key__c values for lookup resolution. "
        "At SF load time, resolve to actual SF record IDs (master-detail requires IDs, not external IDs)."
    ),
    load_order=13,
)


# ===== 6. Parent Locations (Warehouses) =====
register_tab(
    name="Parent_Locations",
    description="Top-level warehouse locations from HDRWHSET. Load BEFORE Child Locations.",
    sql="""
        SELECT DISTINCT
            TRIM(w."WAREHOUSE")       AS warehouse_code,
            TRIM(w."WAREHOUSE_NAME")  AS warehouse_name,
            TRIM(w."ACCOUNT")         AS account,
            TRIM(w."GL_COMPANY")      AS gl_company,
            w."IDENTITY"              AS vip_identity
        FROM staging."HDRWHSET" w
        WHERE COALESCE(TRIM(w."DELETE_FLAG"), '') <> 'Y'
          AND w.import_is_deleted = false
        ORDER BY warehouse_code
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Type__c",
        "ohfy__Key__c",
        "ohfy__Location_Code__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Finished_Good__c",
        "ohfy__Is_Sellable__c",
        "ohfy__Is_Merchandise__c",
        "ohfy__Is_Tap_Handle__c",
        "ohfy__Is_Dirty_Keg_Location__c",
        "ohfy__Is_Keg_Shell__c",
        "ohfy__Is_Truck__c",
        "ohfy__Location_Street__c",
        "ohfy__Location_City__c",
        "ohfy__Location_State__c",
        "ohfy__Location_Postal_Code__c",
        "ohfy__Location_County__c",
        "ohfy__Company__c",
        "ohfy__Notes__c",
    ],
    notes="Type__c = 'Warehouse'. RecordTypeId = Parent_Location. Source: HDRWHSET.",
    load_order=6,
)


# ===== 7. Child Locations (Zones derived from location code prefix) =====
register_tab(
    name="Child_Locations",
    description="Zone-level locations within warehouses, derived from the first character of each location code. Requires Parent Locations loaded.",
    sql="""
        SELECT DISTINCT
            TRIM("LCWHSE")                    AS warehouse_code,
            LEFT(TRIM("LCLOC"), 1)            AS zone_code
        FROM staging."LOCMAST"
        WHERE import_is_deleted = false
          AND TRIM("LCLOC") <> ''
          AND LEFT(TRIM("LCLOC"), 1) ~ '[A-Za-z0-9]'
        ORDER BY warehouse_code, zone_code
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Parent_Location__c",
        "ohfy__Type__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Sellable__c",
        "ohfy__Key__c",
        "ohfy__Location_Code__c",
    ],
    notes="Parent_Location__c = lookup via warehouse Key__c. Type__c = 'Zone'. RecordTypeId = Location.",
    load_order=7,
)


# ===== 8. Pick Path Locations (Bins within zones) =====
register_tab(
    name="Pick_Paths",
    description="Bin-level locations within zones. Requires Child Locations (Zones) loaded.",
    sql="""
        SELECT
            TRIM("LCLOC")      AS location_code,
            TRIM("LCDESC")     AS location_desc,
            TRIM("LCWHSE")     AS warehouse_code,
            LEFT(TRIM("LCLOC"), 1) AS zone_code,
            TRIM("LCSTAT")     AS status,
            TRIM("LCPICK")     AS is_pick,
            TRIM("LCSTAG")     AS is_staging,
            TRIM("LCAVAIL")    AS is_available,
            TRIM("LCBOND")     AS is_bonded,
            TRIM("LCPALL")     AS is_pallet,
            "LCLOCSEQ"         AS pick_sequence,
            "LCXCOR"           AS x_coord,
            "LCYCOR"           AS y_coord,
            "LCCAPC"           AS capacity_cases,
            "LCCAPP"           AS capacity_pallets,
            "LCMIN"            AS min_qty,
            "IDENTITY"         AS vip_identity
        FROM staging."LOCMAST"
        WHERE import_is_deleted = false
          AND TRIM("LCLOC") <> ''
        ORDER BY warehouse_code, zone_code, location_code
    """,
    headers=[
        "Name",
        "ohfy__Parent_Location__c",
        "ohfy__Type__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Sellable__c",
        "ohfy__Is_Finished_Good__c",
        "ohfy__Is_Dirty_Keg_Location__c",
        "ohfy__Notes__c",
        "ohfy__Key__c",
    ],
    notes="Parent_Location__c = lookup via zone Key__c. Type = 'Bin'. Location_Code__c and Location_Number__c are formulas (not writable).",
    load_order=8,
)


# ===== 9. Territories (Parent = Warehouse regions) =====
register_tab(
    name="Territories",
    description="Parent territories derived from warehouses (geographic regions). Child territories TBD after research on VIP brand territory model.",
    sql="""
        SELECT DISTINCT
            TRIM(w."WAREHOUSE")       AS warehouse_code,
            TRIM(w."WAREHOUSE_NAME")  AS warehouse_name,
            w."IDENTITY"              AS vip_identity
        FROM staging."HDRWHSET" w
        WHERE COALESCE(TRIM(w."DELETE_FLAG"), '') <> 'Y'
          AND w.import_is_deleted = false
        ORDER BY warehouse_code
    """,
    headers=["Name", "ohfy__Is_Active__c"],
    notes="Parent territories = warehouse geographic regions. No Key__c or External_ID__c on Territory__c. Child territories (brand-based from HDRTERRT) to be added later.",
    load_order=4,
)


# ===== 10. Equipment / Vehicles (Trucks) =====
register_tab(
    name="Equipment_Vehicles",
    description="Trucks and vehicles from VIP TRUCKT. Load BEFORE Routes.",
    sql="""
        SELECT
            TRIM("TUTRK#")   AS truck_number,
            TRIM("TUDESC")   AS truck_desc,
            TRIM("TUTYPE")   AS truck_type,
            "TUCLBS"          AS capacity_lbs,
            "TUBAYS"          AS bay_count,
            TRIM("TUDCOD")    AS delete_code,
            "IDENTITY"        AS vip_identity
        FROM staging."TRUCKT"
        WHERE import_is_deleted = false
        ORDER BY truck_number
    """,
    headers=[
        "Name",
        "ohfy__Abbreviation__c",
        "ohfy__Type__c",
        "ohfy__Status__c",
        "ohfy__Tare_Weight__c",
        "ohfy__Key__c",
        "ohfy__External_ID__c",
    ],
    notes="Name = truck description. Type__c = 'Truck'. Fulfillment_Location__c set after locations loaded.",
    load_order=5,
)


# ===== 11. Routes =====
register_tab(
    name="Routes",
    description="Delivery/Sales routes from VIP HDRROUTET. Requires Territories and Equipment loaded.",
    sql="""
        SELECT
            TRIM(r."ROUTE")       AS route_code,
            TRIM(r."DESCRIPTION") AS route_desc,
            TRIM(r."DELETEFLAG")  AS delete_flag,
            r."IDENTITY"          AS vip_identity
        FROM staging."HDRROUTET" r
        WHERE COALESCE(TRIM(r."DELETEFLAG"), '') <> 'Y'
          AND r.import_is_deleted = false
        ORDER BY route_code
    """,
    headers=[
        "Name",
        "ohfy__Type__c",
        "ohfy__Frequency__c",
        "ohfy__Is_Active__c",
        "ohfy__Key__c",
    ],
    notes="Name = 'Route {code}'. Type__c = 'Delivery'. Key__c = route code. Driver__c and Vehicle__c set post-load.",
    load_order=9,
)


# ===== 12. Fees =====
register_tab(
    name="Fees",
    description="Deposit/fee structures from VIP DEPOSITST.",
    sql="""
        SELECT DISTINCT
            TRIM("DPDEPTYP")   AS deposit_type,
            "DPDEPO"           AS deposit_amount,
            TRIM("DPTYPE")     AS fee_type,
            TRIM("DPITEM")     AS item_code,
            "DPSDAT"           AS start_date,
            "DPEDAT"           AS end_date,
            "DPIDENTITY"       AS vip_identity
        FROM staging."DEPOSITST"
        WHERE import_is_deleted = false
          AND "DPDEPO" IS NOT NULL
          AND "DPDEPO" <> 0
        ORDER BY deposit_type, item_code
    """,
    headers=[
        "Name",
        "ohfy__Default_Amount__c",
        "ohfy__Type__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Invoice__c",
        "ohfy__Is_Inventory_Receipt__c",
        "ohfy__Key__c",
        "ohfy__External_ID__c",
    ],
    notes="Name = deposit type description. Default_Amount__c = DPDEPO. Type__c derived from DPDEPTYP.",
    load_order=12,
)


# ===== 13. Pricelists =====
register_tab(
    name="Pricelists",
    description="Discount worksheets / price lists from VIP DISCWKSTT.",
    sql="""
        SELECT
            TRIM("DISCOUNTID")    AS discount_code,
            TRIM("DISCDESC")      AS discount_desc,
            TRIM("DISCOUNTTYPE")  AS discount_type,
            "STARTDATE"           AS start_date,
            "ENDDATE"             AS end_date,
            TRIM("BYBOTTLE")      AS by_bottle,
            TRIM("DISCLVL")       AS discount_level,
            "ID_WORKSHEET"        AS worksheet_id,
            "IDENTITY"            AS vip_identity
        FROM staging."DISCWKSTT"
        WHERE import_is_deleted = false
          AND TRIM("DISCOUNTID") <> ''
        ORDER BY discount_desc
    """,
    headers=[
        "Name",
        "ohfy__Type__c",
        "ohfy__Discount_Type__c",
        "ohfy__Start_Date__c",
        "ohfy__End_Date__c",
        "ohfy__Is_Active__c",
        "ohfy__Key__c",
    ],
    notes="Name = DISCDESC. Type__c = 'Discount' or 'Individual Price' based on DISCOUNTTYPE.",
    load_order=13,
)


# ===== 14. Pricelist Items =====
register_tab(
    name="Pricelist_Items",
    description="Item-level pricing from VIP PENDPRICT. Requires Pricelists and Items loaded.",
    sql="""
        SELECT
            TRIM("PRODID")    AS item_code,
            TRIM("CODEID")    AS price_code,
            TRIM("DISCCODE")  AS discount_code,
            "CASEPRICE"       AS case_price,
            "EACHPRICE"       AS each_price,
            "POSTOFF"         AS post_off,
            TRIM("DISCGRP")   AS disc_group,
            "STARTDATE"       AS start_date,
            "ENDDATE"         AS end_date,
            TRIM("TYPEID")    AS type_id,
            "IDENTITY"        AS vip_identity
        FROM staging."PENDPRICT"
        WHERE import_is_deleted = false
          AND "CASEPRICE" IS NOT NULL
        ORDER BY item_code, price_code
    """,
    headers=[
        "ohfy__Item__c",
        "ohfy__Pricelist__c",
        "ohfy__Case_Price__c",
        "ohfy__Unit_Price__c",
        "ohfy__Discount_Dollars__c",
        "ohfy__Discount_Percent__c",
        "ohfy__Key__c",
        "ohfy__External_ID__c",
    ],
    notes="Item__c = lookup via PRODID → Item External_ID__c. Pricelist__c = lookup via DISCCODE → Pricelist Key__c.",
    load_order=18,
)


# ===== 14b. Chain Pricelists (Demo) =====
# One pricelist per chain banner, using representative GDC price codes
# from the deployment master (DPMASTT/DPMAST1T).
register_tab(
    name="Chain_Pricelists",
    description="Customer-specific pricelists per chain banner. Based on VIP price codes from HDRPRCODT.",
    sql="""
        SELECT
            TRIM(h."CHAIN")       AS chain_code,
            TRIM(h."DESCRIPTION") AS chain_name,
            h."IDENTITY"          AS vip_identity
        FROM staging."HDRCHAINT" h
        WHERE h.import_is_deleted = false
          AND TRIM(h."CHAIN") IN (
            '1485','0735','0763','0760','0745','0750','0664',
            '1060','0755','0756','1145'
          )
        ORDER BY chain_name
    """,
    headers=[
        "Name",
        "ohfy__Type__c",
        "ohfy__Discount_Type__c",
        "ohfy__Start_Date__c",
        "ohfy__End_Date__c",
        "ohfy__Is_Active__c",
        "ohfy__Key__c",
    ],
    notes="Type = 'Settings' (customer-specific pricing). Key = 'CHP-{chain_code}'. Load BEFORE Chain_Pricelist_Items.",
    load_order=13.5,
)


# ===== 14c. Chain Pricelist Items (Demo) =====
# Selling prices per item per chain, from VIP deployment master.
# Scoped to 5 demo suppliers: Molson Coors (1C), Constellation (2F),
# Boston Beer (2U), SweetWater (3M), Red Bull (3N).
# Pulls from ALL division-specific price codes per chain to maximize coverage.
register_tab(
    name="Chain_Pricelist_Items",
    description="Item prices per chain pricelist from VIP deployment master. Requires Chain_Pricelists and Items loaded.",
    sql="""
        WITH ranked AS (
            SELECT
                TRIM(d."DPITEM")   AS item_code,
                TRIM(d."DPPRCD")   AS price_code,
                d1."SELLINGPRICE01" AS sell_price,
                d1."FRONTLINEPRICE" AS front_price,
                d."DPBDAT"         AS start_date,
                d."DPEDAT"         AS end_date,
                ROW_NUMBER() OVER (
                    PARTITION BY TRIM(d."DPITEM"), TRIM(d."DPPRCD")
                    ORDER BY d."DPEDAT" DESC, d."DPBDAT" DESC
                ) AS rn
            FROM staging."DPMASTT" d
            JOIN staging."DPMAST1T" d1 ON d."DPIDENTITY" = d1."ID_DPMAST"
            JOIN staging."ITEMT" i ON TRIM(d."DPITEM") = TRIM(i."ITEM_CODE")
            WHERE d.import_is_deleted = false
              AND d1.import_is_deleted = false
              AND i.import_is_deleted = false
              AND TRIM(i."SUPPLIER_CODE") IN ('1C','2F','2U','3M','3N')
              AND TRIM(d."DPPRCD") IN (
                  '1A','7A','8A','9A','HA',
                  '1C','7C','8C','9C','HC',
                  '01','11','71','81','91','H1','51',
                  '03','13','73','83','93','H3'
              )
              AND (d1."SELLINGPRICE01" > 0 OR d1."FRONTLINEPRICE" > 0)
        )
        SELECT item_code, price_code,
               sell_price, front_price,
               start_date, end_date
        FROM ranked
        WHERE rn = 1
        ORDER BY price_code, item_code
    """,
    headers=[
        "ohfy__Item__c",
        "ohfy__Pricelist__c",
        "ohfy__Case_Price__c",
        "ohfy__Key__c",
    ],
    notes="Item__c = lookup via item_code → Item Key__c. Pricelist__c = lookup via CHP-{chain} → Chain Pricelist Key__c. Case_Price = best of SELLINGPRICE01 or FRONTLINEPRICE.",
    load_order=18.5,
)


# ===== 15. Lots =====
ACTIVE_ITEMS_SQL = """
    SELECT TRIM("ITEM_CODE") AS item_code,
           TRIM("PACKAGE_DESCRIPTION") AS pkg_desc
    FROM staging."ITEMT"
    WHERE import_is_deleted = false
      AND TRIM("ITEM_STATUS") = 'A'
    ORDER BY "ITEM_CODE"
"""

LOTS_SQL = """
    SELECT DISTINCT
        TRIM(i."ITEM_CODE") AS item_code,
        TRIM(i."PACKAGE_DESCRIPTION") AS pkg_desc,
        TRIM(i."SUPPLIER_CODE") AS supplier_code,
        COALESCE(pc.latest_cost, 0) AS latest_cost
    FROM staging."ITEMT" i
    LEFT JOIN (
        SELECT "PDITEM", MAX("PDCST$") AS latest_cost
        FROM staging."PODTLT"
        WHERE "PDCST$" > 0
        GROUP BY "PDITEM"
    ) pc ON TRIM(pc."PDITEM") = TRIM(i."ITEM_CODE")
    WHERE i.import_is_deleted = false
      AND TRIM(i."ITEM_STATUS") = 'A'
    ORDER BY item_code
"""

register_tab(
    name="Lots",
    description="One Lot per active item. Expiration 2026-12-31. Includes Supplier + Cost from PO data. Load AFTER Items and Suppliers.",
    sql=LOTS_SQL,
    headers=[
        "Name",
        "ohfy__Item__c",
        "ohfy__Lot_Identifier__c",
        "ohfy__Expiration_Date__c",
        "ohfy__Receipt_Date__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Sellable__c",
        "ohfy__Supplier__r.ohfy__External_ID__c",
        "ohfy__Cost_Per_Unit__c",
    ],
    friendly_headers=[
        "Lot Name",
        "Item (lookup)",
        "Lot Identifier",
        "Expiration Date",
        "Receipt Date",
        "Active?",
        "Sellable?",
        "Supplier (lookup)",
        "Cost Per Unit",
    ],
    notes="Name = '{Item Name} - {MM/DD/YYYY}'. Supplier resolved via ITEMT.SUPPLIER_CODE → Suppliers.csv Customer_Number → External_ID. Cost from latest PO in PODTLT.",
    load_order=19,
)


# ===== 15b. Inventory =====
INVENTORY_CROSS_SQL = """
    SELECT
        TRIM(i."ITEM_CODE") AS item_code,
        TRIM(w."WAREHOUSE") AS warehouse_code,
        dz.zone_code AS default_zone
    FROM staging."ITEMT" i
    CROSS JOIN (
        SELECT DISTINCT TRIM("WAREHOUSE") AS "WAREHOUSE"
        FROM staging."HDRWHSET"
        WHERE COALESCE(TRIM("DELETE_FLAG"), '') <> 'Y'
          AND import_is_deleted = false
    ) w
    LEFT JOIN (
        SELECT TRIM("LCWHSE") AS wh, MIN(LEFT(TRIM("LCLOC"), 1)) AS zone_code
        FROM staging."LOCMAST"
        WHERE import_is_deleted = false
          AND TRIM("LCLOC") <> ''
          AND LEFT(TRIM("LCLOC"), 1) ~ '[A-Za-z0-9]'
        GROUP BY TRIM("LCWHSE")
    ) dz ON TRIM(w."WAREHOUSE") = dz.wh
    WHERE i.import_is_deleted = false
      AND TRIM(i."ITEM_STATUS") = 'A'
    ORDER BY i."ITEM_CODE", w."WAREHOUSE"
"""

register_tab(
    name="Inventory",
    description="Seed inventory: 1000 qty per active item per warehouse (10 warehouses). Requires Items and Child_Locations loaded.",
    sql=INVENTORY_CROSS_SQL,
    headers=[
        "ohfy__Item__c",
        "ohfy__Location__c",
        "ohfy__Quantity_On_Hand__c",
        "ohfy__Quantity_Available__c",
        "ohfy__Is_Active__c",
        "ohfy__Is_Default_Inventory__c",
        "ohfy__Reason__c",
    ],
    friendly_headers=[
        "Item (lookup)",
        "Location (lookup)",
        "Qty On Hand",
        "Qty Available",
        "Active?",
        "Default Inventory?",
        "Reason",
    ],
    notes="Item__c = lookup via item_code → Item External_ID__c. Location__c = default zone per warehouse (Key__c = '{wh}-{zone}'). Qty = 1000 seed data. Is_Default_Inventory = TRUE only for warehouse 1 (Mobile).",
    load_order=19.5,
)


# ===== 15c. Lot Inventory =====
register_tab(
    name="Lot_Inventory",
    description="Links each Inventory record to its Lot, per warehouse. MasterDetail to both — needs SF IDs at load time.",
    sql=INVENTORY_CROSS_SQL,
    headers=[
        "ohfy__Inventory__c",
        "ohfy__Lot__c",
        "ohfy__Quantity_On_Hand__c",
    ],
    friendly_headers=[
        "Inventory (master-detail)",
        "Lot (master-detail)",
        "Qty On Hand",
    ],
    notes="Both fields are MasterDetail — require actual SF record IDs. Reference keys in CSV: Inventory = 'INV-{item_code}-{wh}-{zone}', Lot = '{item_code}-{YYYYMMDD}'. Query SF IDs after loading Lots and Inventory, then substitute before loading Lot_Inventory.",
    load_order=19.7,
)


# ===== 16. Users =====
register_tab(
    name="Users",
    description="VIP Users from USERST. Reference tab - Users created manually or via Salesforce setup.",
    sql="""
        SELECT
            TRIM("FIRSTNAME")           AS first_name,
            TRIM("LASTNAME")            AS last_name,
            TRIM("EMAIL")               AS email,
            TRIM("JOBTITLE")            AS job_title,
            TRIM("EMPLOYEECODE")        AS employee_code,
            TRIM("EMPLOYEEID")          AS employee_id,
            TRIM("EMPLOYEETYPE")        AS employee_type,
            TRIM("DEFAULTWAREHOUSE")    AS default_warehouse,
            TRIM("DEFAULTCOMPANY")      AS default_company,
            TRIM("DEPARTMENTID")        AS department,
            "IDENTITY"                  AS vip_identity
        FROM staging."USERST"
        WHERE import_is_deleted = false
        ORDER BY last_name, first_name
    """,
    headers=[
        "FirstName",
        "LastName",
        "Email",
        "Title",
        "EmployeeNumber",
        "Department",
        "DefaultWarehouse",
    ],
    notes="Users are typically created manually in Salesforce. This tab is for reference during setup.",
    load_order=50,
)


# ===== 17. Contacts =====
register_tab(
    name="Contacts",
    description="Customer contacts extracted from BRATTT buyer field. Load AFTER Customers.",
    sql="""
        SELECT
            TRIM(b."CMACCT")   AS account_number,
            TRIM(b."CMDBA")    AS account_name,
            TRIM(b."CMBUYR")   AS buyer_name,
            b."CMPHON"         AS phone,
            b."CMFAX#"         AS fax,
            TRIM(b."CMSTS")    AS status,
            b."CMIDENTITY"     AS vip_identity
        FROM staging."BRATTT" b
        WHERE b.import_is_deleted = false
          AND TRIM(b."CMBUYR") <> ''
          AND TRIM(b."CMBUYR") IS NOT NULL
        ORDER BY buyer_name
    """,
    headers=[
        "FirstName",
        "LastName",
        "AccountId",
        "Phone",
        "Fax",
        "Title",
        "ohfy__Level__c",
        "ohfy__Is_Billing_Contact__c",
        "ohfy__Is_Delivery_Contact__c",
    ],
    friendly_headers=[
        "First Name",
        "Last Name",
        "Account (lookup)",
        "Phone",
        "Fax",
        "Title",
        "Level",
        "Billing Contact?",
        "Delivery Contact?",
    ],
    notes="AccountId = lookup via CMACCT → Account External_ID__c. Name split from CMBUYR field.",
    load_order=15,
)


# ===== 18. Account Routes =====
register_tab(
    name="Account_Routes",
    description="Account-to-Route junction from BRATTT. Load AFTER Customers and Routes.",
    sql="""
        SELECT
            TRIM(b."CMACCT")    AS account_number,
            TRIM(b."CMDBA")     AS account_name,
            TRIM(b."CMBRT")     AS route_code,
            CAST(b."CMCDAY" AS TEXT) AS delivery_day,
            CAST(b."CMDSEQ" AS TEXT) AS delivery_sequence,
            TRIM(b."CMSTS")     AS status,
            b."CMIDENTITY"      AS vip_identity
        FROM staging."BRATTT" b
        WHERE b.import_is_deleted = false
          AND TRIM(b."CMBRT") <> ''
          AND TRIM(b."CMBRT") IS NOT NULL
        ORDER BY route_code, delivery_sequence
    """,
    headers=[
        "ohfy__Customer__c",
        "ohfy__Route__c",
        "Delivery_Day__c",
        "ohfy__Stop_Order__c",
        "ohfy__Is_Active_Route__c",
        "ohfy__Key__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Account (lookup)",
        "Route (lookup)",
        "Delivery Day",
        "Stop/Sequence",
        "Active?",
        "Key",
        "External ID",
    ],
    notes="Account__c = lookup via CMACCT → External_ID__c. Route__c = lookup via CMBRT → Route Key__c.",
    load_order=16,
)


# ===== 19. Prospects (Inactive/Prospect Customers) =====
register_tab(
    name="Prospects",
    description="Inactive or deleted customer accounts that can be loaded as Prospects. Load AFTER Customers.",
    sql="""
        SELECT
            TRIM(b."CMACCT")        AS account_number,
            TRIM(b."CMDBA")         AS dba_name,
            TRIM(b."CMLNAM")        AS legal_name,
            TRIM(b."CMSTR")         AS street,
            TRIM(c."CITYNAME")      AS city,
            TRIM(c."STATE")         AS state_code,
            TRIM(b."POSTALCODE")    AS zip_code,
            b."CMPHON"              AS phone,
            b."CMFAX#"              AS fax,
            CAST(b."CMONOF" AS TEXT) AS on_off_premise,
            TRIM(b."CMCHN")         AS chain_code,
            TRIM(b."CMCLAS")        AS customer_class,
            TRIM(b."CMLIC#")        AS license_number,
            TRIM(b."CMTERM")        AS payment_term,
            TRIM(b."CMSTS")         AS status,
            b."CMIDENTITY"          AS vip_identity
        FROM staging."BRATTT" b
        LEFT JOIN staging."CITYT" c ON b."ID_CITY" = c."IDENTITY"
        WHERE b.import_is_deleted = false
          AND TRIM(b."CMSTS") IN ('I', 'D', 'X', 'CLR')
        ORDER BY dba_name
    """,
    headers=[
        "RecordTypeId",
        "Name",
        "ohfy__Legal_Name__c",
        "ohfy__Customer_Number__c",
        "Type",
        "ohfy__Prospect_Stage__c",
        "ohfy__Premise_Type__c",
        "BillingStreet",
        "BillingCity",
        "BillingState",
        "BillingPostalCode",
        "BillingCountry",
        "Phone",
        "Fax",
        "ohfy__Chain_Banner__c",
        "ohfy__Customer_Class__c",
        "ohfy__License_Number__c",
        "ohfy__Payment_Terms__c",
        "ohfy__Is_Active__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Record Type ID",
        "DBA Name",
        "Legal Name",
        "Account #",
        "Account Type",
        "Stage",
        "Premise Type",
        "Street",
        "City",
        "State",
        "Zip",
        "Country",
        "Phone",
        "Fax",
        "Chain/Banner",
        "Customer Class",
        "License #",
        "Payment Terms",
        "Active?",
        "External ID",
    ],
    notes="Type = 'Customer'. Stage = 'Prospect'. These are inactive VIP accounts that may be re-engaged.",
    load_order=17,
)


# ===== 20. Allocations (Customer) =====
register_tab(
    name="Allocations_Customer",
    description="Product allocations to customers from VIP ALLOCHT + ALLOCDT. Load AFTER Items and Customers.",
    sql="""
        SELECT
            CAST(h."AHAID#" AS TEXT)   AS alloc_id,
            TRIM(h."AHTYPE")           AS alloc_type,
            TRIM(h."AHDESC")           AS alloc_desc,
            TRIM(d."ADACAS")           AS customer_code,
            TRIM(d."ADITEM")           AS item_code,
            d."ADQTYA"                 AS alloc_qty,
            d."ADQTYU"                 AS ship_qty,
            h."AHSDAT"                 AS start_date,
            h."AHEDAT"                 AS end_date,
            d."ADIDENTITY"             AS vip_identity
        FROM staging."ALLOCHT" h
        JOIN staging."ALLOCDT" d ON h."AHAID#" = d."ADAID#"
        WHERE h.import_is_deleted = false
          AND d.import_is_deleted = false
        ORDER BY alloc_desc, customer_code, item_code
    """,
    headers=[
        "Name",
        "ohfy__Customer__c",
        "ohfy__Item__c",
        "ohfy__Allocated_Case_Amount__c",
        "ohfy__Allocated_Cases_Sold__c",
        "ohfy__Start_Date__c",
        "ohfy__End_Date__c",
        "ohfy__Is_Active__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Allocation Name",
        "Customer (lookup)",
        "Item (lookup)",
        "Allocated Qty",
        "Shipped Qty",
        "Start Date",
        "End Date",
        "Active?",
        "External ID",
    ],
    notes="Account__c = lookup via customer code → External_ID__c. Item__c = lookup via item code → External_ID__c.",
    load_order=20,
)


# ===== 21. Promotions (Special Pricing / Discounts) =====
register_tab(
    name="Promotions",
    description="Special pricing records from VIP DISCOUTT. Load AFTER Items and Pricelists.",
    sql="""
        SELECT
            TRIM("PRODID")         AS item_code,
            TRIM("CODEID")         AS price_code,
            TRIM("DISCCODE")       AS discount_code,
            TRIM("TYPEID")         AS discount_type,
            "STARTDATE"            AS start_date,
            "ENDDATE"              AS end_date,
            TRIM("DISCGRP2")       AS disc_group2,
            TRIM("DISCGRP3")       AS disc_group3,
            "IDENTITY"             AS vip_identity
        FROM staging."DISCOUTT"
        WHERE import_is_deleted = false
        ORDER BY discount_code, item_code
    """,
    headers=[
        "ohfy__Item__c",
        "ohfy__Pricelist__c",
        "Discount_Code__c",
        "ohfy__Type__c",
        "ohfy__Start_Date__c",
        "ohfy__End_Date__c",
        "ohfy__Is_Active__c",
        "ohfy__Key__c",
        "ohfy__External_ID__c",
    ],
    friendly_headers=[
        "Item (lookup)",
        "Pricelist (lookup)",
        "Discount Code",
        "Type",
        "Start Date",
        "End Date",
        "Active?",
        "Key",
        "External ID",
    ],
    notes="Item-level discount details from DISCOUTT. Item__c = lookup via PRODID. Pricelist__c = lookup via DISCCODE.",
    load_order=21,
)


# ===== 22. Overhead =====
register_tab(
    name="Overhead",
    description="Overhead/cost items from VIP cost tables. Load independently.",
    sql="""
        SELECT DISTINCT
            TRIM("DPDEPTYP")   AS overhead_name,
            AVG("DPDEPO")      AS default_price
        FROM staging."DEPOSITST"
        WHERE import_is_deleted = false
          AND "DPDEPO" IS NOT NULL
          AND "DPDEPO" <> 0
        GROUP BY TRIM("DPDEPTYP")
        ORDER BY overhead_name
    """,
    headers=[
        "Name",
        "ohfy__Default_Case_Price__c",
        "ohfy__Last_Landed_Case_Cost__c",
        "ohfy__Is_Active__c",
        "ohfy__Key__c",
    ],
    friendly_headers=[
        "Overhead Name",
        "Default Price",
        "Last Purchase Price",
        "Active?",
        "Key",
    ],
    notes="Derived from VIP DEPOSITST aggregate. Default prices averaged per deposit type.",
    load_order=14,
)


# ===== 23. Data Validation - Sales =====
register_tab(
    name="Data_Validation_Sales",
    description="Picklist values for sales-related objects. Reference for data validation setup.",
    sql="""
        SELECT 'Premise_Type__c' AS field_name, 'On Premise' AS picklist_value, 'Account' AS object_name
        UNION ALL SELECT 'Premise_Type__c', 'Off Premise', 'Account'
        UNION ALL SELECT 'Type', 'Customer', 'Account'
        UNION ALL SELECT 'Type', 'Supplier', 'Account'
        UNION ALL SELECT 'Type', 'Prospect', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'COD', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Net 15', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Net 30', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Prepaid', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Net 45', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Net 10', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'Net 60', 'Account'
        UNION ALL SELECT 'Payment_Terms__c', 'EOM', 'Account'
        UNION ALL SELECT 'Delivery_Method__c', 'Delivery', 'Account'
        UNION ALL SELECT 'Delivery_Method__c', 'Will Call', 'Account'
        UNION ALL SELECT 'Delivery_Method__c', 'Distributor', 'Account'
        UNION ALL SELECT 'Package_Type__c', 'Kegged', 'Item__c'
        UNION ALL SELECT 'Package_Type__c', 'Packaged', 'Item__c'
        UNION ALL SELECT 'UOM__c', 'US Count', 'Item__c'
        UNION ALL SELECT 'UOM__c', 'US Volume', 'Item__c'
        UNION ALL SELECT 'Type__c', 'Discount', 'Pricelist__c'
        UNION ALL SELECT 'Type__c', 'Individual Price', 'Pricelist__c'
        UNION ALL SELECT 'Discount_Type__c', 'Dollars', 'Pricelist__c'
        UNION ALL SELECT 'Discount_Type__c', 'Percent', 'Pricelist__c'
        ORDER BY object_name, field_name, picklist_value
    """,
    headers=["Object", "Field API Name", "Picklist Value"],
    notes="Reference tab. Use these values to configure picklist fields in Ohanafy/Salesforce setup.",
    load_order=90,
)


# ===== 24. Data Validation - Inventory =====
register_tab(
    name="Data_Validation_Inventory",
    description="Picklist values for inventory-related objects. Reference for data validation setup.",
    sql="""
        SELECT 'Type__c' AS field_name, 'Warehouse' AS picklist_value, 'Location__c' AS object_name
        UNION ALL SELECT 'Type__c', 'Zone', 'Location__c'
        UNION ALL SELECT 'Type__c', 'Aisle', 'Location__c'
        UNION ALL SELECT 'Type__c', 'Rack', 'Location__c'
        UNION ALL SELECT 'Type__c', 'Shelf', 'Location__c'
        UNION ALL SELECT 'Type__c', 'Bin', 'Location__c'
        UNION ALL SELECT 'Type__c', 'Truck', 'Equipment__c'
        UNION ALL SELECT 'Type__c', 'Trailer', 'Equipment__c'
        UNION ALL SELECT 'Type__c', 'Van', 'Equipment__c'
        UNION ALL SELECT 'Type__c', 'Delivery', 'Route__c'
        UNION ALL SELECT 'Type__c', 'Sales', 'Route__c'
        UNION ALL SELECT 'Type__c', 'Keg Deposit', 'Fee__c'
        UNION ALL SELECT 'Type__c', 'Return', 'Fee__c'
        UNION ALL SELECT 'Type__c', 'CRV', 'Fee__c'
        UNION ALL SELECT 'Type__c', 'Misc. Charge', 'Fee__c'
        UNION ALL SELECT 'Type__c', 'Beer', 'Item_Line__c'
        UNION ALL SELECT 'Type__c', 'Wine', 'Item_Line__c'
        UNION ALL SELECT 'Type__c', 'Spirits', 'Item_Line__c'
        UNION ALL SELECT 'Type__c', 'Non-Alcoholic', 'Item_Line__c'
        UNION ALL SELECT 'Subtype__c', 'Beer', 'Item_Type__c'
        UNION ALL SELECT 'Subtype__c', 'Wine', 'Item_Type__c'
        UNION ALL SELECT 'Subtype__c', 'Spirits', 'Item_Type__c'
        UNION ALL SELECT 'Subtype__c', 'Non-Alcoholic', 'Item_Type__c'
        ORDER BY object_name, field_name, picklist_value
    """,
    headers=["Object", "Field API Name", "Picklist Value"],
    notes="Reference tab. Use these values to configure picklist fields in Ohanafy/Salesforce setup.",
    load_order=91,
)


# ===== 25. Record Types =====
register_tab(
    name="Record_Types",
    description="Record type definitions needed for Ohanafy objects. Reference for Salesforce setup.",
    sql="""
        SELECT 'Account' AS object_name, 'On Premise' AS record_type_name, 'On-premise customers (bars, restaurants)' AS description
        UNION ALL SELECT 'Account', 'Off Premise', 'Off-premise customers (retail, grocery, liquor stores)'
        UNION ALL SELECT 'Account', 'Supplier', 'Supplier/vendor accounts'
        UNION ALL SELECT 'ohfy__Item__c', 'Finished Good', 'Standard sellable products'
        UNION ALL SELECT 'ohfy__Item__c', 'Non-Inventory', 'Non-inventory items (fees, deposits)'
        UNION ALL SELECT 'ohfy__Location__c', 'Warehouse', 'Top-level warehouse locations'
        UNION ALL SELECT 'ohfy__Location__c', 'Area', 'Areas within warehouses'
        UNION ALL SELECT 'ohfy__Location__c', 'Bin', 'Individual bin/slot locations'
        UNION ALL SELECT 'ohfy__Route__c', 'Delivery', 'Delivery routes'
        UNION ALL SELECT 'ohfy__Route__c', 'Sales', 'Sales-only routes'
        ORDER BY object_name, record_type_name
    """,
    headers=["Object API Name", "Record Type Name", "Description"],
    notes="Reference tab. Create these Record Types in Salesforce Setup before data loading.",
    load_order=92,
)


# ===== 26. Progress Tracker =====
# This is a static reference tab, no SQL needed
register_tab(
    name="Progress_Tracker",
    description="Track migration progress by object. Update manually during migration.",
    sql="""
        SELECT 'Suppliers' AS tab_name, 'Account (Supplier)' AS ohanafy_object, '01' AS load_order
        UNION ALL SELECT 'Item_Lines', 'ohfy__Item_Line__c', '02'
        UNION ALL SELECT 'Item_Types', 'ohfy__Item_Type__c', '03'
        UNION ALL SELECT 'Territories', 'ohfy__Territory__c', '04'
        UNION ALL SELECT 'Equipment_Vehicles', 'ohfy__Equipment__c', '05'
        UNION ALL SELECT 'Parent_Locations', 'ohfy__Location__c', '06'
        UNION ALL SELECT 'Child_Locations', 'ohfy__Location__c', '07'
        UNION ALL SELECT 'Pick_Paths', 'ohfy__Location__c', '08'
        UNION ALL SELECT 'Routes', 'ohfy__Route__c', '09'
        UNION ALL SELECT 'Customers', 'Account (Customer)', '10'
        UNION ALL SELECT 'Items', 'ohfy__Item__c', '11'
        UNION ALL SELECT 'Keg_Shell_Items', 'ohfy__Item__c (Keg Shell)', '12'
        UNION ALL SELECT 'Item_Components', 'ohfy__Item_Component__c', '13'
        UNION ALL SELECT 'Fees', 'ohfy__Fee__c', '14'
        UNION ALL SELECT 'Pricelists', 'ohfy__Pricelist__c', '15'
        UNION ALL SELECT 'Overhead', 'ohfy__Overhead__c', '14'
        UNION ALL SELECT 'Contacts', 'Contact', '15'
        UNION ALL SELECT 'Account_Routes', 'ohfy__Account_Route__c', '16'
        UNION ALL SELECT 'Prospects', 'Account (Prospect)', '17'
        UNION ALL SELECT 'Pricelist_Items', 'ohfy__Pricelist_Item__c', '18'
        UNION ALL SELECT 'Inventory', 'ohfy__Inventory__c', '19'
        UNION ALL SELECT 'Allocations_Customer', 'ohfy__Allocation__c', '20'
        UNION ALL SELECT 'Promotions', 'ohfy__Promotion__c', '21'
        UNION ALL SELECT 'Users', 'User (Reference)', '22'
        ORDER BY 3
    """,
    headers=["Tab Name", "Ohanafy Object", "Load Order", "Status", "Loaded By", "Date Loaded", "Row Count", "Notes"],
    notes="Track your migration progress. Update Status/Loaded By/Date columns as you load each object.",
    load_order=93,
)


# ===== 27. User Warehouse Permissions (Pivot) =====
# This tab is built dynamically — SQL fetches users and warehouse assignments,
# then the transform function pivots into a boolean grid.
register_tab(
    name="User_Warehouse_Permissions",
    description="User-to-warehouse permission matrix. Shows which users have access to which warehouses.",
    sql="""
        SELECT
            TRIM(u."EMPLOYEEID") AS emp_id,
            TRIM(u."FIRSTNAME") AS first_name,
            TRIM(u."LASTNAME") AS last_name,
            TRIM(u."JOBTITLE") AS title,
            TRIM(u."EMAIL") AS email,
            TRIM(u."DEFAULTWAREHOUSE") AS default_warehouse,
            u."IDENTITY" AS user_identity,
            TRIM(uw."WAREHOUSE") AS assigned_warehouse,
            TRIM(uw."PERMISSION") AS permission
        FROM staging."USERST" u
        LEFT JOIN staging."USERWHSET" uw
            ON u."IDENTITY" = uw."ID_USERS" AND uw.import_is_deleted = false
        WHERE u.import_is_deleted = false
        ORDER BY u."LASTNAME", u."FIRSTNAME", uw."WAREHOUSE"
    """,
    headers=[],  # Built dynamically in transform
    notes="Pivot table: rows = users, columns = warehouses. TRUE = user has access. Built from USERST + USERWHSET.",
    load_order=94,
)


# ---------------------------------------------------------------------------
# Loading Guide content
# ---------------------------------------------------------------------------
LOADING_GUIDE = [
    ["VIP to Ohanafy Migration - Loading Guide"],
    ["Generated: {date}"],
    [""],
    ["LOAD ORDER", "TAB NAME", "OHANAFY OBJECT", "DEPENDS ON", "DESCRIPTION", "NOTES"],
    [
        "1",
        "Suppliers",
        "Account",
        "None",
        "Supplier accounts (e.g., Molson Coors)",
        "Type = 'Supplier'. Load FIRST - Item_Lines need Supplier__c lookup.",
    ],
    [
        "2",
        "Item_Lines",
        "ohfy__Item_Line__c",
        "Suppliers",
        "Brand families (e.g., Coors)",
        "Top of product hierarchy. Type__c derived from dominant PRODUCT_CLASS of items.",
    ],
    [
        "3",
        "Item_Types",
        "ohfy__Item_Type__c",
        "Item_Lines",
        "Brands (e.g., Coors Light)",
        "Item_Line__c = lookup to Item_Line via Key__c. Type/Subtype from PRODUCT_CLASS.",
    ],
    [
        "4",
        "Territories",
        "ohfy__Territory__c",
        "None",
        "Sales territories",
        "Load early - Customers and Routes reference Territory.",
    ],
    [
        "5",
        "Equipment_Vehicles",
        "ohfy__Equipment__c",
        "None",
        "Trucks and vehicles",
        "Fulfillment_Location__c = warehouse lookup (set after Locations loaded).",
    ],
    [
        "6",
        "Parent_Locations",
        "ohfy__Location__c",
        "None",
        "Top-level warehouses",
        "Parent locations with no Parent_Location__c.",
    ],
    [
        "7",
        "Child_Locations",
        "ohfy__Location__c",
        "Parent_Locations",
        "Zones within warehouses (derived from 1st char of location code)",
        "Parent_Location__c = lookup to warehouse Key__c. Type = Zone.",
    ],
    [
        "8",
        "Pick_Paths",
        "ohfy__Location__c",
        "Child_Locations",
        "Bin-level locations within zones",
        "Parent_Location__c = lookup to zone Key__c (WH-ZONE). Includes dirty keg detection.",
    ],
    [
        "9",
        "Routes",
        "ohfy__Route__c",
        "Equipment_Vehicles, Territories",
        "Delivery and sales routes",
        "Vehicle__c and Driver__c are lookups.",
    ],
    [
        "10",
        "Chain_Banners",
        "Account",
        "None",
        "Chain/banner groupings (438 from HDRCHAINT)",
        "Type = 'Chain Banner'. Parent accounts for customer rollups. Load BEFORE Customers.",
    ],
    [
        "11",
        "Customers",
        "Account",
        "Territories, Routes, Chain_Banners",
        "Customer accounts (28K+ from BRATTT)",
        "Type = 'Customer'. Chain_Banner__c = lookup to Chain Banner via Customer_Number__c.",
    ],
    [
        "12",
        "Items",
        "ohfy__Item__c",
        "Item_Types, Item_Lines",
        "Products (e.g., Coors Banquet 1/2 BBL)",
        "Item_Type__c and Item_Line__c are lookups by Key__c.",
    ],
    [
        "13",
        "Keg_Shell_Items",
        "ohfy__Item__c",
        "Items, Item_Lines",
        "Empty keg shells (1 per supplier per keg size)",
        "Dunnage items for keg deposit tracking. Key = KEG-SHELL-{SUPPLIER}-{CONTAINER}.",
    ],
    [
        "14",
        "Item_Components",
        "ohfy__Item_Component__c",
        "Items, Keg_Shell_Items",
        "Links keg products to empty keg shells",
        "Parent_Item__c = master-detail (needs SF IDs). Qty = 1. Resolve IDs at load time.",
    ],
    ["15", "Fees", "ohfy__Fee__c", "None", "Deposit and fee structures", "Can be loaded independently."],
    [
        "14",
        "Pricelists",
        "ohfy__Pricelist__c",
        "None",
        "Price lists / discount worksheets",
        "Can be loaded independently.",
    ],
    [
        "15",
        "Overhead",
        "ohfy__Overhead__c",
        "None",
        "Overhead cost items",
        "Can be loaded independently. Derived from VIP deposit types.",
    ],
    [
        "16",
        "Contacts",
        "Contact",
        "Customers",
        "Customer contacts (buyers)",
        "AccountId = lookup via Account External_ID__c. Extracted from BRATTT CMBUYR.",
    ],
    [
        "17",
        "Account_Routes",
        "ohfy__Account_Route__c",
        "Customers, Routes",
        "Account-to-Route junction",
        "Account__c and Route__c are lookups. Includes delivery day and stop sequence.",
    ],
    [
        "18",
        "Prospects",
        "Account",
        "Customers",
        "Inactive/deleted VIP customers as Prospects",
        "Stage = 'Prospect'. Same structure as Customers but for re-engagement.",
    ],
    [
        "19",
        "Pricelist_Items",
        "ohfy__Pricelist_Item__c",
        "Pricelists, Items",
        "Item-level pricing",
        "MasterDetail to both Pricelist__c and Item__c.",
    ],
    [
        "20",
        "Lots",
        "ohfy__Lot__c",
        "Items, Suppliers",
        "One lot per active item (expiry 2026-12-31). Includes Supplier + Cost.",
        "Supplier via ITEMT.SUPPLIER_CODE → Account External_ID. Cost from latest PO.",
    ],
    [
        "21",
        "Inventory",
        "ohfy__Inventory__c",
        "Items, Child_Locations",
        "Seed inventory: 1000 qty per active item per warehouse (10 warehouses)",
        "Item__c = lookup via External_ID__c. Location__c = default zone per warehouse.",
    ],
    [
        "22",
        "Lot_Inventory",
        "ohfy__Lot_Inventory__c",
        "Lots, Inventory",
        "Links Inventory to Lot records per warehouse, qty 1000",
        "MasterDetail to both — needs SF IDs. Query Lot/Inventory IDs after loading, then substitute.",
    ],
    [
        "23",
        "Allocations_Customer",
        "ohfy__Allocation__c",
        "Items, Customers",
        "Product allocations to customers",
        "Account__c and Item__c are lookups. From VIP ALLOCHT/ALLOCDT.",
    ],
    [
        "24",
        "Promotions",
        "ohfy__Promotion__c",
        "Items, Pricelists, Customers",
        "Customer-specific discount records",
        "From VIP DISCOUTT. Account, Item, Pricelist are lookups.",
    ],
    [
        "25",
        "Users",
        "User (standard)",
        "None",
        "System users (reference only)",
        "Create users manually in Salesforce Setup. This tab is for reference.",
    ],
    [
        "26",
        "Data_Validation_Sales",
        "N/A (Reference)",
        "None",
        "Picklist values for sales objects",
        "Use to configure picklist fields in Salesforce Setup.",
    ],
    [
        "27",
        "Data_Validation_Inventory",
        "N/A (Reference)",
        "None",
        "Picklist values for inventory objects",
        "Use to configure picklist fields in Salesforce Setup.",
    ],
    [
        "28",
        "Record_Types",
        "N/A (Reference)",
        "None",
        "Record Type definitions",
        "Create these Record Types in Salesforce Setup before loading.",
    ],
    [
        "29",
        "Progress_Tracker",
        "N/A (Tracking)",
        "None",
        "Migration progress tracking",
        "Update manually as you load each object.",
    ],
    [
        "30",
        "User_Warehouse_Permissions",
        "N/A (Reference)",
        "None",
        "User-to-warehouse permission pivot table",
        "Rows = users, columns = warehouses. TRUE/FALSE access grid.",
    ],
    [""],
    ["KEY CONCEPTS"],
    ["Concept", "Details"],
    [
        "vipid__c",
        "Custom external ID field on every Ohanafy object. Stores the VIP IDENTITY or code for cross-referencing during updates.",
    ],
    [
        "Key__c",
        "Ohanafy's built-in unique key field. Used for upsert operations and relationship lookups between objects.",
    ],
    ["External_ID__c", "Alternative external ID on Account and Item. Use for upsert to avoid duplicates."],
    [
        "Lookups",
        "When a field references another object (e.g., Item_Type__c on Item), use the Key__c or External_ID__c of the parent record.",
    ],
    ["CSV Loading", "Use Salesforce Data Loader or Import Wizard. Set 'External ID' matching for lookup fields."],
    [""],
    ["RECOMMENDED LOAD SEQUENCE"],
    ["Step", "Action"],
    [
        "1",
        "Load Suppliers, Territories, Parent_Locations, Equipment_Vehicles, Fees, Pricelists, Overhead (no dependencies - can be parallel)",
    ],
    ["2", "Load Item_Lines (needs Suppliers), Child_Locations (needs Parent_Locations)"],
    [
        "3",
        "Load Item_Types (needs Item_Lines), Pick_Paths (needs Child_Locations), Routes (needs Equipment, Territories)",
    ],
    ["4", "Load Customers (needs Territories, Routes), Items (needs Item_Types, Item_Lines)"],
    ["5", "Load Contacts, Account_Routes, Prospects (need Customers)"],
    [
        "6",
        "Load Pricelist_Items, Lots, Inventory, Allocations, Promotions (need Items, Customers, Pricelists, Locations)",
    ],
    ["7", "Load Lot_Inventory (needs Lots and Inventory SF IDs — query IDs first, substitute into CSV, then load)"],
    ["8", "Configure Data Validation picklists, Record Types, and verify all lookups resolved correctly"],
    [""],
    ["DATA TRANSFORMATIONS APPLIED"],
    ["Transformation", "Details"],
    [
        "Date conversion",
        "VIP stores dates as numeric YYYYMMDD (e.g., 20240115). Converted to YYYY-MM-DD for Salesforce.",
    ],
    ["Phone formatting", "VIP stores phones as numeric. Formatted as (XXX) XXX-XXXX."],
    ["Status mapping", "VIP status codes mapped: A/blank → Active, I/D/X → Inactive."],
    ["Package type mapping", "VIP CONTAINER_TYPE_CODE mapped to Ohanafy Package_Type__c picklist values."],
    ["UPC formatting", "Numeric UPCs left-padded to standard lengths (12 for UPC, 14 for GTIN)."],
    ["Trim whitespace", "All VIP char fields are right-padded with spaces. Trimmed during extraction."],
]


# ---------------------------------------------------------------------------
# Data transformation helpers
# ---------------------------------------------------------------------------
def vip_date_to_sf(numeric_date):
    """Convert VIP numeric date (YYYYMMDD) to Salesforce date (YYYY-MM-DD)."""
    if not numeric_date or numeric_date == 0:
        return ""
    try:
        d = str(int(numeric_date))
        if len(d) == 8:
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    except (ValueError, TypeError):
        pass
    return ""


def format_phone(phone_num):
    """Format numeric phone to (XXX) XXX-XXXX."""
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


def format_upc(upc_val, length=12):
    """Format UPC/GTIN with leading zeros."""
    if not upc_val or upc_val == 0:
        return ""
    try:
        return str(int(upc_val)).zfill(length)
    except (ValueError, TypeError):
        return str(upc_val) if upc_val else ""


def is_active(status_val):
    """Convert VIP status to boolean."""
    if not status_val:
        return "TRUE"
    s = str(status_val).strip().upper()
    return "FALSE" if s in ("I", "D", "X", "CLR", "N") else "TRUE"


def map_package_type(container_code, uom_code=""):
    """Map VIP container type to Ohanafy Package_Type__c.

    VIP uses numeric CONTAINER_TYPE_CODE values:
      700-series = kegs/barrels (710=1/6 BBL, 720=1/4 BBL, 730=1/2 BBL,
                                 700=13.2/50L KEG, 705=30L, 706=10.8 GAL,
                                 707=5.4 GAL, 715=25L BBL, 590=20L KEG)
    UOM codes HK (half keg) and QK (quarter keg) also indicate kegged product.
    """
    if not container_code:
        return "Packaged"
    c = str(container_code).strip().upper()
    u = str(uom_code).strip().upper() if uom_code else ""
    # Numeric keg container codes
    keg_numeric = {"700", "705", "706", "707", "710", "715", "720", "730", "590"}
    if c in keg_numeric:
        return "Kegged"
    # Text-based fallback (legacy)
    if c in {"KEG", "KG", "K", "BBL", "HBL", "QBL", "SBL"} or "KEG" in c or "BBL" in c:
        return "Kegged"
    # UOM-based fallback
    if u in {"HK", "QK"}:
        return "Kegged"
    return "Packaged"


def map_product_type(product_class):
    """Map VIP numeric PRODUCT_CLASS to Ohanafy Type__c / Subtype__c picklist.

    Gulf Distributing class codes (from HDRCLASST — empty table, derived from data):
      01 = Beer, 02 = NA Beer, 03 = Energy, 04 = NA Beverage,
      05 = Wine, 06 = Spirits/RTD, 07 = Cider, 08 = Spirits,
      09 = Returns, 10-12 = Non-bev, 14 = Hemp/THC, 20 = Equipment, 40 = Empties
    """
    if not product_class:
        return "Beer"
    c = str(product_class).strip()
    wine = {"05"}
    spirits = {"06", "08"}
    na = {"03", "04", "10", "11", "12", "20"}
    if c in wine:
        return "Wine"
    if c in spirits:
        return "Spirits"
    if c in na:
        return "Non-Alcoholic"
    return "Beer"  # 01, 02, 07, 09, 14, 40 and unknown


def map_item_record_type(product_class, package_type):
    """Map VIP PRODUCT_CLASS to Ohanafy Item__c Type__c picklist and Record Type.

    Org picklist: Finished Good, Work In Progress, Packaging, Raw Material,
                  Keg Shell, Merchandise, Tap Handle, Overhead, Template, Dunnage
    Record types: Finished_Good, Keg_Shell, Merchandise, Overhead, Packaging,
                  Raw_Material, Tap_Handle
    """
    c = str(product_class).strip() if product_class else ""
    # Equipment / merch
    if c == "20":
        return "Merchandise"
    # Empties / returns → Overhead (deposit shells, pallets, etc.)
    if c in ("09", "40"):
        return "Overhead"
    # Everything else is a finished good
    return "Finished Good"


def map_packaging_type_picklist(package_size, container_code, is_kegged):
    """Map VIP PACKAGE_SIZE to Ohanafy Packaging_Type__c picklist.

    Org picklist includes: 1/2 Barrel(s), 1/4 Barrel(s), 1/6 Barrel(s),
    50 Liter(s), 40 Liter(s), 20 Liter(s), Case Equivalent(s), Each, etc.

    Only map to barrel types when the item is actually kegged (by container code / UOM).
    Prevents false positives like "1/24/187ML" matching "1/2".
    """
    ps = str(package_size).strip().upper() if package_size else ""
    ct = str(container_code).strip() if container_code else ""
    keg_containers = {"700", "705", "706", "707", "710", "715", "720", "730", "590"}

    if is_kegged or ct in keg_containers:
        # Map by container code first (most reliable), then by package size text
        if ct == "710" or "1/6" in ps:
            return "1/6 Barrel(s)"
        if ct == "720" or "1/4" in ps:
            return "1/4 Barrel(s)"
        if ct == "730" or "1/2" in ps:
            return "1/2 Barrel(s)"
        if "50 LTR" in ps or "50L" in ps:
            return "50 Liter(s)"
        if "30 LTR" in ps:
            return "Barrel(s)"
        if ct == "590" or "20 LTR" in ps:
            return "20 Liter(s)"
        if ct == "700" or "13.2" in ps:
            return "Barrel(s)"
        if ct == "706" or "10.8 GAL" in ps:
            return "Barrel(s)"
        if ct == "707" or "5.4 GAL" in ps:
            return "Barrel(s)"
        if ct == "715" or "25 LTR" in ps:
            return "Barrel(s)"
        # Kegged but unknown size
        return "Barrel(s)"

    # Non-keg: return as-is (raw VIP package size string)
    return safe_str(package_size)


def map_uom(product_class):
    """Map VIP product class to Ohanafy UOM."""
    if not product_class:
        return "US Count"
    c = str(product_class).strip().upper()
    if c in ("05", "06", "08", "WI", "SP", "LQ"):
        return "US Volume"
    return "US Count"


def map_delivery_method(method_code):
    """Map VIP CMETHO to Ohanafy Delivery_Method__c picklist."""
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
    """Map VIP HDRMKTT description to Ohanafy Market__c picklist."""
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
        "MILITARY OFF": "Military",
        "MILITARY ON": "Military",
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
    """Derive Ohanafy Retail_Type__c from market description.

    CMCHN is a universal grouping code (28,740/28,741 customers have one),
    so it cannot be used to distinguish Chain vs Independent.  Instead we
    rely on the HDRMKTT market description which already encodes this.
    """
    if market_desc:
        d = safe_str(market_desc).upper().strip()
        # Explicit chain market types
        if d.startswith("CHAIN") or d.startswith("CHN"):
            return "Chain"
        if d in ("WHOLESALE CLUB", "SUPERCNTR/MASS", "DOLLAR STORE"):
            return "Chain"
        # Explicit independent market types
        if d.startswith("IND ") or d == "SMALL GROCERY":
            return "Independent"
        # Distributor / house accounts
        if d in ("SUB-DISTRIBUTOR", "SUPPLIERS", "TRANSFERS"):
            return "Distributor"
    # No market desc or unrecognized — default to Independent
    return "Independent"


def safe_str(val):
    """Convert value to string, handling None."""
    if val is None:
        return ""
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    return str(val).strip()


# ---------------------------------------------------------------------------
# Row transformation functions (one per tab)
# ---------------------------------------------------------------------------


def transform_item_lines(rows):
    """Transform VIP supplier rows → Item_Line__c rows."""
    result = []
    for r in rows:
        result.append(
            [
                safe_str(r["supplier_name"]),  # Name
                safe_str(
                    r.get("supplier_identity", "")
                ),  # ohfy__Supplier__r.ohfy__External_ID__c (SUPPLIERT.IDENTITY → Account.External_ID__c)
                safe_str(r["supplier_code"]),  # ohfy__Key__c
                map_product_type(r.get("dominant_product_class")),  # ohfy__Type__c
                safe_str(r.get("supplier_identity", r["supplier_code"])),  # ohfy__External_ID__c
            ]
        )
    return result


# Map VIP container type codes → Ohanafy Packaging_Styles__c picklist values
CONTAINER_TO_PACKAGING_STYLE = {
    "710": "1/6 Barrel(s)",
    "720": "1/4 Barrel(s)",
    "730": "1/2 Barrel(s)",
    "700": "50 Liter(s)",
    "705": "50 Liter(s)",
    "706": "50 Liter(s)",
    "707": "50 Liter(s)",
    "715": "50 Liter(s)",
    "590": "20 Liter(s)",
}


def map_container_to_packaging_styles(container_types_csv):
    """Map comma-separated VIP container type codes → semicolon-separated Packaging_Styles multipicklist.

    Non-keg container codes (410, 420, etc.) map to 'Case Equivalent(s)'.
    Returns empty string if no codes provided.
    """
    if not container_types_csv:
        return ""
    codes = [c.strip() for c in container_types_csv.split(",") if c.strip()]
    styles = set()
    for code in codes:
        if code in CONTAINER_TO_PACKAGING_STYLE:
            styles.add(CONTAINER_TO_PACKAGING_STYLE[code])
        else:
            styles.add("Case Equivalent(s)")
    # Sort for deterministic output
    return ";".join(sorted(styles))


def transform_item_types(rows):
    """Transform VIP brand rows → Item_Type__c rows."""
    result = []
    for r in rows:
        brand_name = safe_str(r["brand_name"])
        brand_code = safe_str(r["brand_code"])
        supplier_code = safe_str(r["supplier_code"])
        ptype = map_product_type(r.get("dominant_product_class"))
        rt_id = get_record_type_id("ohfy__Item_Type__c", ptype) if ptype else ""

        # ABV: avg alcohol percent across items in this brand (null if no data)
        abv = r.get("avg_abv")
        abv_str = str(abv) if abv is not None and abv > 0 else ""

        # Packaging styles: map container type codes to picklist values
        pkg_styles = map_container_to_packaging_styles(safe_str(r.get("container_types", "")))

        result.append(
            [
                rt_id,  # RecordTypeId
                brand_name,  # Name
                brand_code,  # ohfy__Key__c
                supplier_code,  # ohfy__Item_Line__c (lookup key)
                ptype,  # ohfy__Subtype__c
                ptype,  # ohfy__Type__c
                brand_code,  # ohfy__Short_Name__c
                safe_str(r.get("pb_desc", "")),  # ohfy__Supplier_Number__c
                abv_str,  # ohfy__ABV__c
                pkg_styles,  # ohfy__Packaging_Styles__c
                safe_str(r["vip_identity"]),  # ohfy__External_ID__c
            ]
        )
    return result


def map_supplier_payment_terms(due_code, due_days):
    """Map VIP VRDUEC/VRDUED to Ohanafy Payment_Terms__c picklist."""
    days = int(due_days) if due_days else 0
    if days == 0:
        return "Due on Receipt"
    # Map to closest Ohanafy picklist value
    terms_map = {
        1: "Due on Receipt",
        5: "10 Days",
        7: "10 Days",
        10: "10 Days",
        14: "15 Days",
        15: "15 Days",
        20: "20 Days",
        21: "20 Days",
        25: "30 Days",
        30: "30 Days",
        45: "60 Days",
        60: "60 Days",
        90: "90 Days",
    }
    # Find closest match
    closest = min(terms_map.keys(), key=lambda k: abs(k - days))
    return terms_map[closest]


def transform_suppliers(rows):
    """Transform VIP supplier+vendor rows → Account (Supplier/Vendor) rows."""
    result = []
    for r in rows:
        sup_name = safe_str(r["supplier_name"])
        vendor_name = safe_str(r["vendor_name"])
        name = sup_name or vendor_name
        vendor_type = safe_str(r.get("vendor_type", "Supplier"))

        street = safe_str(r["address1"])
        if r.get("address2") and safe_str(r["address2"]):
            street += "\n" + safe_str(r["address2"])
        city = safe_str(r.get("city", ""))
        state = safe_str(r.get("state_code", ""))
        zip_code = safe_str(r["postal_code"])
        country = "US" if (city or state or zip_code) else ""

        # Legal name = vendor name if different from supplier name
        legal = vendor_name if vendor_name and vendor_name != sup_name else ""

        # Build description from vendor desc
        desc_parts = []
        if safe_str(r.get("vendor_desc")):
            desc_parts.append(safe_str(r["vendor_desc"]))
        description = "; ".join(desc_parts)

        # Payment terms from APVENT
        payment_terms = ""
        if r.get("due_days") is not None:
            payment_terms = map_supplier_payment_terms(r.get("due_code"), r.get("due_days"))

        # Map vendor_type to RecordTypeId
        rt_name = "Supplier" if vendor_type == "Supplier" else "Vendor/Service"
        rt_id = get_record_type_id("Account", rt_name)

        result.append(
            [
                rt_id,  # RecordTypeId
                name,  # Name
                legal,  # Legal_Name__c
                safe_str(r["supplier_code"]),  # Customer_Number__c
                vendor_type,  # Type (Supplier or Vendor)
                street,  # BillingStreet
                city,  # BillingCity
                state,  # BillingState
                zip_code,  # BillingPostalCode
                country,  # BillingCountry
                street,  # ShippingStreet (copy)
                city,  # ShippingCity
                state,  # ShippingState
                zip_code,  # ShippingPostalCode
                country,  # ShippingCountry
                format_phone(r.get("phone")),  # Phone
                format_phone(r.get("fax")),  # Fax
                safe_str(r.get("email", "")),  # Website (email is closest)
                description,  # Description
                payment_terms,  # Payment_Terms__c
                safe_str(r["supplier_code"]),  # ohfy__Distributor_Vendor_ID_Number__c (SUPPLIERT.SUPPLIER)
                safe_str(r.get("edi_id", "")),  # GS1_Prefix__c
                safe_str(r.get("vendor_id", "")),  # ohfy__QuickBooks_Customer_ID__c (APVENT.VRVEND)
                "TRUE" if safe_str(r.get("sales_tax_flag")).upper() == "N" else "FALSE",  # Is_Tax_Exempt__c
                is_active(r.get("status")),  # Is_Active__c
                safe_str(
                    r.get("supplier_identity", r.get("vip_identity", ""))
                ),  # ohfy__External_ID__c (SUPPLIERT.IDENTITY)
            ]
        )
    return result


def map_premise_type(on_off):
    """Map VIP CMONOF to premise type."""
    v = safe_str(on_off)
    if v == "1":
        return "On Premise"
    if v == "2":
        return "Off Premise"
    return ""


def map_payment_terms(term_code):
    """Map VIP CMTERM to payment terms description."""
    m = {
        "1": "COD",
        "F": "Net 15",
        "3": "Net 30",
        "0": "Prepaid",
        "E": "Net 45",
        "2": "Net 10",
        "5": "Net 60",
        "9": "Net 7",
        "8": "EOM",
        "I": "In Advance",
        "H": "Net 21",
        "N": "No Terms",
    }
    return m.get(safe_str(term_code), safe_str(term_code))


def format_lat_lon(val):
    """Convert VIP integer lat/lon to decimal degrees (stored as degrees * 1,000,000)."""
    if not val:
        return ""
    try:
        v = float(val)
        if v == 0:
            return ""
        return str(round(v / 1000000, 6))
    except (ValueError, TypeError):
        return ""


def transform_chain_banners(rows):
    """Transform VIP HDRCHAINT rows → Account (Chain Banner) rows."""
    result = []
    rt_id = get_record_type_id("Account", "Chain Banner")
    for r in rows:
        chain_code = safe_str(r["chain_code"])
        chain_name = safe_str(r["chain_name"])
        if not chain_code or not chain_name:
            continue
        customer_count = int(r.get("customer_count") or 0)
        street = safe_str(r.get("street", ""))
        city = safe_str(r.get("city", ""))
        state = safe_str(r.get("state", ""))
        zip_code = safe_str(r.get("zip", ""))
        result.append(
            [
                rt_id,  # RecordTypeId
                chain_name,  # Name
                chain_code,  # ohfy__Customer_Number__c
                "Chain Banner",  # Type
                street,  # BillingStreet
                city,  # BillingCity
                state,  # BillingState
                zip_code,  # BillingPostalCode
                "US" if city else "",  # BillingCountry
                street,  # ShippingStreet
                city,  # ShippingCity
                state,  # ShippingState
                zip_code,  # ShippingPostalCode
                "US" if city else "",  # ShippingCountry
                format_phone(r.get("phone")),  # Phone
                "TRUE" if customer_count > 0 else "FALSE",  # ohfy__Is_Active__c
                safe_str(r.get("vip_identity", chain_code)),  # ohfy__External_ID__c
            ]
        )
    return result


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


def transform_customers(rows):
    """Transform VIP BRATTT rows → Account (Customer) rows."""
    result = []
    seen = set()
    for r in rows:
        acct = safe_str(r["account_number"])
        if acct in seen or not acct:
            continue
        seen.add(acct)

        dba = safe_str(r["dba_name"])
        legal = safe_str(r["legal_name"])
        if not dba and not legal:
            continue

        status = safe_str(r.get("status", ""))
        premise = map_premise_type(r.get("on_off_premise"))
        rt_id = get_record_type_id("Account", "Customer")

        street = safe_str(r.get("street", ""))
        city = safe_str(r.get("city", ""))
        state = safe_str(r.get("state_code", ""))
        zip_code = safe_str(r.get("zip_code", ""))

        # Build invoice notes from CMTEXT + CMINST
        notes_parts = []
        if safe_str(r.get("notes")):
            notes_parts.append(safe_str(r["notes"]))
        if safe_str(r.get("instructions")):
            notes_parts.append(f"Instructions: {safe_str(r['instructions'])}")
        invoice_notes = "; ".join(notes_parts)

        market_desc = safe_str(r.get("market_desc", ""))
        chain_code = safe_str(r.get("chain_code", ""))

        result.append(
            [
                rt_id,  # RecordTypeId
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
                street,  # ShippingStreet (copy from billing)
                city,  # ShippingCity
                state,  # ShippingState
                zip_code,  # ShippingPostalCode
                "US",  # ShippingCountry
                format_phone(r.get("phone")),  # Phone
                format_phone(r.get("fax")),  # Fax
                WAREHOUSE_TO_TERRITORY.get(safe_str(r.get("warehouse", "")), ""),  # Territory__c (by Name)
                safe_str(r.get("beer_route", "")),  # Route__c
                safe_str(r.get("beer_salesman", "")),  # Sales_Rep__c
                chain_code,  # Chain_Banner__c
                safe_str(r.get("customer_class", "")),  # Customer_Class__c
                safe_str(r.get("license_number", "")),  # License_Number__c
                safe_str(r.get("license_1", "")),  # ABC_License_Number__c
                vip_date_to_sf(r.get("license_exp_date")),  # ABC_License_Expiration_Date__c
                map_payment_terms(r.get("payment_term")),  # Payment_Terms__c
                "TRUE" if safe_str(r.get("tax_code")).upper() == "Y" else "FALSE",  # Is_Tax_Exempt__c
                safe_str(r.get("credit_limit", "")),  # Credit_Limit__c
                safe_str(r.get("ar_balance", "")),  # Account_Balance__c
                format_lat_lon(r.get("latitude")),  # Latitude__c
                format_lat_lon(r.get("longitude")),  # Longitude__c
                map_delivery_method(r.get("delivery_method")),  # Delivery_Method__c
                safe_str(r.get("warehouse", "")),  # Fulfillment_Location__c
                safe_str(r.get("price_group", "")),  # Pricelist__c
                map_market_type(market_desc),  # Market__c
                map_retail_type(chain_code, market_desc),  # Retail_Type__c
                vip_date_to_sf(r.get("business_open_date")),  # Customer_Since__c
                invoice_notes,  # Invoice_Notes__c
                safe_str(r.get("store_pin", "")),  # Store_Number__c
                is_active(status),  # Is_Active__c
                safe_str(r.get("vip_identity", acct)),  # ohfy__External_ID__c (BRATTT.CMIDENTITY)
            ]
        )
    return result


def transform_items(rows):
    """Transform VIP item rows → Item__c rows.

    Field mapping (VIP → Ohanafy):
      PACKAGE_DESCRIPTION       → Name
      ITEM_CODE                 → Item_Number__c, State_Item_Code__c, External_ID__c, Key__c, VIP_External_ID__c
      BRAND_CODE                → Item_Type__c (lookup key — resolves to Item_Type via Key__c)
      SUPPLIER_CODE             → Item_Line__c (lookup key — resolves to Item_Line via Key__c)
      PRODUCT_CLASS             → Type__c (Finished Good / Merchandise / Overhead)
      CONTAINER_TYPE_CODE       → Package_Type__c (700-series → Kegged, else Packaged)
      PACKAGE_SIZE + CONTAINER  → Packaging_Type__c (mapped to org picklist: 1/6 Barrel(s), etc.)
      PACKAGE_SHORT             → Packaging_Type_Short_Name__c (e.g. "1/6 BBL", "4/6/12Z CAN")
      PRODUCT_CLASS             → UOM__c (wine/spirits → US Volume, else US Count)
      UNITS_CASE                → Units_Per_Case__c
      CASE_WEIGHT               → Weight__c (all VIP weights are in pounds)
      (hardcoded)               → Weight_UOM__c = "Pound(s)"
      CASES_KEGS_PER_PALLET     → Cases_Per_Pallet__c
      SUGGESTED_SELLING_PRICE   → Default_Case_Price__c
      CASE_UPC                  → Case_UPC__c (12-digit padded)
      CASE_GTIN                 → Case_GTIN__c (14-digit padded)
      BOTTLE_UPC                → Unit_UPC__c (12-digit), also → UPC__c
      BOTTLE_GTIN               → Unit_GTIN__c (14-digit padded)
      RETAIL_UPC                → Retailer_UPC__c (12-digit padded)
      BOTTLE_UPC                → UPC__c (canonical single-unit UPC)
      SUPPLIER_SKU              → Supplier_Number__c
      SUPPLIER_SKU              → SKU_Number__c (same value, different field purpose)
      DEPOSITST.DPDEPO          → Keg_Deposit__c (actual $ amount from deposit table; $50 default for kegs missing a record)
      PALLET_UPC                → Carrier_UPC__c (14-digit padded)
      RETAIL_GTIN               → Pack_GTIN__c (14-digit padded)
      OZ_CASE                   → UOM_In_Fluid_Ounces__c
      RETAIL_SELL_UNITS_CASE    → Retail_Units_Per_Case__c
      ITEM_STATUS               → Is_Active__c, Item_Purposes__c
      TAXABLE_FLAG              → Is_Tax_Exempt__c (inverted: Y=taxable → FALSE exempt)
      SELLABLE_BY_UNIT          → Is_Sold_In_Units__c, Can_Credit_In_Units__c
    """
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        pkg_desc = safe_str(r["pkg_desc"])
        brand_code = safe_str(r["brand_code"])
        supplier_code = safe_str(r["supplier_code"])
        container = safe_str(r.get("container_type", ""))
        product_class = safe_str(r.get("product_class", ""))
        uom_code = safe_str(r.get("uom_code", ""))
        package_size = safe_str(r.get("package_size", ""))
        pkg_short = safe_str(r.get("pkg_short", ""))
        supplier_sku = safe_str(r.get("supplier_sku", ""))
        bottle_upc = format_upc(r.get("bottle_upc"), 12)
        deposit_amount = r.get("deposit_amount")

        # Keg deposit: use actual DEPOSITST dollar amount; default $50 for kegged items missing a record
        # Ohanafy validation rule E001 REQUIRES Keg_Deposit__c on barrel-type Finished Good items
        pkg_type = map_package_type(container, uom_code)
        if pkg_type == "Kegged":
            if deposit_amount and float(deposit_amount) > 0:
                keg_deposit = f"{float(deposit_amount):.2f}"
            else:
                keg_deposit = "50.00"  # Gulf default: 98% of kegs are $50
        else:
            keg_deposit = ""

        item_type = map_item_record_type(product_class, pkg_type)
        rt_id = get_record_type_id("ohfy__Item__c", item_type)

        result.append(
            [
                rt_id,  # RecordTypeId
                pkg_desc,  # Name
                item_code,  # Item_Number__c
                brand_code,  # Item_Type__c (lookup key)
                supplier_code,  # Item_Line__c (lookup key)
                item_type,  # Type__c
                pkg_type,  # Package_Type__c
                map_packaging_type_picklist(package_size, container, pkg_type == "Kegged"),  # Packaging_Type__c
                pkg_short,  # Packaging_Type_Short_Name__c
                map_uom(product_class),  # UOM__c
                safe_str(r.get("units_per_case", "")),  # Units_Per_Case__c
                safe_str(r.get("case_weight", "")),  # Weight__c
                "Pound(s)",  # Weight_UOM__c
                safe_str(r.get("per_pallet", "")),  # Cases_Per_Pallet__c
                safe_str(r.get("ssp", "")),  # Default_Case_Price__c
                format_upc(r.get("case_upc"), 12),  # Case_UPC__c
                format_upc(r.get("case_gtin"), 14),  # Case_GTIN__c
                bottle_upc,  # Unit_UPC__c
                format_upc(r.get("bottle_gtin"), 14),  # Unit_GTIN__c
                format_upc(r.get("retail_upc"), 12),  # Retailer_UPC__c
                bottle_upc,  # UPC__c (same as Unit_UPC)
                supplier_sku,  # Supplier_Number__c
                supplier_sku,  # SKU_Number__c
                item_code,  # State_Item_Code__c
                pkg_short,  # Short_Name__c
                is_active(r.get("item_status")),  # Is_Active__c
                "TRUE" if safe_str(r.get("taxable")).upper() != "Y" else "FALSE",  # Is_Tax_Exempt__c
                "TRUE" if safe_str(r.get("sell_by_unit")).upper() == "Y" else "FALSE",  # Is_Sold_In_Units__c
                "TRUE" if safe_str(r.get("sell_by_unit")).upper() == "Y" else "FALSE",  # Can_Credit_In_Units__c
                keg_deposit,  # Keg_Deposit__c
                format_upc(r.get("pallet_upc"), 14),  # Carrier_UPC__c
                format_upc(r.get("retail_gtin"), 14),  # Pack_GTIN__c
                safe_str(r.get("oz_case", "")),  # UOM_In_Fluid_Ounces__c
                safe_str(r.get("retail_units_case", "")),  # Retail_Units_Per_Case__c
                "Buy;Sell" if is_active(r.get("item_status")) == "TRUE" else "None",  # Item_Purposes__c
                "TRUE" if item_type == "Finished Good" else "FALSE",  # Is_Lot_Tracked__c (all Finished Goods)
                "Damaged,Breakage,Spoilage,Returned"
                if is_active(r.get("item_status")) == "TRUE" and item_type == "Finished Good"
                else "",  # Credit_Type__c
                item_code,  # VIP_External_ID__c
                item_code,  # External_ID__c
                item_code,  # Key__c
            ]
        )
    return result


# Container code → display name for keg shell naming
KEG_SIZE_DISPLAY = {
    "710": "1/6bbl",
    "720": "1/4bbl",
    "730": "1/2bbl",
    "700": "50L",
    "705": "30L",
    "706": "10.8gal",
    "707": "5.4gal",
    "590": "20L",
    "715": "25L",
}

# Container code → Ohanafy Stock_UOM_Sub_Type__c picklist
KEG_SIZE_UOM_SUBTYPE = {
    "710": "1/6 Barrel(s)",
    "720": "1/4 Barrel(s)",
    "730": "1/2 Barrel(s)",
    "700": "Barrel(s)",
    "705": "Barrel(s)",
    "706": "Barrel(s)",
    "707": "Barrel(s)",
    "590": "20 Liter(s)",
    "715": "Barrel(s)",
}


def transform_keg_shell_items(rows):
    """Transform distinct supplier+keg-size combos → Keg Shell Item__c rows.

    Creates one empty keg shell item per unique (SUPPLIER_CODE, CONTAINER_TYPE_CODE).
    These are Dunnage items representing the returnable keg for deposit tracking.
    """
    rt_id = get_record_type_id("ohfy__Item__c", "Keg Shell")
    seen = set()
    result = []
    item_number = 990001

    for r in rows:
        supplier_code = safe_str(r["supplier_code"])
        supplier_name = safe_str(r["supplier_name"])
        container_code = safe_str(r["container_code"])
        brand_code = safe_str(r.get("brand_code", ""))

        combo_key = f"{supplier_code}-{container_code}"
        if combo_key in seen:
            continue
        seen.add(combo_key)

        size_display = KEG_SIZE_DISPLAY.get(container_code, container_code)
        uom_subtype = KEG_SIZE_UOM_SUBTYPE.get(container_code, "Barrel(s)")
        name = f"Empty {supplier_name} {size_display} Keg"
        key = f"KEG-SHELL-{supplier_code}-{container_code}"

        result.append(
            [
                rt_id,  # RecordTypeId
                name,  # Name
                str(item_number),  # Item_Number__c
                brand_code,  # Item_Type__c (lookup key)
                supplier_code,  # Item_Line__c (lookup key)
                "Keg Shell",  # Type__c
                "Kegged",  # Package_Type__c
                "US Volume",  # UOM__c
                uom_subtype,  # Packaging_Type__c
                "Pound(s)",  # Weight_UOM__c
                "TRUE",  # Is_Active__c
                "Buy;Sell",  # Item_Purposes__c
                "TRUE",  # Is_Tax_Exempt__c
                "50.00",  # Keg_Deposit__c ($50 Gulf default)
                "Returned;Keg Return",  # Credit_Type__c
                "1",  # Units_Per_Case__c
                key,  # VIP_External_ID__c
                key,  # External_ID__c
                key,  # Key__c
            ]
        )
        item_number += 1

    return result


def transform_item_components(rows):
    """Transform kegged items → Item_Component__c rows.

    Creates one Item Component per kegged item, linking it to the matching
    supplier-specific empty keg shell. Parent_Item__c and Child_Item__c
    contain Key__c values — resolve to SF IDs at load time.
    """
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        supplier_code = safe_str(r["supplier_code"])
        container_code = safe_str(r["container_code"])

        child_key = f"KEG-SHELL-{supplier_code}-{container_code}"
        component_key = f"{item_code}|{child_key}"

        result.append(
            [
                item_code,  # Parent_Item__c (Key__c of parent item)
                child_key,  # Child_Item__c (Key__c of keg shell)
                "1",  # Quantity__c
                component_key,  # Key__c
            ]
        )
    return result


def transform_parent_locations(rows):
    """Transform HDRWHSET rows → Location__c rows."""
    # Warehouse city/state derived from known Gulf Distributing locations
    WAREHOUSE_LOCATIONS = {
        "1": ("Mobile", "AL"),
        "2": ("Milton", "FL"),
        "5": ("Jackson", "MS"),
        "6": ("Gulfport", "MS"),
        "7": ("Montgomery", "AL"),
        "9": ("Birmingham", "AL"),
        "10": ("Huntsville", "AL"),
        "11": ("Mobile", "AL"),  # ABC Board
        "99": ("Mobile", "AL"),  # AL Liquor Sales
        "J": ("Jackson", "MS"),  # Old Jackson A/R
    }
    PARENT_LOCATION_RT = "012WE00000LTeCaYAL"
    result = []
    for r in rows:
        wh = safe_str(r["warehouse_code"])
        name = safe_str(r["warehouse_name"]) or wh
        city, state = WAREHOUSE_LOCATIONS.get(wh, ("", ""))
        result.append(
            [
                PARENT_LOCATION_RT,  # RecordTypeId
                name,  # Name
                "Warehouse",  # Type__c
                wh,  # Key__c
                wh,  # Location_Code__c
                "TRUE",  # Is_Active__c
                "TRUE",  # Is_Finished_Good__c
                "TRUE",  # Is_Sellable__c
                "TRUE",  # Is_Merchandise__c
                "TRUE",  # Is_Tap_Handle__c
                "FALSE",  # Is_Dirty_Keg_Location__c
                "FALSE",  # Is_Keg_Shell__c
                "FALSE",  # Is_Truck__c
                "",  # Location_Street__c (needs manual entry)
                city,  # Location_City__c
                state,  # Location_State__c
                "",  # Location_Postal_Code__c (needs manual entry)
                "US",  # Location_County__c (country)
                "",  # Company__c (picklist — set in org)
                "",  # Notes__c
            ]
        )
    return result


def transform_child_locations(rows):
    """Transform zone rows (derived from location code prefix) → Location__c rows."""
    LOCATION_RT = "012WE00000LTeCZYA1"
    result = []
    for r in rows:
        wh = safe_str(r["warehouse_code"])
        zone = safe_str(r["zone_code"])
        key = f"{wh}-{zone}"
        result.append(
            [
                LOCATION_RT,  # RecordTypeId
                f"Zone {zone}",  # Name
                wh,  # Parent_Location__c (lookup key)
                "Zone",  # Type__c
                "TRUE",  # Is_Active__c
                "TRUE",  # Is_Sellable__c
                key,  # Key__c
                zone,  # Location_Code__c
            ]
        )
    return result


def transform_pick_paths(rows):
    """Transform pick-path rows → Location__c rows (bins within zones)."""
    result = []
    for r in rows:
        wh = safe_str(r["warehouse_code"])
        zone = safe_str(r["zone_code"])
        loc = safe_str(r["location_code"])
        desc = safe_str(r["location_desc"]) or loc
        parent_key = f"{wh}-{zone}" if zone else wh
        key = f"{wh}-{loc}"
        status = safe_str(r.get("status", ""))

        # Detect dirty keg locations from description
        desc_upper = desc.upper()
        is_dirty_keg = "TRUE" if any(k in desc_upper for k in ("BAD KEG", "DIRTY KEG", "DIRTY")) else "FALSE"

        # Detect sellable: available + pickable
        is_sellable = (
            "TRUE"
            if safe_str(r.get("is_available")).upper() in ("Y", "1")
            and safe_str(r.get("is_pick")).upper() in ("Y", "1")
            else "FALSE"
        )
        is_finished = "TRUE" if safe_str(r.get("is_available")).upper() in ("Y", "1") else "FALSE"

        notes_parts = [desc] if desc and desc != loc else []
        if r.get("pick_sequence"):
            notes_parts.append(f"Pick Seq: {safe_str(r['pick_sequence'])}")
        if r.get("capacity_cases") and float(r.get("capacity_cases", 0) or 0) > 0:
            notes_parts.append(f"Cap (cases): {safe_str(r['capacity_cases'])}")
        if r.get("capacity_pallets") and float(r.get("capacity_pallets", 0) or 0) > 0:
            notes_parts.append(f"Cap (pallets): {safe_str(r['capacity_pallets'])}")

        result.append(
            [
                desc,  # Name
                parent_key,  # Parent_Location__c (lookup key)
                "Bin",  # Type__c
                is_active(status),  # Is_Active__c
                is_sellable,  # Is_Sellable__c
                is_finished,  # Is_Finished_Good__c
                is_dirty_keg,  # Is_Dirty_Keg_Location__c
                "; ".join(notes_parts),  # Notes__c
                key,  # Key__c
            ]
        )
    return result


def transform_territories(rows):
    """Transform warehouse rows → parent Territory__c rows (geographic regions)."""
    result = []
    for r in rows:
        wh = safe_str(r["warehouse_code"])
        name = WAREHOUSE_TO_TERRITORY.get(wh, safe_str(r["warehouse_name"]) or f"Territory {wh}")
        result.append(
            [
                name,  # Name
                "TRUE",  # Is_Active__c
            ]
        )
    return result


def transform_equipment(rows):
    """Transform truck rows → Equipment__c rows."""
    result = []
    for r in rows:
        truck_num = safe_str(r["truck_number"])
        desc = safe_str(r["truck_desc"]) or truck_num
        result.append(
            [
                desc,  # Name
                truck_num,  # Abbreviation__c
                "Truck",  # Type__c
                "Active",  # Status__c
                safe_str(r.get("capacity_lbs", "")),  # Tare_Weight__c
                truck_num,  # Key__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_routes(rows):
    """Transform route rows → Route__c rows."""
    result = []
    for r in rows:
        code = safe_str(r["route_code"])
        desc = safe_str(r["route_desc"]) or ""
        # Name = "Route {code} - {driver}" for readability
        name = f"Route {code}"
        if desc:
            name = f"Route {code} - {desc.title()}"
        result.append(
            [
                name,  # Name
                "Delivery",  # Type__c
                "",  # Frequency__c (varies by route, set post-load)
                "TRUE",  # Is_Active__c
                code,  # Key__c
            ]
        )
    return result


def transform_fees(rows):
    """Transform deposit rows → Fee__c rows."""
    result = []
    seen = set()
    for r in rows:
        dep_type = safe_str(r["deposit_type"]) or "Deposit"
        amount = safe_str(r["deposit_amount"])
        key = f"{dep_type}-{amount}"
        if key in seen:
            continue
        seen.add(key)

        type_map = {"D": "Keg Deposit", "R": "Return", "C": "CRV"}
        fee_type = type_map.get(safe_str(r.get("fee_type", "")).upper(), "Misc. Charge")

        result.append(
            [
                f"{fee_type} - ${amount}",  # Name
                amount,  # Default_Amount__c
                fee_type
                if fee_type in ("Freight", "Fuel Surcharge", "Shipping", "Storage", "Service", "Pallet", "Misc. Charge")
                else "Misc. Charge",
                "TRUE",  # Is_Active__c
                "TRUE",  # Is_Invoice__c
                "FALSE",  # Is_Inventory_Receipt__c
                key,  # Key__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_pricelists(rows):
    """Transform discount worksheet rows → Pricelist__c rows."""
    result = []
    seen = set()
    for r in rows:
        code = safe_str(r["discount_code"])
        if code in seen:
            continue
        seen.add(code)

        desc = safe_str(r["discount_desc"]) or code
        dtype = safe_str(r.get("discount_type", ""))
        ohfy_type = "Individual Price" if dtype.upper() in ("I", "P") else "Discount"
        disc_type = "Percent" if dtype.upper() in ("P", "%") else "Dollars"

        result.append(
            [
                desc,  # Name
                ohfy_type,  # Type__c
                disc_type,  # Discount_Type__c
                vip_date_to_sf(r.get("start_date")),  # Start_Date__c
                vip_date_to_sf(r.get("end_date")),  # End_Date__c
                "TRUE",  # Is_Active__c
                code,  # Key__c
            ]
        )
    return result


def transform_pricelist_items(rows):
    """Transform pending price rows → Pricelist_Item__c rows."""
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        disc_code = safe_str(r["discount_code"]) or safe_str(r.get("price_code", ""))
        case_price = safe_str(r.get("case_price", ""))
        each_price = safe_str(r.get("each_price", ""))
        post_off = safe_str(r.get("post_off", ""))
        key = f"{disc_code}-{item_code}"

        result.append(
            [
                item_code,  # Item__c (lookup by External_ID)
                disc_code,  # Pricelist__c (lookup by Key__c)
                case_price,  # Case_Price__c
                each_price,  # Unit_Price__c
                post_off,  # Discount_Dollars__c
                "",  # Discount_Percent__c
                key,  # Key__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


# Chain code (from HDRCHAINT) → price codes in priority order.
# Chain-specific codes first, then generic base codes as fallback.
CHAIN_PRICE_CODES = {
    "1485": ["1A", "9A", "7A", "HA", "8A", "01"],  # WALMART
    "1145": ["1C", "9C", "HC", "7C", "8C", "01"],  # PUBLIX
    "1060": ["13", "03", "H3", "93", "73", "83"],  # IND ON PREM
    "0755": ["13", "03", "H3", "93", "73", "83"],  # IND RESTAURANT
    "0735": ["11", "01", "51", "H1", "91", "71", "81"],  # IND CSTORE
    "0763": ["11", "01", "H1", "91", "71", "81"],  # IND DELTA9 OFF
    "0760": ["11", "01", "51", "H1", "91", "71", "81"],  # IND DRUG
    "0745": ["11", "01", "51", "H1", "91", "71", "81"],  # IND GROCERY
    "0750": ["11", "01", "51", "H1", "91", "71", "81"],  # IND LIQUOR
    "0664": ["11", "01", "H1", "91", "71", "81"],  # IND NEIGHBOR S
    "0756": ["11", "01", "51", "H1", "91", "71", "81"],  # IND TOBACCO
}


def transform_chain_pricelists(rows):
    """Transform HDRCHAINT rows → one Pricelist__c per chain banner."""
    result = []
    for r in rows:
        chain_code = safe_str(r["chain_code"])
        chain_name = safe_str(r["chain_name"]) or chain_code
        # Strip leading zeros to match Customer_Number__c as loaded
        chain_num = chain_code.lstrip("0") or chain_code
        key = f"CHP-{chain_num}"

        result.append(
            [
                chain_name.title(),  # Name
                "Settings",  # Type__c (customer-specific pricing)
                "Dollars",  # Discount_Type__c
                "2025-01-01",  # Start_Date__c
                "2099-12-31",  # End_Date__c
                "TRUE",  # Is_Active__c
                key,  # Key__c
            ]
        )
    return result


def transform_chain_pricelist_items(rows):
    """Transform deployment master rows → Pricelist_Item__c per chain per item.

    Uses prioritized price codes: chain-specific codes (e.g., 1A for Walmart)
    take precedence over generic base codes (e.g., 01 Goldring Off-Prem).
    For each item × chain, the first matching price code wins.
    """
    # Build reverse map: price_code → list of (chain_code, priority) tuples
    price_code_to_chains = {}
    for chain, codes in CHAIN_PRICE_CODES.items():
        for priority, prcd in enumerate(codes):
            price_code_to_chains.setdefault(prcd, []).append((chain, priority))

    # First pass: collect all candidate prices per (chain, item)
    # Key = (chain_num, item_code), Value = (priority, case_price)
    best = {}
    for r in rows:
        item_code = safe_str(r["item_code"])
        price_code = safe_str(r["price_code"])
        sell = float(r.get("sell_price") or 0)
        front = float(r.get("front_price") or 0)
        case_price = sell if sell > 0 else front

        if case_price <= 0:
            continue

        for chain_code, priority in price_code_to_chains.get(price_code, []):
            chain_num = chain_code.lstrip("0") or chain_code
            key = (chain_num, item_code)
            if key not in best or priority < best[key][0]:
                best[key] = (priority, case_price)

    # Second pass: build result rows from deduplicated best prices
    result = []
    for (chain_num, item_code), (_, case_price) in sorted(best.items()):
        pricelist_key = f"CHP-{chain_num}"
        item_key = f"{pricelist_key}-{item_code}"

        result.append(
            [
                item_code,  # Item__c (lookup by Key__c)
                pricelist_key,  # Pricelist__c (lookup by Key__c)
                f"{case_price:.2f}",  # Case_Price__c
                item_key,  # Key__c
            ]
        )
    return result


def _load_supplier_lookup():
    """Build supplier_code → External_ID__c mapping from Suppliers.csv."""
    suppliers_csv = Path(__file__).parent / "migration_output" / "Suppliers.csv"
    lookup = {}
    if suppliers_csv.exists():
        with open(suppliers_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cust_num = (row.get("ohfy__Customer_Number__c") or "").strip()
                ext_id = (row.get("ohfy__External_ID__c") or "").strip()
                if cust_num and ext_id:
                    lookup[cust_num] = ext_id
    return lookup


def transform_lots(rows):
    """Transform active items → Lot__c rows. One lot per item.

    Name = '{Item Name} - {MM/DD/YYYY}' (truncated to 80 chars).
    Lot_Identifier = '{item_code}-{YYYYMMDD}'.
    Supplier resolved via ITEMT.SUPPLIER_CODE → Suppliers.csv Customer_Number → External_ID.
    Cost from latest PO in PODTLT.
    """
    exp_date_sf = "2026-12-31"  # Salesforce date format
    exp_date_display = "12/31/2026"  # Display format for Name
    exp_date_compact = "20261231"  # Compact format for Lot_Identifier
    supplier_lookup = _load_supplier_lookup()
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        pkg_desc = safe_str(r["pkg_desc"])
        supplier_code = safe_str(r.get("supplier_code", ""))
        latest_cost = safe_str(r.get("latest_cost", "0"))
        lot_name = f"{pkg_desc} - {exp_date_display}"
        if len(lot_name) > 80:
            lot_name = lot_name[:80]
        # Resolve supplier code to Account External_ID__c
        supplier_ext_id = supplier_lookup.get(supplier_code, "")
        # Format cost — strip trailing zeros but keep 2 decimal places minimum
        try:
            cost_val = float(latest_cost)
            cost_str = f"{cost_val:.2f}" if cost_val > 0 else ""
        except (ValueError, TypeError):
            cost_str = ""
        result.append(
            [
                lot_name,  # Name
                item_code,  # Item__c (lookup via External_ID__c)
                f"{item_code}-{exp_date_compact}",  # Lot_Identifier__c
                exp_date_sf,  # Expiration_Date__c
                "2026-03-17",  # Receipt_Date__c
                "TRUE",  # Is_Active__c
                "TRUE",  # Is_Sellable__c
                supplier_ext_id,  # Supplier (via External_ID__c lookup)
                cost_str,  # Cost_Per_Unit__c
            ]
        )
    return result


def transform_inventory(rows):
    """Transform active items × warehouses → Inventory__c rows. Seed qty 1000 per warehouse."""
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        wh = safe_str(r["warehouse_code"])
        zone = safe_str(r.get("default_zone", ""))
        if not zone:
            continue  # Skip warehouses with no zones in LOCMAST
        location_key = f"{wh}-{zone}"
        # Default inventory only for warehouse 1 (Mobile)
        is_default = "TRUE" if wh == "1" else "FALSE"
        result.append(
            [
                item_code,  # Item__c (lookup via External_ID__c)
                location_key,  # Location__c (zone Key__c)
                "1000",  # Quantity_On_Hand__c
                "1000",  # Quantity_Available__c
                "TRUE",  # Is_Active__c
                is_default,  # Is_Default_Inventory__c
                "Initial Load",  # Reason__c
            ]
        )
    return result


def transform_lot_inventory(rows):
    """Transform active items × warehouses → Lot_Inventory__c rows.

    Both Inventory__c and Lot__c are MasterDetail fields requiring SF record IDs.
    This outputs reference keys that must be replaced with actual SF IDs before loading:
      - Inventory ref: 'INV-{item_code}-{wh}-{zone}' → query Inventory by Item + Location
      - Lot ref: '{item_code}-20261231' → query Lot by Lot_Identifier__c
    """
    result = []
    for r in rows:
        item_code = safe_str(r["item_code"])
        wh = safe_str(r["warehouse_code"])
        zone = safe_str(r.get("default_zone", ""))
        if not zone:
            continue  # Skip warehouses with no zones
        result.append(
            [
                f"INV-{item_code}-{wh}-{zone}",  # Inventory__c (needs SF ID)
                f"{item_code}-20261231",  # Lot__c (needs SF ID)
                "1000",  # Quantity_On_Hand__c
            ]
        )
    return result


def transform_users(rows):
    """Transform VIP user rows → User reference rows."""
    result = []
    for r in rows:
        result.append(
            [
                safe_str(r.get("first_name", "")),
                safe_str(r.get("last_name", "")),
                safe_str(r.get("email", "")),
                safe_str(r.get("job_title", "")),
                safe_str(r.get("employee_code", "")),
                safe_str(r.get("department", "")),
                safe_str(r.get("default_warehouse", "")),
            ]
        )
    return result


def transform_contacts(rows):
    """Transform BRATTT buyer field → Contact rows."""
    result = []
    seen = set()
    for r in rows:
        acct = safe_str(r["account_number"])
        buyer = safe_str(r.get("buyer_name", ""))
        if not buyer or not acct:
            continue

        key = f"{acct}-{buyer}"
        if key in seen:
            continue
        seen.add(key)

        # Split buyer name into first/last
        parts = buyer.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = " ".join(parts[1:])
        elif len(parts) == 1:
            first_name = ""
            last_name = parts[0]
        else:
            continue

        # Handle multiple contacts separated by & or AND
        if " & " in buyer or " AND " in buyer.upper():
            # Keep as-is, put full name in LastName
            first_name = ""
            last_name = buyer

        result.append(
            [
                first_name,  # FirstName
                last_name,  # LastName
                acct,  # AccountId (lookup)
                format_phone(r.get("phone")),  # Phone
                format_phone(r.get("fax")),  # Fax
                "Buyer",  # Title
                "Primary",  # ohfy__Level__c
                "TRUE",  # ohfy__Is_Billing_Contact__c
                "TRUE",  # ohfy__Is_Delivery_Contact__c
            ]
        )
    return result


def transform_account_routes(rows):
    """Transform BRATTT account-route junction rows."""
    result = []
    seen = set()
    for r in rows:
        acct = safe_str(r["account_number"])
        route = safe_str(r.get("route_code", ""))
        if not acct or not route:
            continue

        key = f"{acct}-{route}"
        if key in seen:
            continue
        seen.add(key)

        day = safe_str(r.get("delivery_day", ""))
        seq = safe_str(r.get("delivery_sequence", ""))
        status = safe_str(r.get("status", ""))

        result.append(
            [
                acct,  # ohfy__Customer__c (lookup by External_ID)
                route,  # ohfy__Route__c (lookup by Key__c)
                day,  # Delivery_Day__c
                seq,  # ohfy__Stop_Order__c
                is_active(status),  # ohfy__Is_Active_Route__c
                key,  # ohfy__Key__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_prospects(rows):
    """Transform VIP BRATTT inactive rows → Account (Prospect) rows."""
    result = []
    seen = set()
    for r in rows:
        acct = safe_str(r["account_number"])
        if acct in seen or not acct:
            continue
        seen.add(acct)

        dba = safe_str(r["dba_name"])
        legal = safe_str(r["legal_name"])
        if not dba and not legal:
            continue

        premise = map_premise_type(r.get("on_off_premise"))

        rt_id = get_record_type_id("Account", "Customer")

        result.append(
            [
                rt_id,  # RecordTypeId
                dba or legal,  # Name
                legal,  # ohfy__Legal_Name__c
                acct,  # ohfy__Customer_Number__c
                "Customer",  # Type
                "Prospect",  # ohfy__Prospect_Stage__c
                premise,  # ohfy__Premise_Type__c
                safe_str(r.get("street", "")),  # BillingStreet
                safe_str(r.get("city", "")),  # BillingCity
                safe_str(r.get("state_code", "")),  # BillingState
                safe_str(r.get("zip_code", "")),  # BillingPostalCode
                "US",  # BillingCountry
                format_phone(r.get("phone")),  # Phone
                format_phone(r.get("fax")),  # Fax
                safe_str(r.get("chain_code", "")),  # ohfy__Chain_Banner__c
                safe_str(r.get("customer_class", "")),  # ohfy__Customer_Class__c
                safe_str(r.get("license_number", "")),  # ohfy__License_Number__c
                map_payment_terms(r.get("payment_term")),  # ohfy__Payment_Terms__c
                "FALSE",  # ohfy__Is_Active__c
                safe_str(r.get("vip_identity", acct)),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_allocations_customer(rows):
    """Transform VIP allocation rows → Allocation__c rows."""
    result = []
    for r in rows:
        alloc_id = safe_str(r.get("alloc_id", ""))
        desc = safe_str(r.get("alloc_desc", "")) or alloc_id
        customer = safe_str(r.get("customer_code", ""))
        item = safe_str(r.get("item_code", ""))
        key = f"{alloc_id}-{customer}-{item}"

        result.append(
            [
                desc,  # Name
                customer,  # ohfy__Customer__c (lookup)
                item,  # ohfy__Item__c (lookup)
                safe_str(r.get("alloc_qty", "")),  # ohfy__Allocated_Case_Amount__c
                safe_str(r.get("ship_qty", "")),  # ohfy__Allocated_Cases_Sold__c
                vip_date_to_sf(r.get("start_date")),  # ohfy__Start_Date__c
                vip_date_to_sf(r.get("end_date")),  # ohfy__End_Date__c
                "TRUE",  # ohfy__Is_Active__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_promotions(rows):
    """Transform VIP DISCOUTT rows → Promotion rows."""
    result = []
    for r in rows:
        item = safe_str(r.get("item_code", ""))
        price_code = safe_str(r.get("price_code", ""))
        disc_code = safe_str(r.get("discount_code", ""))
        key = f"{disc_code}-{item}-{price_code}"

        dtype = safe_str(r.get("discount_type", ""))
        type_map = {"P": "Post-Off", "F": "Front-Line", "S": "Special", "I": "Individual"}
        promo_type = type_map.get(dtype.upper(), "Discount")

        result.append(
            [
                item,  # ohfy__Item__c
                disc_code,  # ohfy__Pricelist__c
                price_code,  # Discount_Code__c
                promo_type,  # ohfy__Type__c
                vip_date_to_sf(r.get("start_date")),  # ohfy__Start_Date__c
                vip_date_to_sf(r.get("end_date")),  # ohfy__End_Date__c
                "TRUE",  # ohfy__Is_Active__c
                key,  # ohfy__Key__c
                safe_str(r.get("vip_identity", "")),  # ohfy__External_ID__c
            ]
        )
    return result


def transform_overhead(rows):
    """Transform VIP deposit aggregates → Overhead rows."""
    result = []
    for r in rows:
        name = safe_str(r.get("overhead_name", "")) or "Unnamed"
        price = safe_str(r.get("default_price", ""))
        result.append(
            [
                name,  # Name
                price,  # Default_Price__c
                "",  # Last_Purchase_Price__c
                "TRUE",  # Is_Active__c
                name,  # Key__c
            ]
        )
    return result


def transform_data_validation(rows):
    """Transform picklist value rows."""
    result = []
    for r in rows:
        result.append(
            [
                safe_str(r.get("object_name", "")),
                safe_str(r.get("field_name", "")),
                safe_str(r.get("picklist_value", "")),
            ]
        )
    return result


def transform_record_types(rows):
    """Transform record type rows."""
    result = []
    for r in rows:
        result.append(
            [
                safe_str(r.get("object_name", "")),
                safe_str(r.get("record_type_name", "")),
                safe_str(r.get("description", "")),
            ]
        )
    return result


def transform_progress_tracker(rows):
    """Transform progress tracker rows with extra empty columns for manual entry."""
    result = []
    for r in rows:
        result.append(
            [
                safe_str(r.get("tab_name", "")),
                safe_str(r.get("ohanafy_object", "")),
                safe_str(r.get("load_order", "")),
                "Not Started",  # Status
                "",  # Loaded By
                "",  # Date Loaded
                "",  # Row Count
                "",  # Notes
            ]
        )
    return result


def transform_user_warehouse_permissions(rows):
    """Pivot user-warehouse rows into a boolean permission grid.

    Input rows have one row per user-warehouse assignment (with NULLs for
    users without assignments). Output is one row per user with TRUE/FALSE
    columns for each warehouse.
    """
    # Collect all warehouses and build user data
    warehouses = set()
    users = {}  # keyed by user_identity
    for r in rows:
        uid = r["user_identity"]
        wh = safe_str(r.get("assigned_warehouse", ""))
        if wh:
            warehouses.add(wh)
        if uid not in users:
            users[uid] = {
                "emp_id": safe_str(r.get("emp_id", "")),
                "first_name": safe_str(r.get("first_name", "")),
                "last_name": safe_str(r.get("last_name", "")),
                "title": safe_str(r.get("title", "")),
                "email": safe_str(r.get("email", "")),
                "default_warehouse": safe_str(r.get("default_warehouse", "")),
                "warehouses": set(),
            }
        if wh:
            users[uid]["warehouses"].add(wh)

    # Sort warehouses for consistent column order
    sorted_wh = sorted(warehouses)

    # Build the headers dynamically for this tab
    # Find the tab definition and update its headers
    for tab in TABS:
        if tab["name"] == "User_Warehouse_Permissions":
            tab["headers"] = ["Employee ID", "First Name", "Last Name", "Title", "Email", "Default Warehouse"] + [
                f"WH {w}" for w in sorted_wh
            ]
            break

    # Build output rows
    result = []
    for uid in sorted(users.keys(), key=lambda u: (users[u]["last_name"], users[u]["first_name"])):
        u = users[uid]
        row = [
            u["emp_id"],
            u["first_name"],
            u["last_name"],
            u["title"],
            u["email"],
            u["default_warehouse"],
        ]
        for wh in sorted_wh:
            row.append("TRUE" if wh in u["warehouses"] else "FALSE")
        result.append(row)
    return result


# Map tab names to transform functions
TRANSFORM_MAP = {
    "Item_Lines": transform_item_lines,
    "Item_Types": transform_item_types,
    "Suppliers": transform_suppliers,
    "Chain_Banners": transform_chain_banners,
    "Customers": transform_customers,
    "Items": transform_items,
    "Keg_Shell_Items": transform_keg_shell_items,
    "Item_Components": transform_item_components,
    "Parent_Locations": transform_parent_locations,
    "Child_Locations": transform_child_locations,
    "Pick_Paths": transform_pick_paths,
    "Territories": transform_territories,
    "Equipment_Vehicles": transform_equipment,
    "Routes": transform_routes,
    "Fees": transform_fees,
    "Pricelists": transform_pricelists,
    "Pricelist_Items": transform_pricelist_items,
    "Chain_Pricelists": transform_chain_pricelists,
    "Chain_Pricelist_Items": transform_chain_pricelist_items,
    "Lots": transform_lots,
    "Inventory": transform_inventory,
    "Lot_Inventory": transform_lot_inventory,
    "Users": transform_users,
    "Contacts": transform_contacts,
    "Account_Routes": transform_account_routes,
    "Prospects": transform_prospects,
    "Allocations_Customer": transform_allocations_customer,
    "Promotions": transform_promotions,
    "Overhead": transform_overhead,
    "Data_Validation_Sales": transform_data_validation,
    "Data_Validation_Inventory": transform_data_validation,
    "Record_Types": transform_record_types,
    "Progress_Tracker": transform_progress_tracker,
    "User_Warehouse_Permissions": transform_user_warehouse_permissions,
}


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db_connection():
    """Create a PostgreSQL connection."""
    print(f"  Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def run_query(conn, sql):
    """Execute a query and return rows as list of dicts."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql)
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------
def get_sheets_client():
    """Authenticate and return gspread client."""
    # Try multiple paths for service account
    sa_paths = [
        SERVICE_ACCOUNT_PATH,
        Path(__file__).parent / "service-account.json",
        Path.home() / "service-account.json",
    ]
    sa_path = None
    for p in sa_paths:
        if p.exists():
            sa_path = p
            break

    if not sa_path:
        raise FileNotFoundError(f"Service account JSON not found. Tried: {[str(p) for p in sa_paths]}")

    print(f"  Using service account: {sa_path}")
    creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    return gspread.authorize(creds)


def write_tab(spreadsheet, tab_name, headers, data_rows, retries=3):
    """Write headers + data to a sheet tab, creating it if needed."""
    # Find or create worksheet
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=max(len(data_rows) + 10, 100), cols=len(headers) + 2)

    # Check for two-row headers (friendly names + API names)
    friendly = FRIENDLY_HEADERS.get(tab_name)

    # Resize if needed
    header_rows = 2 if friendly else 1
    needed_rows = len(data_rows) + header_rows + 1
    needed_cols = len(headers) + 1
    if ws.row_count < needed_rows or ws.col_count < needed_cols:
        ws.resize(rows=max(needed_rows, 100), cols=max(needed_cols, 20))

    # Prepare all data (headers + rows)
    if friendly:
        all_data = [friendly, headers] + data_rows
    else:
        all_data = [headers] + data_rows

    # Write in batches to avoid API limits
    batch_size = 1000
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i : i + batch_size]
        start_row = i + 1
        end_row = start_row + len(batch) - 1
        end_col = chr(ord("A") + len(headers) - 1) if len(headers) <= 26 else "Z"

        for attempt in range(retries):
            try:
                ws.update(
                    range_name=f"A{start_row}",
                    values=batch,
                )
                break
            except gspread.exceptions.APIError as e:
                if "RATE_LIMIT" in str(e) or "429" in str(e):
                    wait = (attempt + 1) * 30
                    print(f"    Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise

        # Small delay between batches to avoid rate limiting
        if i + batch_size < len(all_data):
            time.sleep(1)

    print(f"    {tab_name}: {len(data_rows)} rows written")
    return ws


def write_loading_guide(spreadsheet):
    """Write the Loading Guide tab."""
    guide_data = []
    for row in LOADING_GUIDE:
        if isinstance(row, list):
            formatted = [str(c).replace("{date}", datetime.now().strftime("%Y-%m-%d")) for c in row]
            guide_data.append(formatted)
        else:
            guide_data.append([str(row)])

    # Pad rows to same width
    max_cols = max(len(r) for r in guide_data)
    for r in guide_data:
        while len(r) < max_cols:
            r.append("")

    try:
        ws = spreadsheet.worksheet("Loading_Guide")
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title="Loading_Guide", rows=len(guide_data) + 10, cols=max_cols + 2)

    ws.update(range_name="A1", values=guide_data)
    print(f"    Loading_Guide: {len(guide_data)} rows written")
    return ws


# ---------------------------------------------------------------------------
# CSV export (backup / offline mode)
# ---------------------------------------------------------------------------
def export_csvs(output_dir, all_tab_data):
    """Export all tabs as CSV files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for tab_name, headers, data_rows in all_tab_data:
        filepath = output_dir / f"{tab_name}.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)
        print(f"    {filepath}: {len(data_rows)} rows")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="VIP to Ohanafy Migration")
    parser.add_argument("--csv-only", action="store_true", help="Export CSVs without Google Sheets")
    parser.add_argument("--sheet-id", default=DEFAULT_SHEET_ID, help="Google Sheet ID")
    parser.add_argument("--output-dir", default="./migration_output", help="CSV output directory")
    parser.add_argument("--tabs", nargs="*", help="Only process specific tabs (space-separated)")
    args = parser.parse_args()

    print("=" * 60)
    print("VIP to Ohanafy Migration")
    print("=" * 60)

    # Step 1: Connect to VIP database
    print("\n[1/3] Connecting to VIP database...")
    try:
        conn = get_db_connection()
        print("  Connected successfully!")
    except Exception as e:
        print(f"  ERROR connecting to database: {e}")
        print("  Tip: Set PGHOST, PGUSER, PGPASSWORD env vars to override defaults.")
        sys.exit(1)

    # Sort tabs by load_order for correct dependency sequencing
    TABS.sort(key=lambda t: t["load_order"])

    # Step 2: Extract and transform data
    print("\n[2/3] Extracting and transforming data...")
    all_tab_data = []

    for tab in TABS:
        tab_name = tab["name"]
        if args.tabs and tab_name not in args.tabs:
            continue

        print(f"\n  Processing: {tab_name}")
        try:
            sql = tab["sql"]
            # Inject supplier→vendor overrides into the Supplier query
            if tab_name == "Suppliers":
                if not SUPPLIER_OVERRIDES:
                    load_supplier_overrides()
                if SUPPLIER_OVERRIDES:
                    # Build a temp table of overrides and use it in the query
                    with conn.cursor() as tmp_cur:
                        tmp_cur.execute("DROP TABLE IF EXISTS tmp_supplier_overrides")
                        tmp_cur.execute("CREATE TEMP TABLE tmp_supplier_overrides (supplier_code TEXT, vrvend NUMERIC)")
                        values = [(code, int(vrvend)) for code, vrvend in SUPPLIER_OVERRIDES.items()]
                        tmp_cur.executemany("INSERT INTO tmp_supplier_overrides VALUES (%s, %s)", values)
                        conn.commit()
                    # Modify the SQL to include override path in the CTE
                    sql = sql.replace(
                        """WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
            ORDER BY s."SUPPLIER", v."VRADD1" IS NULL, v."VRVEND" NULLS LAST
        )""",
                        """WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
            ORDER BY s."SUPPLIER", v."VRADD1" IS NULL, v."VRVEND" NULLS LAST
        ),
        -- Human-reviewed fuzzy match overrides (from supplier_vendor_overrides.csv)
        override_matches AS (
            SELECT
                TRIM(s."SUPPLIER") AS supplier_code,
                TRIM(s."SUPPLIER_NAME") AS supplier_name,
                TRIM(s."EDI_TRADING_PARTNER_ID") AS edi_id,
                s."IDENTITY" AS supplier_identity,
                ov.vrvend AS vrvend
            FROM staging."SUPPLIERT" s
            JOIN tmp_supplier_overrides ov ON TRIM(s."SUPPLIER") = ov.supplier_code
            WHERE COALESCE(TRIM(s."DELETE_FLAG"), '') <> 'Y'
        ),
        -- Merge: prefer override match, then original match
        merged AS (
            SELECT
                sv.supplier_code, sv.supplier_name, sv.edi_id, sv.supplier_identity,
                COALESCE(om.vrvend, sv.vrvend) AS vrvend
            FROM supplier_vrvend sv
            LEFT JOIN override_matches om ON sv.supplier_code = om.supplier_code
        )""",
                    )
                    # Replace references to supplier_vrvend with merged
                    # Only in the main query body, not inside the CTE definitions
                    # The main query has "LEFT JOIN supplier_vrvend sv ON" and "FROM supplier_vrvend sv\n"
                    sql = sql.replace("LEFT JOIN supplier_vrvend sv ON", "LEFT JOIN merged sv ON")
                    # The UNION ALL part: "FROM supplier_vrvend sv\n        WHERE sv.vrvend IS NULL"
                    sql = sql.replace(
                        "FROM supplier_vrvend sv\n        WHERE sv.vrvend IS NULL",
                        "FROM merged sv\n        WHERE sv.vrvend IS NULL",
                    )

            raw_rows = run_query(conn, sql)
            print(f"    Extracted {len(raw_rows)} raw rows")

            transform_fn = TRANSFORM_MAP.get(tab_name)
            if transform_fn:
                transformed = transform_fn(raw_rows)
            else:
                # Fallback: just stringify all values
                transformed = [[safe_str(v) for v in r.values()] for r in raw_rows]

            all_tab_data.append((tab_name, tab["headers"], transformed))
            print(f"    Transformed to {len(transformed)} rows with {len(tab['headers'])} columns")

        except Exception as e:
            conn.rollback()  # Reset transaction so next query works
            print(f"    ERROR: {e}")
            # Continue with other tabs
            all_tab_data.append((tab_name, tab["headers"], []))

    conn.close()

    # Step 3: Output
    if args.csv_only:
        print(f"\n[3/3] Exporting CSVs to {args.output_dir}...")
        export_csvs(args.output_dir, all_tab_data)
    else:
        print(f"\n[3/3] Writing to Google Sheet: {args.sheet_id}...")
        try:
            gc = get_sheets_client()
            spreadsheet = gc.open_by_key(args.sheet_id)
            print(f"  Opened sheet: {spreadsheet.title}")

            # Write Loading Guide first
            write_loading_guide(spreadsheet)
            time.sleep(2)  # Rate limit buffer

            # Write each data tab
            for tab_name, headers, data_rows in all_tab_data:
                write_tab(spreadsheet, tab_name, headers, data_rows)
                time.sleep(2)  # Rate limit buffer

            print(f"\n  Sheet URL: https://docs.google.com/spreadsheets/d/{args.sheet_id}")

        except Exception as e:
            print(f"  ERROR writing to Google Sheets: {e}")
            print("  Falling back to CSV export...")
            export_csvs(args.output_dir, all_tab_data)

    # Also export CSVs as backup
    if not args.csv_only:
        print(f"\n  Also saving CSV backup to {args.output_dir}...")
        export_csvs(args.output_dir, all_tab_data)

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
