# VIP SRS — Supplier Reporting System Knowledge Base

Vermont Information Processing (VIP) Supplier Reporting System — the beverage industry standard for distributor-to-supplier data exchange.

**Source:** ISV Interface File Specifications v6.0 (January 2023)
**Contact:** SRS_SPEC_SUPPORT@vipinfo.com

## File Type Index

VIP delivers up to 22 file types. Files are gzipped CSVs delivered daily via SFTP.

### Master Data (load first)

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 1 | VAL | [Valid Values](file-types/SRSVALUE.md) | Code/enum lookup table for all coded fields | Yes (as transform reference) |
| 2 | DIST | [Distributor Master](file-types/DISTDA.md) | Distributor locations, contacts, hierarchy | Yes → Location__c |
| 3 | ITM2 | [Supplier Item Master](file-types/ITM2DA.md) | Supplier's product catalog (66 columns) | Yes → Item__c, Item_Line__c, Item_Type__c |
| 4 | CHN | [Chain](file-types/SRSCHAIN.md) | Retail chain reference (Publix, Walmart, etc.) | Yes → Account (Chain Banner) |

### Distributor-Reported Master Data

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 5 | OUT | [Retail Outlets](file-types/OUTDA.md) | Outlet accounts with demographics (71 columns) | Yes → Account, Contact |
| 6 | VIPOUT | [VIP Outlet Master](file-types/VIPOUT.md) | VIP's own outlet database (75+ fields) | No — reference only |

### Distributor-Reported Transaction Data

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 7 | SLS | [Sales](file-types/SLSDA.md) | Invoice-level sales transactions | Yes → Depletion__c, Placement__c |
| 8 | SLSLITE | [Sales Lite](file-types/SLSLITE.md) | Simplified sales summary (new Nov 2024) | No — reference only |
| 9 | ORD | [Future Sales/Orders](file-types/ORD.md) | Pre-sold orders | No — reference only |
| 10 | INV | [Inventory](file-types/INVDA.md) | Inventory transactions (positions + movements) | Yes → Inventory__c, History, Adjustment |

### Summarized Transaction Data

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 11 | DEPL | [Summary Depletions](file-types/DEPL.md) | Monthly summarized depletions by dist/item | No — reference only |

### Distributor-Reported Reference Data

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 12 | ITM/DIC | [Dist Item Cross-Ref](file-types/DIC.md) | Distributor-to-supplier item mapping | Yes (as ITMDA) → Item__c enrichment |
| 13 | SLM | [Dist Salesperson](file-types/SLM.md) | Sales rep records with org hierarchy | No — reference only |

### Processing Control

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 14 | CAL | [Calendar](file-types/CAL.md) | Distributor trading days + exceptions | No — reference only |
| 15 | NON | [Non-Reporters](file-types/NON.md) | Missing data tracking with rank | No — reference only |
| 16 | CTL | [Sales Control](file-types/CTL.md) | Sales balancing/control file | Yes (as CTLDA) → Allocation__c |
| 17 | CTLS | [Depletion Control](file-types/CTLS.md) | Depletion balancing/control file | No — reference only |

### Additional Files (Supplier-to-VIP)

| # | Prefix | File Type | Description | Integrated? |
|---|--------|-----------|-------------|-------------|
| 18 | -- | Distributor Discount | Discount definitions | No |
| 19 | -- | Retroactive Discount | Cumulative discount adjustments | No |

## Reference Documents

| Document | Description |
|----------|-------------|
| [ISV Spec Overview](isv-spec-overview.md) | How to read any VIP file — format, naming, record structure |
| [Valid Values](valid-values.md) | Complete coded field value reference (Appendix B) |
| [Repack Logic](appendices/repack-logic.md) | Case/bottle conversion rules (Appendix E) |
| [Zero Sales Records](appendices/zero-sales-records.md) | When zero sales records are created (Appendix F) |
| [Summary Inventory](appendices/summary-inventory.md) | Monthly summary vs daily transaction (Appendix G) |
| [Depletion Warehouse](appendices/depletion-warehouse.md) | Multi-warehouse attribution (Appendix H) |
| [Retroactive Discounts](appendices/retroactive-discounts.md) | Reverse/rebill patterns (Appendix J) |

## Integration Reference

The Ohanafy-specific integration (field mappings, crosswalks, external IDs, Tray.io pipeline) lives at:
- `integrations/vip-srs/docs/VIP_AGENT_HANDOFF.md` — THE source of truth for VIP-to-Ohanafy mapping
- `integrations/vip-srs/CLAUDE.md` — Technical implementation context
- `integrations/vip-srs/ROADMAP.md` — Project history and decisions

## Processing Sequence

Files must be loaded in this order (dependencies flow downward):

```
1. VAL     — Valid Values (reference data for all other files)
2. DIST    — Distributor Master
3. ITM2    — Supplier Item Master
4. CHN     — Chain Reference
5. OUT     — Retail Outlets (references DIST, CHN, VAL)
6. SLS     — Sales (references DIST, OUT, ITM2)
7. ORD     — Future Sales/Orders (references DIST, OUT, ITM2)
8. INV     — Inventory (references DIST, ITM2)
9. DEPL    — Summary Depletions (references DIST, ITM2)
10. DIC    — Distributor Item Cross-Reference (references DIST, ITM2)
11. SLM    — Distributor Salesperson (references DIST)
12. CAL    — Calendar (references DIST)
13. NON    — Non-Reporters (references DIST)
14. CTL    — Sales Control (references DIST, ITM2)
15. CTLS   — Depletions Control (references DIST, ITM2)
```
