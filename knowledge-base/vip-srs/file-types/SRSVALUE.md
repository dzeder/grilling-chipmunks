# SRSVALUE — Valid Values

## Overview

The Valid Values file is the universal decode/reference table for all coded fields across the VIP SRS file system. Each record maps a field name and code to its human-readable description. Any file that uses coded values (class of trade, container type, UOM, status codes, etc.) should be decoded using entries from this file.

## File Naming

- **Pattern:** `SRSVALUE`
- **Example:** `SRSVALUE`

## Load Method

- **Method:** Add/Update
- **Key:** FIELD

## Field Layout (Detail Records)

Delimited format (5 columns) with fixed-position backing:

| # | Field | Pos Start | Length | Description | Req | Max Len | Type |
|---|-------|-----------|--------|-------------|-----|---------|------|
| 1 | FIELD | 1 | 10 | Field name identifier | Y | 10 | A |
| 2 | FIELDNAME | 11 | 20 | Field description | Y | 20 | A |
| 3 | CODE | 31 | 5 | Value code | Y | 5 | A |
| 4 | DESC | 34 | 50 | Value description | Y | 50 | A |

**Record Type:** Each record includes a RecordType identifier.

## Cross-References

| File | Relationship |
|------|-------------|
| ITM2DA | ITCTYP (ContainerType) and other coded item fields |
| OUTDA | ROCOD (ClassOfTrade), ROFWIN (FineWine), ROCSTS (ChainStatus), ROCSP (Displays), ROETHN (PatronEthnicity), ROIVOL (IndustryVolume), ROLIFE (PatronLifestyle), ROOCC (Occupation), ROPAGE (PatronAge), ROPTYPE (PackageType), ROSELL (Sell), ROSTS (Status) |
| SLSDA | BSTRTYPE (transaction type codes), UOM codes |
| INVDA | TransCode decode values |
| All files | Any field containing coded/enumerated values |

## Notes

- This is the single source of truth for decoding all coded fields in VIP SRS.
- Always load SRSVALUE before processing other files so decode lookups are available.
- The CODE field length is 5 characters — some codes are numeric, some alphabetic.
- Note the slight overlap in fixed-position layout: CODE starts at 31 (length 5) and DESC starts at 34 — this reflects the ISV spec's actual positions. In delimited format, fields are cleanly separated.
- New valid values may be added by VIP over time; always process as Add/Update.
