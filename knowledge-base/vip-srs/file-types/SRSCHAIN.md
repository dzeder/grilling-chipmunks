# SRSCHAIN — Chain Reference

## Overview

The Chain Reference file provides a master lookup of retail chain codes used throughout the VIP SRS system. Each record maps a 10-digit zero-padded chain code to its human-readable description. Retail outlet records (OUTDA) reference these chain codes via the ROCHN field to identify the chain affiliation of each account.

## File Naming

- **Pattern:** `SRSCHAIN`
- **Example:** `SRSCHAIN`

## Load Method

- **Method:** Add/Update
- **Key:** CHAIN

## Field Layout (Detail Records)

Fixed-position format:

| # | Field | Pos Start | Length | Description | Req | Type |
|---|-------|-----------|--------|-------------|-----|------|
| 1 | CHAIN | 1 | 10 | Chain code (zero-padded) | Y | A |
| 2 | DESC | 11 | 50 | Chain description | Y | A |
| 3 | FILE | 61 | 130 | Reserved for future use | N | A |

**Record Type:** Each record includes a RecordType identifier.

## Cross-References

| File | Relationship |
|------|-------------|
| OUTDA | Outlet ROCHN field references CHAIN code |
| SRSVALUE | Chain-related coded values may appear here |

## Notes

- Chain codes are always 10 digits, zero-padded on the left.
- The FILE field is reserved for future use and is currently blank or unused.
- This is a reference/decode file — it does not contain transactional data.
- Used to enrich outlet records with chain name during import processing.
