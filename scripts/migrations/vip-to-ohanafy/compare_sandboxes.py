#!/usr/bin/env python3
"""Compare all Ohanafy objects between Gulf partial-copy and CAM sandboxes."""

import json
import os
import subprocess
from datetime import datetime

PARTIAL = "gulf-partial-copy-sandbox"
CAM = "gulf-cam-sandbox"

SKIP_FIELDS = {
    "Id",
    "OwnerId",
    "IsDeleted",
    "CreatedById",
    "CreatedDate",
    "LastModifiedById",
    "LastModifiedDate",
    "SystemModstamp",
    "CurrencyIsoCode",
    "LastReferencedDate",
    "LastViewedDate",
    "LastActivityDate",
    "PhotoUrl",  # contains org-specific SF record IDs
}

# Fields that differ for known reasons — tracked separately, not counted as mismatches.
# key = (object_api_name, field_api_name), value = reason string
KNOWN_DIFFS = {
    ("ohfy__Route__c", "ohfy__Driver__c"): "Different placeholder users per org (mobile.driver vs ckoorangi)",
    ("Account", "ohfy__Sales_Rep__c"): "Different placeholder users per org (integrations vs ckoorangi)",
    ("Account", "Status__c"): "Non-ohfy custom field — not part of migration CSV",
}

# How to resolve a reference to each object type (None = skip)
REF_KEY = {
    "Account": "ohfy__External_ID__c",
    "RecordType": "DeveloperName",
    "User": "Username",
    "Group": None,
    "ohfy__Territory__c": "Name",
    "ohfy__Fee__c": "ohfy__Key__c",
    "ohfy__Pricelist__c": "ohfy__Key__c",
    "ohfy__Transformation_Setting__c": "ohfy__Key__c",
    "ohfy__Location__c": "ohfy__Key__c",
    "ohfy__Equipment__c": "ohfy__Key__c",
    "ohfy__Item_Line__c": "ohfy__Key__c",
    "ohfy__Item_Type__c": "ohfy__Key__c",
    "ohfy__Route__c": "ohfy__Key__c",
    "ohfy__Item__c": "ohfy__Key__c",
    "ohfy__Item_Component__c": "ohfy__Key__c",
    "ohfy__Lot__c": "Name",
    "ohfy__Inventory__c": None,  # auto-numbered
    "ohfy__Pricelist_Item__c": "ohfy__Key__c",
    "ohfy__Promotion__c": "Name",
    "ohfy__Account_Route__c": "ohfy__Key__c",
    "ohfy__Lot_Inventory__c": None,  # auto-numbered
    "ohfy__Pricelist_Setting__c": "ohfy__Key__c",
    "ohfy__Pricelist_Account__c": "ohfy__Key__c",
    "ohfy__Incentive__c": "ohfy__Key__c",
    "ohfy__Billback__c": "Name",
    "ohfy__Invoice__c": "ohfy__External_ID__c",
    "ohfy__Purchase_Order__c": "Name",
    "ohfy__Display__c": "ohfy__Key__c",
    "ohfy__Display_Run__c": "ohfy__Key__c",
    "ohfy__Tier_Setting__c": "ohfy__Key__c",
    "Contact": "Name",
}

