----
# ohfy-transformation-settings Skill
## 2026-03-16
### Added
- `scripts/sfdx_connect.py` — Step 1: verify sf CLI, list orgs, confirm target org via `sf org display`
- `scripts/sfdx_describe_object.py` — Step 2: describe `ohfy__Transformation_Setting__c`, auto-discover GlobalValueSet name from `ohfy__UOM__c` field metadata
- `scripts/sfdx_retrieve_globalvalueset.py` — Step 3: retrieve GlobalValueSet via Metadata API using temp sfdx project in `/tmp/ohfy-uom-retrieve/`, parse XML → JSON
- `scripts/generate_net_new_uom.py` — Step 5: compute net-new UOM picklist values vs existing GlobalValueSet
- `scripts/sfdx_query_existing.py` — Step 6: SOQL query existing `ohfy__Transformation_Setting__c` records, output existing keys for delta
- `scripts/compute_delta.py` — Step 7: compare expected records vs existing using unified key format, output `net_new` / `existing_matched` / `existing_mismatched`
- `references/sfdx-commands.md` — reference doc for all `sf` CLI commands used in workflow

### Changed
- `SKILL.md` — complete rewrite from static offline generator to 9-step SFDX-connected interactive workflow with user confirmation gates
- `scripts/generate_transformation_settings.py` — replaced v1/v2 key format variants with unified key format; added `--existing-keys` and `--existing-keys-file` flags to exclude already-existing records (net-new only output)

### Notes
- Unified key format: Volume = `Fluid Ounce(s){UOM}`, Weight = `Weight{SubType}{UOM}Pound(s)`
- All scripts use `subprocess` + `sf` CLI with `--json`, `argparse`, Python stdlib only
- `compute_delta.py` imports CONVERSIONS from `generate_transformation_settings.py` directly
----
