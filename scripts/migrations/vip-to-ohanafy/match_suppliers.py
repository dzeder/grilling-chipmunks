#!/usr/bin/env python3
"""
Fuzzy-match unmatched VIP Suppliers to AP Vendors (APVENT).

Produces a CSV of proposed matches for human review, then a final
supplier_vendor_overrides.csv that the migration script can consume.
"""

import csv
import re
import psycopg2
import psycopg2.extras
from difflib import SequenceMatcher
from pathlib import Path

DB_CONFIG = {
    "host": "gulfstream-db2-data.postgres.database.azure.com",
    "port": 5432,
    "dbname": "gulfstream",
    "user": "ohanafy",
    "password": "Xq7!mR#2vK$9pLw@nZ",
    "sslmode": "require",
}

OUTPUT_DIR = Path(__file__).parent / "migration_output"

# Words to strip for matching (common suffixes that differ between supplier/vendor names)
NOISE = re.compile(
    r"\b(LLC|INC|CO|CORP|COMPANY|CORPORATION|BREWING|BREWERY|DISTILLING|DISTILLERY|"
    r"BEVERAGE|BEVERAGES|BRANDS|BRAND|DISTRIBUT\w*|IMPORT\w*|WINE\w*|SPIRIT\w*|"
    r"USA|OF\s+\w+|THE|\*+EFT|\*+E|\*+)\b",
    re.IGNORECASE,
)