OBJECTS = [
    {"name": "Territory", "api": "ohfy__Territory__c", "key": "Name"},
    {"name": "Fee", "api": "ohfy__Fee__c", "key": "ohfy__Key__c"},
    {"name": "Pricelist", "api": "ohfy__Pricelist__c", "key": "ohfy__Key__c"},
    {"name": "Transformation_Setting", "api": "ohfy__Transformation_Setting__c", "key": "ohfy__Key__c"},
    {"name": "Location", "api": "ohfy__Location__c", "key": "ohfy__Key__c"},
    {"name": "Equipment", "api": "ohfy__Equipment__c", "key": "ohfy__Key__c"},
    {"name": "Item_Line", "api": "ohfy__Item_Line__c", "key": "ohfy__Key__c"},
    {"name": "Item_Type", "api": "ohfy__Item_Type__c", "key": "ohfy__Key__c"},
    {"name": "Route", "api": "ohfy__Route__c", "key": "ohfy__Key__c"},
    {"name": "Account", "api": "Account", "key": "ohfy__External_ID__c", "where": "ohfy__External_ID__c != null"},
    {
        "name": "Contact",
        "api": "Contact",
        "key": None,
        "composite": ["Account.ohfy__External_ID__c", "LastName", "FirstName"],
        "where": "Account.ohfy__External_ID__c != null",
    },
    {"name": "Item", "api": "ohfy__Item__c", "key": "ohfy__Key__c"},
    {"name": "Item_Component", "api": "ohfy__Item_Component__c", "key": "ohfy__Key__c"},
    {"name": "Lot", "api": "ohfy__Lot__c", "key": "Name"},
    {
        "name": "Inventory",
        "api": "ohfy__Inventory__c",
        "key": None,
        "composite": ["ohfy__Item__r.ohfy__Key__c", "ohfy__Location__r.ohfy__Key__c"],
    },
    {"name": "Pricelist_Item", "api": "ohfy__Pricelist_Item__c", "key": "ohfy__Key__c"},
    {"name": "Promotion", "api": "ohfy__Promotion__c", "key": "Name"},
    {"name": "Account_Route", "api": "ohfy__Account_Route__c", "key": "ohfy__Key__c"},
    {
        "name": "Lot_Inventory",
        "api": "ohfy__Lot_Inventory__c",
        "key": None,
        "composite": [
            "ohfy__Lot__r.Name",
            "ohfy__Inventory__r.ohfy__Item__r.ohfy__Key__c",
            "ohfy__Inventory__r.ohfy__Location__r.ohfy__Key__c",
        ],
    },
]


