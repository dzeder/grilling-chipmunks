#!/usr/bin/env python3
"""
Step 3: Retrieve a GlobalValueSet via Metadata API and parse XML → JSON array.

Creates a temp sfdx project in /tmp/ohfy-uom-retrieve/, retrieves the
GlobalValueSet metadata, and parses it into a JSON array of picklist values.

Usage:
  python3 sfdx_retrieve_globalvalueset.py --target-org <alias> --value-set-name <name>
  python3 sfdx_retrieve_globalvalueset.py --target-org <alias> --value-set-name <name> --output /tmp/uom-values.json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

TEMP_PROJECT_DIR = "/tmp/ohfy-uom-retrieve"
SFDX_PROJECT_JSON = {
    "packageDirectories": [{"path": "force-app", "default": True}],
    "namespace": "",
    "sfdcLoginUrl": "https://login.salesforce.com",
    "sourceApiVersion": "59.0"
}


def run_sf(args, error_label="sf command", cwd=None):
    cmd = ["sf"] + args + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=cwd)
    except FileNotFoundError:
        print(json.dumps({"error": "sf CLI not found"}))
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(json.dumps({"error": f"{error_label} timed out after 120s"}))
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "non-JSON output", "raw": result.stdout, "stderr": result.stderr}


def setup_temp_project():
    """Create minimal sfdx project in temp directory."""
    os.makedirs(TEMP_PROJECT_DIR, exist_ok=True)
    project_file = os.path.join(TEMP_PROJECT_DIR, "sfdx-project.json")
    with open(project_file, "w") as f:
        json.dump(SFDX_PROJECT_JSON, f, indent=2)
    # Create force-app directory
    os.makedirs(os.path.join(TEMP_PROJECT_DIR, "force-app"), exist_ok=True)
    return TEMP_PROJECT_DIR


def retrieve_global_value_set(target_org, value_set_name, project_dir):
    """Retrieve GlobalValueSet metadata using sf project retrieve start."""
    return run_sf(
        [
            "project", "retrieve", "start",
            "--metadata", f"GlobalValueSet:{value_set_name}",
            "--target-org", target_org,
            "--output-dir", os.path.join(project_dir, "force-app")
        ],
        f"retrieve GlobalValueSet:{value_set_name}",
        cwd=project_dir
    )


def find_xml_file(project_dir, value_set_name):
    """Locate the retrieved XML file."""
    # sf CLI retrieves to force-app/main/default/globalValueSets/
    candidates = [
        os.path.join(project_dir, "force-app", "main", "default", "globalValueSets", f"{value_set_name}.globalValueSet-meta.xml"),
        os.path.join(project_dir, "force-app", f"{value_set_name}.globalValueSet-meta.xml"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path

    # Walk to find it
    for root, _, files in os.walk(project_dir):
        for fname in files:
            if fname.endswith(".globalValueSet-meta.xml"):
                return os.path.join(root, fname)
    return None


def parse_global_value_set_xml(xml_path):
    """Parse GlobalValueSet XML → list of {value, label, isActive, isDefault}."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle namespace
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    values = []
    for cv in root.findall(f"{ns}customValue"):
        full_name = cv.find(f"{ns}fullName")
        label = cv.find(f"{ns}label")
        is_active = cv.find(f"{ns}isActive")
        is_default = cv.find(f"{ns}default")

        values.append({
            "value": full_name.text if full_name is not None else None,
            "label": label.text if label is not None else (full_name.text if full_name is not None else None),
            "isActive": (is_active.text or "").lower() == "true" if is_active is not None else True,
            "isDefault": (is_default.text or "").lower() == "true" if is_default is not None else False,
        })
    return values


def main():
    parser = argparse.ArgumentParser(description="Retrieve GlobalValueSet and parse to JSON")
    parser.add_argument("--target-org", required=True, help="Org alias or username")
    parser.add_argument("--value-set-name", required=True, help="GlobalValueSet API name (e.g. ohfy__UOM)")
    parser.add_argument("--output", help="Write JSON output to file (default: stdout only)")
    args = parser.parse_args()

    project_dir = setup_temp_project()

    retrieve_result = retrieve_global_value_set(args.target_org, args.value_set_name, project_dir)
    if retrieve_result.get("status") == 1 or "error" in retrieve_result:
        print(json.dumps({
            "status": "error",
            "message": retrieve_result.get("message", "Retrieve failed"),
            "detail": retrieve_result
        }, indent=2))
        sys.exit(1)

    xml_path = find_xml_file(project_dir, args.value_set_name)
    if not xml_path:
        print(json.dumps({
            "status": "error",
            "message": f"Could not find retrieved XML for {args.value_set_name}",
            "project_dir": project_dir
        }, indent=2))
        sys.exit(1)

    try:
        values = parse_global_value_set_xml(xml_path)
    except ET.ParseError as e:
        print(json.dumps({"status": "error", "message": f"XML parse error: {e}", "xml_path": xml_path}, indent=2))
        sys.exit(1)

    active_values = [v["value"] for v in values if v.get("isActive")]
    output = {
        "status": "ok",
        "value_set_name": args.value_set_name,
        "xml_path": xml_path,
        "total_count": len(values),
        "active_count": len(active_values),
        "active_values": active_values,
        "all_values": values
    }

    print(json.dumps(output, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n# Written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
