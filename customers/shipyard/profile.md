# Shipyard Brewing Company

## Overview

- **Industry:** Beverage manufacturing (supplier/brewery)
- **Region:** Portland, Maine
- **Role:** Supplier — uses VIP SRS to receive sales/inventory data from distributors
- **Ohanafy SKUs:** TBD (pending sandbox connection)
- **Go-live date:** TBD
- **Key contacts:** TBD
- **Account tier:** TBD

## Org Topology

| Environment | Alias | Org ID | Type | Status |
|-------------|-------|--------|------|--------|
| Sandbox     | shipyard-sandbox | TBD | sandbox | Pending connection |

## Installed Packages

<!-- Populated automatically by connect-org.sh -->

| Package | Namespace | Version | Status |
|---------|-----------|---------|--------|
|         |           |         |        |

## Data Profile

Based on VIP SRS sample data (11 business days, supplier code `ARG`):

- **Supplier Items (ITM2DA):** ~65 SKUs
- **Distributors (DISTDA):** ~13 distributors
- **Distributor-Item Mappings (ITMDA):** ~102
- **Outlets/Accounts (OUTDA):** ~36,587 (all distributors; filtered per org)
- **Sales/Invoice Lines (SLSDA):** ~110/day
- **Inventory Transactions (INVDA):** ~656/day
- **Allocations (CTLDA):** ~24
- **Chain Banners (SRSCHAIN):** ~6,633
- **Custom objects (non-OHFY):** TBD (pending sandbox connection)

## External Systems

| System | Purpose | Integration Method | Status |
|--------|---------|-------------------|--------|
| VIP SRS | Daily sales/inventory/account data from distributors | SFTP → Tray.io → SF | Building |

## Customization Delta

### Custom Fields

See `customizations.md` for VIP-specific fields added to support the SRS integration.

### Custom Validation Rules
<!-- TBD after sandbox connection -->

### Custom Flows
<!-- TBD after sandbox connection -->

### Picklist Customizations
<!-- Market picklist values may need additions — see integrations/vip-srs/ docs -->

## Deployment History

| Date | What | Branch/PR | Notes |
|------|------|-----------|-------|
|      |      |           |       |

## Migration History

- **Source system:** VIP SRS (daily file delivery, not a one-time migration)
- **Migration status:** Building integration pipeline
- **Key artifacts:** `integrations/vip-srs/`, `.context/attachments/VIP_AGENT_HANDOFF.md`