def sf_json(args, timeout=300):
    try:
        proc = subprocess.run(["sf"] + args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "Timed out"
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return None, (proc.stdout or "")[:200] + (proc.stderr or "")[:200]
    if proc.returncode != 0:
        return None, data.get("message", str(data))[:300]
    return data, None


def describe(api_name, org=PARTIAL):
    data, err = sf_json(["sobject", "describe", "--sobject", api_name, "--target-org", org, "--json"])
    if err:
        return [], err
    return data.get("result", {}).get("fields", []), None


def describe_both(api_name):
    """Describe object in both orgs, return only fields that exist in BOTH."""
    p_fields, p_err = describe(api_name, PARTIAL)
    if p_err:
        return [], p_err
    c_fields, c_err = describe(api_name, CAM)
    if c_err:
        return [], c_err
    # Intersect by field name, use partial's metadata
    cam_names = {f["name"] for f in c_fields}
    shared = [f for f in p_fields if f["name"] in cam_names]
    dropped = len(p_fields) - len(shared)
    if dropped:
        print(f"  ({dropped} fields only in partial, excluded)")
    return shared, None


def query(org, soql):
    data, err = sf_json(["data", "query", "--query", soql, "--target-org", org, "--json"], timeout=600)
    if err:
        return [], err
    return data.get("result", {}).get("records", []), None


def dot_get(obj, path):
    for part in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def eq(a, b):
    if a == b:
        return True
    # null vs empty string
    if (a is None and b == "") or (a == "" and b is None):
        return True
    # null vs 0 for numeric fields (rollups/formulas default to 0 in some orgs)
    if (a is None and b == 0) or (a == 0 and b is None):
        return True
    if (a is None and b == 0.0) or (a == 0.0 and b is None):
        return True
    if a is None or b is None:
        return False
    # numeric tolerance
    try:
        return abs(float(a) - float(b)) < 0.001
    except (TypeError, ValueError):
        pass
    return str(a).strip() == str(b).strip()


def audit_object(cfg):
    name, api = cfg["name"], cfg["api"]
    print(f"\n--- {name} ({api}) ---")

    fields_meta, err = describe_both(api)
    if err:
        print(f"  DESCRIBE ERROR: {err}")
        return {"name": name, "error": f"Describe: {err}"}

    select = []
    compare_map = {}
    formulas = set()
    skipped_refs = []

    for f in fields_meta:
        fn, ft = f["name"], f["type"]
        if fn in SKIP_FIELDS or f.get("autoNumber") or ft in ("address", "location", "base64"):
            continue

        if ft == "reference":
            rel = f.get("relationshipName")
            refs = f.get("referenceTo", [])
            if not rel or not refs:
                continue
            biz = REF_KEY.get(refs[0])
            if biz is None:
                skipped_refs.append(f"{fn}->{refs[0]}")
                continue
            path = f"{rel}.{biz}"
            select.append(path)
            compare_map[fn] = path
            if f.get("calculated"):
                formulas.add(fn)
            continue

        if ft == "id":
            continue
        # Skip ALL formula/calculated fields — they're derived from base data.
        # Formula fields often contain org-specific SF IDs (e.g. Supplier__c,
        # Location_Hierarchy_Dev__c) which always differ between orgs.
        if f.get("calculated"):
            formulas.add(fn)
            continue
        select.append(fn)
        compare_map[fn] = fn

    for ck in cfg.get("composite", []):
        if ck not in select:
            select.append(ck)
    mk = cfg.get("key")
    if mk and mk not in select:
        select.append(mk)

    select = list(dict.fromkeys(select))  # dedupe preserving order

    where = f" WHERE {cfg['where']}" if cfg.get("where") else ""
    soql = f"SELECT {', '.join(select)} FROM {api}{where}"
    print(f"  {len(select)} fields | SOQL len={len(soql)}")

    print("  Partial...", end=" ", flush=True)
    p_recs, p_err = query(PARTIAL, soql)
    if p_err:
        print(f"ERROR: {p_err[:80]}")
        return {"name": name, "error": f"Partial: {p_err[:200]}"}
    print(f"{len(p_recs)}", end="  |  ", flush=True)

    print("CAM...", end=" ", flush=True)
    c_recs, c_err = query(CAM, soql)
    if c_err:
        print(f"ERROR: {c_err[:80]}")
        return {"name": name, "error": f"CAM: {c_err[:200]}"}
    print(f"{len(c_recs)}")

    def make_key(rec):
        if mk:
            v = dot_get(rec, mk)
            return str(v) if v is not None else None
        parts = [str(dot_get(rec, c) or "") for c in cfg.get("composite", [])]
        return "|".join(parts) if any(parts) else None

    def flatten(rec):
        return {label: dot_get(rec, path) for label, path in compare_map.items()}

    p_dict, c_dict = {}, {}
    for r in p_recs:
        k = make_key(r)
        if k:
            p_dict[k] = flatten(r)
    for r in c_recs:
        k = make_key(r)
        if k:
            c_dict[k] = flatten(r)

    only_p = sorted(set(p_dict) - set(c_dict))
    only_c = sorted(set(c_dict) - set(p_dict))
    common = sorted(set(p_dict) & set(c_dict))

    mismatches = []
    known_mismatches = []
    for key in common:
        pr, cr = p_dict[key], c_dict[key]
        diffs = []
        known = []
        for label in sorted(compare_map):
            if not eq(pr.get(label), cr.get(label)):
                entry = {
                    "field": label,
                    "partial": pr.get(label),
                    "cam": cr.get(label),
                    "formula": label in formulas,
                }
                reason = KNOWN_DIFFS.get((api, label))
                if reason:
                    entry["known_reason"] = reason
                    known.append(entry)
                else:
                    diffs.append(entry)
        if diffs:
            mismatches.append({"key": key, "diffs": diffs})
        if known:
            known_mismatches.append({"key": key, "diffs": known})

    ok = not mismatches and not only_p and not only_c
    tag = "MATCH" if ok else "DIFF"
    kn = f"  known={len(known_mismatches)}" if known_mismatches else ""
    print(
        f"  {tag}: {len(common)} matched, {len(mismatches)} mismatched, {len(only_p)} only-P, {len(only_c)} only-C{kn}"
    )
    if skipped_refs:
        print(
            f"  Skipped refs: {', '.join(skipped_refs[:5])}"
            + (f" +{len(skipped_refs) - 5} more" if len(skipped_refs) > 5 else "")
        )

    return {
        "name": name,
        "api": api,
        "partial_count": len(p_recs),
        "cam_count": len(c_recs),
        "matched": len(common),
        "mismatched": len(mismatches),
        "only_partial": only_p,
        "only_cam": only_c,
        "mismatches": mismatches,
        "known_mismatches": known_mismatches,
        "fields_compared": len(compare_map),
        "formula_count": len(formulas),
        "skipped_refs": skipped_refs,
    }


def esc(v):
    """HTML-escape a value."""
    if v is None:
        return '<span class="null">null</span>'
    return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_report(results, path):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    ok = [r for r in results if "error" not in r]
    errs = [r for r in results if "error" in r]

    tot_p = sum(r["partial_count"] for r in ok)
    tot_c = sum(r["cam_count"] for r in ok)
    tot_m = sum(r["matched"] for r in ok)
    tot_d = sum(r["mismatched"] for r in ok)
    tot_kn = sum(len(r.get("known_mismatches", [])) for r in ok)
    tot_op = sum(len(r["only_partial"]) for r in ok)
    tot_oc = sum(len(r["only_cam"]) for r in ok)
    denom = tot_m + tot_op + tot_oc
    rate = f"{(tot_m - tot_d) / denom * 100:.1f}" if denom else "0"
    rate_num = float(rate) if rate != "0" else 0

    # Annotations — human-written context for specific objects
    ANNOTATIONS = {
        "Item_Type": {
            "verdict": "CAM is correct",
            "note": 'Partial has Key__c code as Short_Name (e.g. "11"), CAM has the real abbreviation (e.g. "BS"). The CAM migration correctly mapped PKGTYPE from ITMPCKT.',
        },
        "Contact": {
            "verdict": "Partial is correct",
            "note": "ohfy__Is_Delivery_Contact__c should be TRUE (set in migration CSV). CAM load appears to have dropped this column — likely a Bulk API field mapping issue.",
        },
        "Item": {
            "verdict": "Partial is correct",
            "note": "ohfy__UOM_In_Fluid_Ounces__c — CAM stored 1/value instead of value (e.g. 0.00347 instead of 288). The CAM migration script inverted this field.",
        },
        "Inventory": {
            "verdict": "Partial is correct",
            "note": "ohfy__Inventory_Value_Lot_Tracked__c — 8 records for item 77427 have value=67000 in Partial but 0 in CAM. CAM load missed this field.",
        },
        "Pricelist_Item": {
            "verdict": "11 items missing from CAM",
            "note": "11 Pricelist Items exist in Partial but not CAM. Likely items with null External_ID that failed the CAM upsert.",
        },
        "Account": {
            "verdict": "CAM has more data",
            "note": "ohfy__Billing_Contact__c is populated in CAM (146 accounts) but null in Partial. This field was added after the initial Partial load.",
        },
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CAM vs Partial Copy — Sandbox Audit</title>
<style>
  :root {{ --green: #22c55e; --yellow: #eab308; --red: #ef4444; --blue: #3b82f6; --orange: #f97316; --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #e2e8f0; --muted: #94a3b8; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; line-height: 1.5; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.3rem; }}
  .subtitle {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 2rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1.2rem; text-align: center; }}
  .card .num {{ font-size: 2rem; font-weight: 700; }}
  .card .label {{ font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.3rem; }}
  .card.green .num {{ color: var(--green); }}
  .card.yellow .num {{ color: var(--yellow); }}
  .card.red .num {{ color: var(--red); }}
  .card.orange .num {{ color: var(--orange); }}
  .rate-bar {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 2rem; }}
  .rate-bar .track {{ background: #334155; border-radius: 6px; height: 28px; position: relative; overflow: hidden; }}
  .rate-bar .fill {{ height: 100%; border-radius: 6px; transition: width 0.8s ease; }}
  .rate-bar .rate-label {{ display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.85rem; color: var(--muted); }}
  .rate-bar .rate-label strong {{ color: var(--text); font-size: 1.1rem; }}
  section {{ margin-bottom: 2.5rem; }}
  h2 {{ font-size: 1.2rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ background: var(--card); text-align: left; padding: 0.6rem 0.8rem; border-bottom: 2px solid var(--border); font-weight: 600; position: sticky; top: 0; }}
  td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--border); }}
  tr:hover td {{ background: rgba(255,255,255,0.03); }}
  .match {{ color: var(--green); font-weight: 600; }}
  .diff {{ color: var(--red); font-weight: 600; }}
  .error {{ color: var(--red); }}
  .null {{ color: var(--muted); font-style: italic; }}
  .mono {{ font-family: 'SF Mono', Menlo, monospace; font-size: 0.8rem; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  .badge.match {{ background: rgba(34,197,94,0.15); color: var(--green); }}
  .badge.diff {{ background: rgba(239,68,68,0.15); color: var(--red); }}
  .badge.known {{ background: rgba(249,115,22,0.15); color: var(--orange); }}
  .badge.error {{ background: rgba(239,68,68,0.15); color: var(--red); }}
  .collapsible {{ cursor: pointer; user-select: none; }}
  .collapsible::before {{ content: "\\25B6"; display: inline-block; margin-right: 0.5rem; font-size: 0.7rem; transition: transform 0.2s; }}
  .collapsible.open::before {{ transform: rotate(90deg); }}
  .detail-section {{ display: none; margin: 0.5rem 0 1.5rem 0; }}
  .detail-section.open {{ display: block; }}
  .only-list {{ columns: 3; column-gap: 2rem; list-style: none; padding: 0; }}
  .only-list li {{ font-family: 'SF Mono', Menlo, monospace; font-size: 0.8rem; padding: 0.15rem 0; break-inside: avoid; }}
  .diff-val {{ background: rgba(239,68,68,0.1); padding: 0.1rem 0.3rem; border-radius: 3px; }}
  .known-val {{ background: rgba(249,115,22,0.1); padding: 0.1rem 0.3rem; border-radius: 3px; }}
  .field-summary {{ margin-bottom: 1rem; padding: 0.8rem; background: rgba(59,130,246,0.05); border-radius: 8px; border: 1px solid var(--border); }}
  .field-summary h4 {{ margin-bottom: 0.5rem; font-size: 0.9rem; }}
  .field-chip {{ display: inline-block; padding: 0.2rem 0.6rem; margin: 0.15rem; border-radius: 4px; font-size: 0.78rem; font-family: 'SF Mono', Menlo, monospace; background: rgba(239,68,68,0.12); color: #fca5a5; }}
  .field-chip .count {{ color: var(--muted); margin-left: 0.3rem; }}
  .annotation {{ background: var(--card); border-left: 3px solid var(--blue); padding: 0.8rem 1rem; margin: 0.8rem 0; border-radius: 0 6px 6px 0; font-size: 0.85rem; }}
  .annotation .verdict {{ font-weight: 600; margin-bottom: 0.3rem; }}
  .annotation .verdict.partial {{ color: var(--green); }}
  .annotation .verdict.cam {{ color: var(--blue); }}
  .annotation .verdict.missing {{ color: var(--yellow); }}
  .known-section {{ background: rgba(249,115,22,0.05); border: 1px solid rgba(249,115,22,0.2); border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
  .known-section h4 {{ color: var(--orange); margin-bottom: 0.5rem; }}
  .known-reason {{ color: var(--muted); font-size: 0.8rem; font-style: italic; }}
</style>
</head>
<body>
<h1>CAM vs Partial Copy Sandbox Audit</h1>
<div class="subtitle">Generated {ts} &mdash; Partial: <code>{PARTIAL}</code> &mdash; CAM: <code>{CAM}</code></div>
"""

    # Rate bar color
    bar_color = "var(--green)" if rate_num >= 98 else "var(--yellow)" if rate_num >= 90 else "var(--red)"

    html += f"""
<div class="rate-bar">
  <div class="track"><div class="fill" style="width:{rate}%;background:{bar_color}"></div></div>
  <div class="rate-label"><span>Match Rate (excludes known diffs)</span><strong>{rate}%</strong></div>
</div>

<div class="cards">
  <div class="card"><div class="num">{len(results)}</div><div class="label">Objects Audited</div></div>
  <div class="card green"><div class="num">{tot_m - tot_d:,}</div><div class="label">Records Identical</div></div>
  <div class="card {"yellow" if tot_d else "green"}"><div class="num">{tot_d:,}</div><div class="label">Real Diffs</div></div>
  <div class="card {"orange" if tot_kn else "green"}"><div class="num">{tot_kn:,}</div><div class="label">Known Diffs</div></div>
  <div class="card {"red" if tot_op + tot_oc else "green"}"><div class="num">{tot_op + tot_oc:,}</div><div class="label">Missing Records</div></div>
  <div class="card"><div class="num">{tot_p:,}</div><div class="label">Partial</div></div>
  <div class="card"><div class="num">{tot_c:,}</div><div class="label">CAM</div></div>
</div>
"""

    # Per-object summary table
    html += """<section><h2>Per-Object Summary</h2>
<table>
<tr><th>Object</th><th>Partial</th><th>CAM</th><th>Matched</th><th>Real Diffs</th><th>Known</th><th>Only-P</th><th>Only-C</th><th>Fields</th><th>Status</th></tr>
"""
    for r in results:
        if "error" in r:
            html += f'<tr><td>{esc(r["name"])}</td><td colspan="8" class="error">{esc(r["error"][:120])}</td><td><span class="badge error">ERROR</span></td></tr>\n'
            continue
        mm = r["mismatched"]
        kn = len(r.get("known_mismatches", []))
        op = len(r["only_partial"])
        oc = len(r["only_cam"])
        has_real = mm or op or oc
        has_known_only = not has_real and kn
        if has_real:
            badge = '<span class="badge diff">DIFF</span>'
        elif has_known_only:
            badge = '<span class="badge known">KNOWN</span>'
        else:
            badge = '<span class="badge match">MATCH</span>'
        html += (
            f"<tr><td><strong>{esc(r['name'])}</strong></td>"
            f"<td>{r['partial_count']:,}</td><td>{r['cam_count']:,}</td>"
            f"<td>{r['matched']:,}</td>"
            f"<td>{'' if not mm else f'<strong class=diff>{mm:,}</strong>'}</td>"
            f"<td>{'' if not kn else f'<span style=color:var(--orange)>{kn:,}</span>'}</td>"
            f"<td>{'' if not op else f'<strong class=diff>{op:,}</strong>'}</td>"
            f"<td>{'' if not oc else f'<strong class=diff>{oc:,}</strong>'}</td>"
            f'<td class="mono">{r["fields_compared"]}</td>'
            f"<td>{badge}</td></tr>\n"
        )

    html += "</table></section>\n"

    # Errors
    if errs:
        html += "<section><h2>Errors</h2>\n"
        for r in errs:
            html += f'<p class="error"><strong>{esc(r["name"])}:</strong> {esc(r["error"])}</p>\n'
        html += "</section>\n"

    # Detailed diffs (real)
    diffs = [r for r in ok if r["mismatched"] or r["only_partial"] or r["only_cam"]]
    if diffs:
        html += "<section><h2>Actionable Differences</h2>\n"
        for idx, r in enumerate(diffs):
            obj_fields = {}
            for m in r.get("mismatches", []):
                for d in m["diffs"]:
                    obj_fields[d["field"]] = obj_fields.get(d["field"], 0) + 1

            html += f'<h3 class="collapsible" onclick="toggle(this, \'detail-{idx}\')">{esc(r["name"])}'
            html += f" &mdash; {r['mismatched']:,} diffs, {len(r['only_partial']):,} only-P, {len(r['only_cam']):,} only-C</h3>\n"
            html += f'<div id="detail-{idx}" class="detail-section">\n'

            # Annotation
            ann = ANNOTATIONS.get(r["name"])
            if ann:
                vc = "partial" if "Partial" in ann["verdict"] else "cam" if "CAM" in ann["verdict"] else "missing"
                html += f'<div class="annotation"><div class="verdict {vc}">{esc(ann["verdict"])}</div>{esc(ann["note"])}</div>\n'

            if obj_fields:
                html += '<div class="field-summary"><h4>Affected Fields</h4>'
                for fname, cnt in sorted(obj_fields.items(), key=lambda x: -x[1]):
                    html += f'<span class="field-chip">{esc(fname)}<span class="count">x{cnt}</span></span>'
                html += "</div>\n"

            if r["only_partial"]:
                html += f'<h4>Only in Partial ({len(r["only_partial"])})</h4><ul class="only-list">'
                for k in r["only_partial"][:50]:
                    html += f"<li>{esc(k)}</li>"
                if len(r["only_partial"]) > 50:
                    html += f"<li>...and {len(r['only_partial']) - 50} more</li>"
                html += "</ul>\n"

            if r["only_cam"]:
                html += f'<h4>Only in CAM ({len(r["only_cam"])})</h4><ul class="only-list">'
                for k in r["only_cam"][:50]:
                    html += f"<li>{esc(k)}</li>"
                if len(r["only_cam"]) > 50:
                    html += f"<li>...and {len(r['only_cam']) - 50} more</li>"
                html += "</ul>\n"

            if r["mismatches"]:
                html += "<table><tr><th>Key</th><th>Field</th><th>Partial</th><th>CAM</th></tr>\n"
                n = 0
                for m in r["mismatches"]:
                    for d in m["diffs"]:
                        pv = (
                            esc(str(d["partial"])[:80])
                            if d["partial"] is not None
                            else '<span class="null">null</span>'
                        )
                        cv = esc(str(d["cam"])[:80]) if d["cam"] is not None else '<span class="null">null</span>'
                        html += (
                            f'<tr><td class="mono">{esc(m["key"][:60])}</td>'
                            f'<td class="mono">{esc(d["field"])}</td>'
                            f'<td class="diff-val">{pv}</td><td class="diff-val">{cv}</td></tr>\n'
                        )
                        n += 1
                        if n >= 300:
                            break
                    if n >= 300:
                        remain = sum(len(x["diffs"]) for x in r["mismatches"]) - n
                        if remain > 0:
                            html += f'<tr><td colspan="4" style="color:var(--muted)">...and {remain:,} more differences</td></tr>\n'
                        break
                html += "</table>\n"
            html += "</div>\n"
        html += "</section>\n"

    # Known diffs section
    known_objs = [r for r in ok if r.get("known_mismatches")]
    if known_objs:
        html += "<section><h2>Known Differences (Not Counted)</h2>\n"
        html += '<p style="color:var(--muted);margin-bottom:1rem">These fields differ for expected reasons — different placeholder users, non-migration fields, etc.</p>\n'
        for r in known_objs:
            reasons = {}
            for m in r["known_mismatches"]:
                for d in m["diffs"]:
                    reason = d.get("known_reason", "")
                    key = (d["field"], reason)
                    reasons[key] = reasons.get(key, 0) + 1
            html += (
                f'<div class="known-section"><h4>{esc(r["name"])} &mdash; {len(r["known_mismatches"]):,} records</h4>\n'
            )
            html += "<table><tr><th>Field</th><th>Records</th><th>Reason</th></tr>\n"
            for (field, reason), cnt in sorted(reasons.items(), key=lambda x: -x[1]):
                html += f'<tr><td class="mono">{esc(field)}</td><td>{cnt:,}</td><td class="known-reason">{esc(reason)}</td></tr>\n'
            html += "</table></div>\n"
        html += "</section>\n"

    # Clean objects
    clean = [
        r
        for r in ok
        if not r["mismatched"] and not r["only_partial"] and not r["only_cam"] and not r.get("known_mismatches")
    ]
    if clean:
        html += "<section><h2>Clean Objects (100% Match)</h2><table>\n"
        html += "<tr><th>Object</th><th>Records</th><th>Fields Compared</th><th>Formula Fields Skipped</th></tr>\n"
        for r in clean:
            html += (
                f'<tr><td class="match"><strong>{esc(r["name"])}</strong></td>'
                f"<td>{r['matched']:,}</td><td>{r['fields_compared']}</td>"
                f"<td>{r['formula_count']}</td></tr>\n"
            )
        html += "</table></section>\n"

    html += """
<script>
function toggle(el, id) {
  el.classList.toggle('open');
  document.getElementById(id).classList.toggle('open');
}
// Auto-expand first diff section
document.addEventListener('DOMContentLoaded', () => {
  const first = document.querySelector('.collapsible');
  if (first) { first.click(); }
});
</script>
</body></html>"""

    with open(path, "w") as f:
        f.write(html)


def main():
    print("=" * 60)
    print("  CAM vs Partial Copy Sandbox Audit")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    for obj in OBJECTS:
        try:
            results.append(audit_object(obj))
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            results.append({"name": obj["name"], "error": str(e)})

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare_sandboxes_report.html")
    write_report(results, out)

    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    for r in results:
        if "error" in r:
            print(f"  {r['name']:30s} ERROR")
        else:
            s = "MATCH" if not r["mismatched"] and not r["only_partial"] and not r["only_cam"] else "DIFF"
            print(
                f"  {r['name']:30s} {s:6s}  "
                f"P={r['partial_count']:>6,}  C={r['cam_count']:>6,}  "
                f"eq={r['matched'] - r['mismatched']:>6,}  "
                f"diff={r['mismatched']:>4,}  "
                f"+P={len(r['only_partial']):>3,}  +C={len(r['only_cam']):>3,}"
            )
    print(f"\nReport: {out}")


if __name__ == "__main__":
    main()
