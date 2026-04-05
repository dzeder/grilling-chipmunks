#!/usr/bin/env python3
"""
Step 1: Connect to Salesforce Org via sf CLI.

Verifies sf CLI is installed, lists available orgs, and displays details
for the target org so the user can confirm before proceeding.

Usage:
  python3 sfdx_connect.py --target-org <alias>
  python3 sfdx_connect.py --list-orgs
"""

import argparse
import json
import subprocess
import sys


def run_sf(args, error_label="sf command"):
    """Run an sf CLI command, return parsed JSON output."""
    cmd = ["sf"] + args + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        print(json.dumps({"error": "sf CLI not found. Install with: npm install -g @salesforce/cli"}))
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(json.dumps({"error": f"{error_label} timed out after 30s"}))
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"{error_label} returned non-JSON", "raw": result.stdout, "stderr": result.stderr}


def verify_sf_cli():
    """Check sf CLI version is available."""
    try:
        result = subprocess.run(["sf", "version", "--json"], capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        return data
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return None


def list_orgs():
    """List all authenticated orgs."""
    return run_sf(["org", "list"], "org list")


def display_org(target_org):
    """Show details for a specific org."""
    return run_sf(["org", "display", "--target-org", target_org], "org display")


def main():
    parser = argparse.ArgumentParser(description="Verify sf CLI and confirm target Salesforce org")
    parser.add_argument("--target-org", help="Org alias or username to verify")
    parser.add_argument("--list-orgs", action="store_true", help="List all authenticated orgs and exit")
    args = parser.parse_args()

    # Step 1: verify sf CLI
    version_info = verify_sf_cli()
    if not version_info:
        print(json.dumps({
            "status": "error",
            "message": "sf CLI not found or not working. Install with: npm install -g @salesforce/cli"
        }))
        sys.exit(1)

    if args.list_orgs or not args.target_org:
        orgs = list_orgs()
        print(json.dumps({
            "status": "ok",
            "sf_version": version_info.get("result", {}).get("sfdxVersion", "unknown"),
            "orgs": orgs.get("result", orgs)
        }, indent=2))
        return

    # Display target org details
    org_info = display_org(args.target_org)
    if org_info.get("status") == 1 or "error" in org_info:
        print(json.dumps({
            "status": "error",
            "target_org": args.target_org,
            "message": org_info.get("message", "Org not found or not authenticated"),
            "detail": org_info
        }, indent=2))
        sys.exit(1)

    result = org_info.get("result", {})
    print(json.dumps({
        "status": "ok",
        "sf_version": version_info.get("result", {}).get("sfdxVersion", "unknown"),
        "target_org": args.target_org,
        "alias": result.get("alias"),
        "username": result.get("username"),
        "instanceUrl": result.get("instanceUrl"),
        "orgId": result.get("id"),
        "isDevHub": result.get("isDevHub", False),
        "isScratchOrg": result.get("isScratchOrg", False),
        "connectedStatus": result.get("connectedStatus"),
        "expirationDate": result.get("expirationDate")
    }, indent=2))


if __name__ == "__main__":
    main()
