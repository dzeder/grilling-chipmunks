# VIP SRS Integration

Daily automated pipeline that ingests 9 VIP beverage distribution data files, transforms them to the Ohanafy data model, and loads them into Salesforce via Tray.io.

## Architecture

```
SFTP (9 .gz files daily)
  → Tray.io Orchestrator
    → Phase 1: Reference Data (parallel)
        01-srschain → Account (Chain Banners)
        02-itm2da   → Item_Line__c + Item_Type__c + Item__c
        03-distda   → Location__c
    → Phase 2: Enrichment (parallel)
        04-itmda    → Item__c (distributor SKU enrichment)
        05-outda    → Account (Outlets) + Contact (Buyers)
    → Phase 3: Inventory
        06-invda    → Inventory__c + History + Adjustments
    → Phase 4: Transactions (parallel)
        07-slsda    → Depletion__c
        08-ctlda    → Allocation__c
    → Cleanup
        09-cleanup  → Stale record deletion
        10-summary  → Daily run summary
```

## Source Files

| File | Description | Rows/Day | Target Objects |
|------|-------------|----------|---------------|
| SRSCHAIN | Chain/account groups | ~6,633 | Account (Chain Banner) |
| SRSVALUE | Code/enum lookups | ~177 | _(reference only)_ |
| ITM2DA | Supplier item master | ~65 | Item_Line__c, Item_Type__c, Item__c |
| DISTDA | Distributor master | ~13 | Location__c |
| ITMDA | Distributor-item mapping | ~102 | Item__c (enrichment) |
| OUTDA | Outlet/account universe | ~36,587 | Account (Outlets), Contact (Buyers) |
| SLSDA | Sales/depletion lines | ~110 | Depletion__c |
| INVDA | Inventory transactions | ~656 | Inventory__c, History__c, Adjustment__c |
| CTLDA | Supplier allocations | ~24 | Allocation__c |

## Directory Structure

```
integrations/vip-srs/
  config/
    shipyard.json          # Per-customer config (dist ID, supplier ID)
  shared/
    constants.js           # Prefixes, crosswalks, trans codes
    external-ids.js        # Key generators
    filters.js             # Row filtering
    transforms.js          # Date/phone/string transforms
  scripts/
    01-srschain-chains.js  # → Account (Chain Banners)
    02-itm2da-items.js     # → Item_Line + Item_Type + Item
    03-distda-locations.js # → Location
    04-itmda-enrichment.js # → Item (enrichment)
    05-outda-accounts.js   # → Account (Outlets) + Contact
    06-invda-inventory.js  # → Inventory + History + Adjustments
    07-slsda-depletions.js # → Depletion
    08-ctlda-allocations.js# → Allocation
    09-cleanup-stale.js    # Stale record deletion
    10-run-summary.js      # Daily run summary
  tests/
    fixtures/              # Sample data from yangon workspace
  docs/
    VIP_AGENT_HANDOFF.md   # Complete spec
```

## External ID Strategy

Keys use only immutable business identifiers. Colon-delimited, prefixed, deterministic.

| Object | Prefix | Example |
|--------|--------|---------|
| Account (Chain) | CHN | `CHN:0000010305` |
| Account (Outlet) | ACT | `ACT:FL01:00015` |
| Contact | CON | `CON:FL01:00015` |
| Item__c | ITM | `ITM:102312102` |
| Location__c | LOC | `LOC:FL01` |
| Depletion__c | DEP | `DEP:FL01:0699528:21159:102312102:C` |
| Inventory__c | IVT | `IVT:FL01:102312102` |
| Inventory_History__c | IVH | `IVH:FL01:102312102:20260403:C` |
| Inventory_Adjustment__c | IVA | `IVA:FL01:102312102:20:20260403:C` |
| Allocation__c | ALC | `ALC:FL01:102312102:202604:C` |

## Customers

| Customer | Supplier Code | Config |
|----------|--------------|--------|
| Shipyard Brewing | ARG | `config/shipyard.json` |

## Spec

Full specification: `.context/attachments/VIP_AGENT_HANDOFF.md`
