# Gulf Distributing

## Overview

- **Industry:** Beverage distribution
- **Region:** Gulf Coast (Alabama)
- **Ohanafy SKUs:** OMS, WMS, REX, Payments, EDI, Configure, Platform, Core, Data Model
- **Key contacts:** <!-- fill in as needed -->

## Org Topology

| Environment | Alias | Org ID | Type | Status |
|-------------|-------|--------|------|--------|
| Production  | gulf-production | 00Dal00001PWc3REAT | customer | Connected |
| CAM Sandbox | gulf-cam-sandbox | 00DWE00000ND1r02AD | sandbox | Connected |
| Partial Copy | ohanafy-sandbox | 00DWE00000Mbk0q2AB | sandbox | Token expired |

## Data Profile

- **Accounts:** <!-- fill after querying -->
- **Items/Products:** ~8,743 (from VIP migration)
- **Brands:** ~927 (from VIP migration)
- **Orders/month:** <!-- fill after querying -->
- **Warehouses/Locations:** <!-- fill after querying -->

## External Systems

| System | Purpose | Integration Method |
|--------|---------|-------------------|
| VIP (DB2/AS400) | Legacy ERP (migrating from) | Azure Postgres staging DB |
| GP Analytics | Placements, depletions | Tray.io integration |

## Migration History

Gulf is migrating from VIP (AS400/DB2) to Ohanafy.
- Migration playbook: `scripts/migrations/vip-to-ohanafy/vip-to-ohanafy-playbook.md`
- Data workbook: Google Sheets `108Eyx2n16FzOilD7Kaze1YTKF_NQBDYoHsb3svlDeWE`
- VIP staging DB: `gulfstream-db2-data.postgres.database.azure.com:5432`
- Case study docs: `docs/case-studies/gulf-vip-to-ohanafy/`
