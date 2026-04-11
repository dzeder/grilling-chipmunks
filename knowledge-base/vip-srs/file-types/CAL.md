# CAL — Distributor Sales Calendar

## Overview

Trading day definitions for distributors, combining standard day-of-week schedules with exception dates (closures and special openings). The CAL file enables accurate business-day calculations for delivery scheduling, order deadlines, and sales period normalization.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `CAL.N{MMDDYYYY}`
- **Example:** `CAL.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** DISTID + SCTYPE + SCDATA (Distributor + Record Type + Calendar Data)

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | DISTID | Distributor ID | Y | 8 | N |
| 3 | SCTYPE | Calendar Record Type (DOW/EXC/OPN) | Y | 3 | A |
| 4 | SCDATA | Calendar Data (format varies by SCTYPE) | Y | 8 | A |
| 5 | SCPARENT | Parent Distributor ID | N | 8 | A |
| 6 | SCSTARTDT | Effective Start Date (YYYYMMDD) | N | 8 | N |
| 7 | SCENDDT | Effective End Date (YYYYMMDD) | N | 8 | N |

### Calendar Record Types (SCTYPE)

| Type | Description | SCDATA Format |
|------|-------------|---------------|
| DOW | Day of Week schedule | 8-position binary string (see below) |
| EXC | Exception closure | YYYYMMDD of the closed date |
| OPN | Open exception | YYYYMMDD of the open exception date |

### DOW SCDATA Format

An 8-position binary string where:
- Position 0: Ignored
- Position 1: Monday (1=open, 0=closed)
- Position 2: Tuesday
- Position 3: Wednesday
- Position 4: Thursday
- Position 5: Friday
- Position 6: Saturday
- Position 7: Sunday

**Example:** `01111100` = Monday through Friday open, Saturday and Sunday closed.

## Cross-References

| File | Relationship |
|------|-------------|
| DISTDA | DISTID maps to distributor master |

## Potential Ohanafy Mapping

Could feed a `Distributor_Calendar__c` custom object for delivery day planning. Trading day data is valuable for normalizing sales rates (sales-per-trading-day metrics) and predicting delivery windows.

## Notes

- 7 fields per record.
- A distributor typically has one DOW record (standard weekly schedule), plus EXC records for holidays, and optionally OPN records for special open days.
- EXC records override DOW — if DOW says Monday is open but an EXC exists for that specific Monday, the distributor is closed.
- OPN records override DOW — if DOW says Saturday is closed but an OPN exists for that Saturday, the distributor is open.
- SCSTARTDT/SCENDDT define the effective date range. DOW without dates applies indefinitely.
- No suffix variation in file naming — CAL files are delivered as a single consolidated file.