def normalize(name):
    """Normalize a name for comparison."""
    if not name:
        return ""
    s = name.upper().strip()
    s = NOISE.sub("", s)
    s = re.sub(r"[^A-Z0-9 ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similarity(a, b):
    """Return similarity ratio between two normalized strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def word_overlap(a, b):
    """Return Jaccard similarity of word sets."""
    wa = set(a.split())
    wb = set(b.split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def combined_score(supplier_name, vendor_name):
    """Combined fuzzy score using sequence matching + word overlap."""
    na = normalize(supplier_name)
    nb = normalize(vendor_name)
    seq = similarity(na, nb)
    words = word_overlap(na, nb)
    # Weighted: 60% sequence, 40% word overlap
    return 0.6 * seq + 0.4 * words


def main():
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 1. Get unmatched suppliers
    print("Finding unmatched suppliers...")
    cur.execute("""
        WITH supplier_vrvend AS (
            SELECT DISTINCT ON (s."SUPPLIER")
                TRIM(s."SUPPLIER") AS supplier_code,
                TRIM(s."SUPPLIER_NAME") AS supplier_name,
                s."IDENTITY" AS supplier_identity,
                v."VRVEND" AS vrvend
            FROM staging."SUPPLIERT" s
            LEFT JOIN staging."APVENT" v ON v.import_is_deleted = false
                AND (
                    (TRIM(s."AP_VENDOR") <> '0' AND TRIM(s."AP_VENDOR") = CAST(v."VRVEND" AS TEXT))
                    OR (
                        LENGTH(REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g')) >= 3
                        AND (
                            REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g')
                                LIKE REGEXP_REPLACE(UPPER(TRIM(s."SUPPLIER_NAME")), '[^A-Z0-9]', '', 'g') || '%%'
                            OR REGEXP_REPLACE(UPPER(TRIM(s."SUPPLIER_NAME")), '[^A-Z0-9]', '', 'g')
                                LIKE REGEXP_REPLACE(UPPER(TRIM(v."VRNAME")), '[^A-Z0-9]', '', 'g') || '%%'
                        )
                    )
                    OR (TRIM(s."AP_VENDOR") <> '0' AND TRIM(s."AP_VENDOR") = CAST(v."VRIDENTITY" AS TEXT))
                    OR EXISTS (
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
        SELECT supplier_code, supplier_name, supplier_identity
        FROM supplier_vrvend
        WHERE vrvend IS NULL
        ORDER BY supplier_name
    """)
    unmatched = cur.fetchall()
    print(f"  Found {len(unmatched)} unmatched suppliers")

    # 2. Get all AP vendors with addresses
    print("Loading AP vendors...")
    cur.execute("""
        SELECT v."VRVEND" AS vrvend, TRIM(v."VRNAME") AS vendor_name,
               TRIM(v."VRADD1") AS addr1, TRIM(v."VRADD2") AS addr2,
               TRIM(c."CITYNAME") AS city, TRIM(c."STATE") AS state,
               TRIM(v."POSTALCODE") AS zip,
               TRIM(v."VRSSTAT") AS status
        FROM staging."APVENT" v
        LEFT JOIN staging."CITYT" c ON v."ID_CITY" = c."IDENTITY"
        WHERE v.import_is_deleted = false
        ORDER BY v."VRNAME"
    """)
    vendors = cur.fetchall()
    print(f"  Loaded {len(vendors)} AP vendors")
    conn.close()

    # 3. For each unmatched supplier, find best vendor matches
    print("\nScoring matches...")
    results = []
    for sup in unmatched:
        sup_name = sup["supplier_name"]
        sup_code = sup["supplier_code"]

        # Score all vendors
        scored = []
        for v in vendors:
            vname = v["vendor_name"] or ""
            score = combined_score(sup_name, vname)
            if score >= 0.25:  # Minimum threshold to be a candidate
                scored.append((score, v))

        # Take top 3 candidates
        scored.sort(key=lambda x: -x[0])
        top = scored[:3]

        if top and top[0][0] >= 0.40:
            best_score, best = top[0]
            confidence = "HIGH" if best_score >= 0.65 else "MEDIUM" if best_score >= 0.50 else "LOW"
            results.append(
                {
                    "supplier_code": sup_code,
                    "supplier_name": sup_name,
                    "confidence": confidence,
                    "score": f"{best_score:.2f}",
                    "matched_vrvend": str(best["vrvend"]),
                    "matched_vendor_name": best["vendor_name"],
                    "matched_addr": best["addr1"] or "",
                    "matched_city": best["city"] or "",
                    "matched_state": best["state"] or "",
                    "matched_zip": best["zip"] or "",
                    "alt_2_vrvend": str(top[1][1]["vrvend"]) if len(top) > 1 else "",
                    "alt_2_name": (top[1][1]["vendor_name"] or "") if len(top) > 1 else "",
                    "alt_2_score": f"{top[1][0]:.2f}" if len(top) > 1 else "",
                    "alt_3_vrvend": str(top[2][1]["vrvend"]) if len(top) > 2 else "",
                    "alt_3_name": (top[2][1]["vendor_name"] or "") if len(top) > 2 else "",
                    "alt_3_score": f"{top[2][0]:.2f}" if len(top) > 2 else "",
                    "action": "ACCEPT" if confidence == "HIGH" else "REVIEW",
                }
            )
        else:
            results.append(
                {
                    "supplier_code": sup_code,
                    "supplier_name": sup_name,
                    "confidence": "NONE",
                    "score": f"{top[0][0]:.2f}" if top else "0.00",
                    "matched_vrvend": str(top[0][1]["vrvend"]) if top else "",
                    "matched_vendor_name": (top[0][1]["vendor_name"] or "") if top else "",
                    "matched_addr": (top[0][1]["addr1"] or "") if top else "",
                    "matched_city": (top[0][1]["city"] or "") if top else "",
                    "matched_state": (top[0][1]["state"] or "") if top else "",
                    "matched_zip": (top[0][1]["zip"] or "") if top else "",
                    "alt_2_vrvend": "",
                    "alt_2_name": "",
                    "alt_2_score": "",
                    "alt_3_vrvend": "",
                    "alt_3_name": "",
                    "alt_3_score": "",
                    "action": "SKIP",
                }
            )

    # 4. Write review CSV
    review_path = OUTPUT_DIR / "supplier_vendor_review.csv"
    with open(review_path, "w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "action",
                "confidence",
                "score",
                "supplier_code",
                "supplier_name",
                "matched_vrvend",
                "matched_vendor_name",
                "matched_addr",
                "matched_city",
                "matched_state",
                "matched_zip",
                "alt_2_vrvend",
                "alt_2_name",
                "alt_2_score",
                "alt_3_vrvend",
                "alt_3_name",
                "alt_3_score",
            ],
        )
        w.writeheader()
        w.writerows(results)

    # 5. Auto-generate overrides for HIGH confidence matches
    overrides_path = OUTPUT_DIR / "supplier_vendor_overrides.csv"
    accepted = [r for r in results if r["confidence"] == "HIGH"]
    with open(overrides_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["supplier_code", "vrvend"])
        w.writeheader()
        for r in accepted:
            w.writerow({"supplier_code": r["supplier_code"], "vrvend": r["matched_vrvend"]})

    # Summary
    high = sum(1 for r in results if r["confidence"] == "HIGH")
    med = sum(1 for r in results if r["confidence"] == "MEDIUM")
    low = sum(1 for r in results if r["confidence"] == "LOW")
    none = sum(1 for r in results if r["confidence"] == "NONE")

    print(f"\n{'=' * 60}")
    print(f"Results: {len(results)} unmatched suppliers analyzed")
    print(f"  HIGH confidence (auto-accept):  {high}")
    print(f"  MEDIUM confidence (review):     {med}")
    print(f"  LOW confidence (review):        {low}")
    print(f"  NO match found:                 {none}")
    print(f"\nReview file:    {review_path}")
    print(f"Overrides file: {overrides_path}")
    print("\nEdit the review CSV — change 'action' to ACCEPT/SKIP, then")
    print("re-run the migration to use the overrides.")


if __name__ == "__main__":
    main()
