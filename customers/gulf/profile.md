# Gulf Distributing

## Overview

- **Industry:** Beverage distribution
- **Region:** Gulf Coast (Alabama)
- **Ohanafy SKUs:** OMS, WMS, REX, Payments, EDI, Configure, Platform, Core, Data Model
- **Go-live date:** <!-- fill when known -->
- **Key contacts:** <!-- fill as needed -->
- **Account tier:** Enterprise

## Org Topology

| Environment | Alias | Org ID | Type | Status |
|-------------|-------|--------|------|--------|
| Production  | gulf-production | 00Dal00001PWc3REAT | customer | Connected |
| CAM Sandbox | gulf-cam-sandbox | 00DWE00000ND1r02AD | sandbox | Connected |
| Partial Copy | ohanafy-sandbox | 00DWE00000Mbk0q2AB | sandbox | Token expired |

## Installed Packages

<!-- Populated automatically by connect-org.sh -->

| Package | Namespace | Version | Status |
|---------|-----------|---------|--------|
| OHFY-Core | ohfy | <!-- query --> | Active |
| OHFY-OMS | ohfy | <!-- query --> | Active |
| OHFY-WMS | ohfy | <!-- query --> | Active |
| OHFY-REX | ohfy | <!-- query --> | Active |
| OHFY-Payments | ohfy | <!-- query --> | Active |
| OHFY-EDI | ohfy | <!-- query --> | Active |
| OHFY-Configure | ohfy | <!-- query --> | Active |
| OHFY-Platform | ohfy | <!-- query --> | Active |
| OHFY-Data_Model | ohfy | <!-- query --> | Active |

## Data Profile

- **Accounts:** <!-- fill after querying -->
- **Items/Products:** ~8,743 (from VIP migration)
- **Brands:** ~927 (from VIP migration)
- **Orders/month:** <!-- fill after querying -->
- **Warehouses/Locations:** <!-- fill after querying -->
- **Custom objects (non-OHFY):** <!-- fill after querying -->

## External Systems

| System | Purpose | Integration Method | Status |
|--------|---------|-------------------|--------|
| VIP (DB2/AS400) | Legacy ERP (migrating from) | Azure Postgres staging DB | Active migration |
| GP Analytics | Placements, depletions | Tray.io integration | Active |

## Customization Delta

### Custom Fields
<!-- Fields added beyond the standard OHFY package — populate from org snapshot -->

### Custom Validation Rules
<!-- Validation rules specific to Gulf — populate from org snapshot -->

### Custom Flows
<!-- Flows specific to Gulf's business logic — populate from org snapshot -->

### Picklist Customizations
<!-- Non-standard picklist values — populate from org snapshot -->

## Deployment History

| Date | What | Branch/PR | Notes |
|------|------|-----------|-------|
|      |      |           |       |

## Migration History

Gulf is migrating from VIP (AS400/DB2) to Ohanafy.

- **Source system:** VIP (DB2/AS400)
- **Migration status:** In progress
- **Key artifacts:**
  - Migration playbook: `scripts/migrations/vip-to-ohanafy/vip-to-ohanafy-playbook.md`
  - Data workbook: Google Sheets `108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE`
  - VIP staging DB: `gulfstream-db2-data.postgres.database.azure.com:5432`
  - Case study docs: `docs/case-studies/gulf-vip-to-ohanafy/`
