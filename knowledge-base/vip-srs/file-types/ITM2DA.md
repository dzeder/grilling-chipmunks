# ITM2DA — Supplier Item Master (Extended)

## Overview

The extended Supplier Item Master file contains the canonical product catalog from the supplier's perspective. Each record represents a unique supplier item (SKU) with 66 columns covering identification, GTINs, packaging dimensions, volume metrics, brand hierarchy, and category classifications. This is the primary item reference file — distributor-specific item mappings are in ITMDA.

## File Naming

- **Pattern:** `ITM2DA.N{MMDDYYYY}`
- **Example:** `ITM2DA.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** ITEM (Supplier Item Code)

## Field Layout (Detail Records)

Fixed-position format. Core fields shown below (66 total columns; remaining columns cover volume, packaging, brand, and category fields):

| # | Field | Pos Start | Length | Description | Req | Type |
|---|-------|-----------|--------|-------------|-----|------|
| 1 | SUPPID | 1 | 3 | Supplier ID | Y | A |
| 2 | DISTID | 4 | 8 | Distributor ID (blank in supplier item file) | N | A |
| 3 | ITEM | 12 | 10 | Supplier Item Code — **PRIMARY KEY** | Y | A |
| 4 | DESC | 22 | 60 | Item Description | Y | A |
| 5 | CASEGTIN | 82 | 14 | Case GTIN (UPC) | N | N |
| 6 | RETGTIN | 96 | 14 | Retail GTIN (UPC) | N | N |
| 7 | ACTDATE | 110 | 8 | Activation Date (YYYYMMDD) | N | N |
| 8 | DEADATE | 118 | 8 | Deactivation Date (YYYYMMDD) | N | N |
| 9 | UNITS | 126 | 4 | Units per case | Y | N |
| 10 | SELLUNIT | 130 | 3 | Selling units per case | N | N |
| 11 | WEIGHT | 133 | 5 | Case weight (decimal) | N | D |
| 12 | OUNCE | 138 | 4 | Ounces per case | N | N |
| 13-66 | ... | 142+ | varies | Volume, packaging, brand, categories, etc. | N | varies |

**Note:** Columns 13-66 include additional attributes such as container type (ITCTYP), brand code, brand family, category, subcategory, size, proof/ABV, vintage, country of origin, region, varietal, and various classification codes. Refer to the full ISV spec for complete positional layout.

## Cross-References

| File | Relationship |
|------|-------------|
| SRSVALUE | ITCTYP (ContainerType) and other coded fields decode here |
| ITMDA | Distributor item mappings reference SupplierItem back to this file |
| SLSDA | SupplierItem in sales transactions maps to ITEM |
| INVDA | SupplierItem in inventory transactions maps to ITEM |
| CTLDA | SupplierItem in control/allocation records maps to ITEM |

## Notes

- DISTID is blank in this file — it represents the supplier's master catalog, not distributor-specific data.
- ITEM is the universal join key across all transactional files (SLSDA, INVDA, CTLDA).
- ACTDATE and DEADATE control item lifecycle — deactivated items may still appear in historical transactions.
- UNITS (units per case) is critical for bottle-to-case conversion in INVDA and SLSDA processing.
- The file contains 66 columns total; only the first 12 positional fields are detailed above. The remaining 54 cover extended product attributes.
- GTIN fields (CASEGTIN, RETGTIN) are 14-digit numeric — handle as strings to preserve leading zeros.
