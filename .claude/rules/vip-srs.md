# VIP SRS Integration Rules

## Context Loading

When working on VIP SRS tasks, load these files in order:
1. `integrations/vip-srs/CLAUDE.md` — implementation context
2. `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md` — field mappings (source of truth)
3. `customers/shipyard/known-issues.md` — active blockers and workarounds
4. `integrations/vip-srs/ROADMAP.md` — completion status and gotchas (19 documented)

## Active Blockers (ROS2)

These affect EVERY data load until Ohanafy engineering fixes the managed package:

1. **AccountTriggerMethods missing** — Account updates fail. Contact inserts also fail (cascade: Contact AfterInsert → Account update → missing class). Workaround: purge before loading so all DML is INSERT, not UPDATE. Contacts have NO workaround.

2. **Item lookup filter chain on Depletion__c.Item__c** — Items need 5 prerequisites before depletions can load. Script 02 sets 4 of 5. The 5th (Transformation_Setting__c record) must exist in the org. Always verify before Phase 4.

3. **Stock_UOM_Sub_Type__c validation** — Setting Packaging_Type__c on Finished Goods requires Stock_UOM_Sub_Type__c. Affects Script 04 (item enrichment). Accept 1 failure or map the field.

## Data Load Procedure

Always follow this sequence:
1. `sf org display --target-org <alias>` — verify auth
2. `bash purge-vip-data.sh --dist-id <ID> --include-references` — dry-run first
3. `bash purge-vip-data.sh --dist-id <ID> --include-references --execute` — clean slate
4. Verify Transformation_Setting__c: `SELECT Id FROM ohfy__Transformation_Setting__c WHERE ohfy__UOM__c = 'Each'`
5. `node e2e-sandbox-runner.js --dist-id <ID> --file-date <YYYY-MM-DD>` — run pipeline
6. SOQL count queries for all 14 object types to verify

## Pipeline Phase Order (must be sequential)

- Phase 1 (Reference): 01-srschain, 02-itm2da, 03-distda — no interdependencies
- Phase 2 (Enrichment): 04-itmda, 05-outda — depends on Phase 1 items + chains
- Phase 3 (Inventory): 06-invda — depends on Phase 1 items + locations; pre-query runs lazily
- Phase 4 (Transactions): 07-slsda, 07b-slsda, 08-ctlda — depends on items + accounts

## Key Gotchas

- **VIP_File_Date__c = date of pipeline run**, not from file contents. FromDate/ToDate are the reporting window.
- **Placement__c is `ohfy__Placement__c`** (managed, 59+ fields). NOT `Distributor_Placement__c` (stale ref in older docs).
- **VIP SLSDA = depletions** (Depletion__c + Placement__c). NOT Invoice__c (that's supplier→distributor billing).
- **Master-detail fields are create-only** on Placement__c, Inventory__c, Depletion__c. Use `__r` relationship syntax. On update, strip these from the PATCH body.
- **Inventory pre-query must run AFTER Phase 1** — Items don't have VIP_External_ID__c until Phase 1 stamps them.
- **Location_Code__c max 5 chars** — Store raw dist ID (FL01), not prefixed key (LOC:FL01).
- **Restricted picklists need exact org values** — Market__c, Packaging_Type__c, Premise_Type__c. Describe the field first.
- **External ID field names vary by object** — Account uses `ohfy__External_ID__c` (managed), Contact uses `External_ID__c` (unmanaged), most VIP objects use `VIP_External_ID__c`.

## Artifact Routing

- Scripts, shared modules, knowledge → this repo (`integrations/vip-srs/`)
- Tray exports, SF deploy packages → `dzeder/daniels-ohanafy-artifacts`
- Never commit built Tray JSON to this repo
