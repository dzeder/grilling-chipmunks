---
title: "UFF → X12 810 Translation Mapping"
last_updated: "2026-04-23"
relevant_skills: [ohfy-edi-expert, tray-expert, edi-processing-specialist]
---

# UFF → X12 810 Translation Mapping

When OpenText's translator (or a downstream trading partner) rejects a UFF file, the error often references **X12 810 segment names** (BIG, N1, IT1, TDS) rather than UFF field names. Understanding how UFF positions map to X12 segments is critical for reading those errors.

The distributor sends UFF. OpenText (formerly GXS) translates UFF → X12 810 for retailers who consume X12. Rejections can come from either layer:

- **OpenText translator rejects** — the UFF-to-X12 mapping failed (missing mandatory X12 element). Error surfaces as an X12 segment/element reference.
- **Retailer rejects** — the X12 that OpenText sent was structurally valid but failed the retailer's application rules (wrong store #, duplicate invoice, price mismatch vs. PO, etc.).

## Envelope translation

UFF has no envelope — OpenText synthesizes ISA/GS/IEA/GE wrappers from its partner configuration:

| X12 Segment | Source |
|---|---|
| `ISA` — Interchange Control Header | OpenText partner config (sender/receiver IDs, interchange #) |
| `GS` — Functional Group Header | OpenText config (functional ID = `IN` for invoices) |
| `ST*810` — Transaction Set Header | One per UFF header record |
| `SE` — Transaction Set Trailer | Generated at end of each transaction |
| `GE` / `IEA` | Generated at end of functional group / interchange |

## UFF Header (10) → X12 BIG + N1 loops + ITD

| X12 Element | X12 Ref | UFF Position | UFF Field |
|---|---|---|---|
| `BIG01` | DE 373 (Date) | 121–128 | Invoice Date |
| `BIG02` | DE 76 (Reference ID) | **77–98** | **Invoice Number** |
| `BIG03` | DE 373 (Date) | 129–136 | Purchase Order Date |
| `BIG04` | DE 324 (Reference ID) | 99–120 | Purchase Order Number |
| `BIG07` | DE 640 (Transaction Type) | 145–146 | DR / CR → `DI` / `CN` or partner-specific |
| `N1*BY` loop | — | Customer section (800–1106) | Bill-to (buyer) |
| `N1*ST` loop | — | Outlet section (581–799) | Ship-to (outlet) |
| `N1*RI` loop | — | Distributor section (209–580) | Remit-to (distributor/seller) |
| `N1*VN` loop | — | Distributor Vendor ID (209–228) | Vendor N1/VN |
| `REF*IA` | — | Distributor AP Number (551–560) | Vendor AP reference |
| `REF*VR` / `REF*DP` | — | Outlet Account Number (614–633) | Customer-assigned account |
| `ITD01-ITD14` | — | Terms section (1107–1207) | Payment terms |
| `DTM*011` | — | Delivery Date (137–144) | Shipment/delivery date |

## UFF Detail (20) → X12 IT1 loop + TXI/SAC

| X12 Element | X12 Ref | UFF Position | UFF Field |
|---|---|---|---|
| `IT101` | — | (line counter) | Assigned Identification (line number) |
| `IT102` | DE 380 (Quantity) | 176–184 | Quantity Shipped |
| `IT103` | DE 355 (UOM) | 185–186 | Shipped Unit of Measure |
| `IT104` | DE 212 (Unit Price) | 138–146 | Net Unit Price |
| `IT106` | DE 235 (Product ID Qualifier) | — | `UK` (GTIN-14) or `UP` (UPC-12) |
| `IT107` | DE 234 (Product ID) | 247–260 / 261–274 | UPC Case or Pack (retailer-dependent) |
| `IT108` | DE 235 | — | `VN` or `IN` (Vendor or Buyer part) |
| `IT109` | DE 234 | 331–350 | Distributor Item Number |
| `PID*F` | — | 399–458 | Product Description |
| `PO4` | — | 371–376, 377–382 | Packs per Case, Units per Pack |
| `TXI` loop (state) | — | 75–83 | State Tax per unit |
| `TXI` loop (county) | — | 84–92 | County Tax per unit |
| `TXI` loop (city) | — | 93–101 | City Tax per unit |
| `SAC` (deposit) | — | 12–20 | Deposit Amount |
| `SAC` (freight) | — | 120–128 | Freight Charge |
| `SAC` (promo) | — | 129–137 | Promotional Discount |

## UFF Summary (30) → X12 TDS + CAD + CTT

| X12 Element | UFF Position | UFF Field |
|---|---|---|
| `TDS01` (Total Invoice Amount) | 3–11 | Net Invoice Total |
| `CAD` (Carrier Detail) | (composite) | Delivery route/truck from header |
| `SAC` summary allowances | 124–132, 169–177, 178–186 | Grand Total Charges, Delivery, Freight |
| `TXI` summary taxes | 133–141, 142–150, 151–159, 160–168 | State/County/City/Grand Total Tax |
| `CTT01` (Number of Line Items) | 196–198 | Total Number of Detail Lines |

## How to read a rejection error

OpenText rejection messages typically look like:

> **Tag in Error: BIG — ~BIG_01_373**

Decode:
- `BIG` — the X12 segment where validation failed.
- `BIG_01` — the element position within that segment (1 = first element).
- `373` — an X12 data element reference number (373 = "Date, CCYYMMDD"). **This is descriptive, not prescriptive** — the error isn't necessarily about the date; it's OpenText tagging the first element reference as a structural anchor.

**When the structural element (BIG02 here = Invoice Number) is missing, OpenText cannot anchor the segment and often surfaces the error against BIG01 with the date-type reference.** Diagnosis requires walking the UFF positions that feed the named segment and finding blank mandatory fields — not chasing the literal element named in the error.

### Common misleading errors

| Reported error | Likely real cause |
|---|---|
| `BIG_01_373` | Missing Invoice Number (UFF 77–98) or blank BIG02 after translation |
| `BIG_04_127` | Missing Purchase Order Number (UFF 99–120) |
| `N1_04_67` | Missing DUNS or Vendor ID (UFF 209–228 or 242–254) |
| `IT1_07_234` | Missing UPC at the level the retailer expects (case vs. pack) |
| `TDS_01_782` | Net Invoice Total (UFF 3–11 of summary) doesn't match sum of IT1 extensions |
| `CTT_01_354` | Total Number of Detail Lines (UFF 196–198) doesn't match actual record-20 count |

### Triage approach

1. Identify the X12 segment from the error tag.
2. Look up its UFF source positions in this doc.
3. Walk the UFF file at those positions — blank mandatory field? Wrong type encoding? Scale error?
4. Cross-ref `knowledge-base/edi/uff-format.md` for field requirements.
5. Cross-ref `knowledge-base/edi/uff-retailer-requirements.md` if this retailer has stricter rules.

## OpenText attachment error codes

The 500-series errors are OpenText's envelope-level codes:

| Code | Meaning |
|---|---|
| 504 | Target Error Within Attachment — inner document failed validation |
| 506 | User-Defined Generic Error — partner-configured validation rule failed |
| 510 | Data Type Error |
| 520 | Mandatory Element Missing |
| 530 | Invalid Code Value |

These wrap the inner X12 error; the inner `~BIG_XX_XXX` tag is where the actual problem lives.
