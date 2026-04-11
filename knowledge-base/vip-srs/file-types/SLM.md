# SLM — Distributor Salesperson

## Overview

Sales representative records from distributors, including an organizational hierarchy of up to three levels above the individual rep. The SLM file captures salesperson codes, names, division assignments, and parent distributor relationships. This data enables sales territory analysis and rep-level performance tracking.

## Integration Status

Not currently integrated. Reference only.

## File Naming

- **Pattern:** `SLM{suffix}.N{MMDDYYYY}`
- **Suffixes:** DA (daily), WK (weekly), FX (fixed/full), NW (new)
- **Example:** `SLMDA.N04102026`

## Load Method

- **Method:** Add/Update
- **Key:** SMCODE + SMDIST (Salesperson Code + Distributor ID)

## Field Layout (Detail Records)

| # | Field | Description | Req | Max Len | Type |
|---|-------|-------------|-----|---------|------|
| 1 | RecordType | Record type indicator | Y | - | - |
| 2 | SMDID | Distributor System ID | Y | 8 | A |
| 3 | SMDIST | Distributor ID | Y | 8 | A |
| 4 | SMCODE | Salesperson Code | Y | 8 | A |
| 5 | SMNAME | Salesperson Name | Y | 35 | A |
| 6 | SML1 | Level 1 Code (immediate supervisor) | N | 5 | A |
| 7 | SML1NAME | Level 1 Name | N | 35 | A |
| 8 | SML2 | Level 2 Code | N | 5 | A |
| 9 | SML2NAME | Level 2 Name | N | 35 | A |
| 10 | SML3 | Level 3 Code | N | 5 | A |
| 11 | SML3NAME | Level 3 Name | N | 35 | A |
| 12 | SMDIV | Sales Division Code | N | 5 | A |
| 13 | SMSVNAME | Sales Division Description | N | 35 | A |
| 14 | SMPARENT | Parent Distributor ID | N | 8 | A |

## Cross-References

| File | Relationship |
|------|-------------|
| DISTDA | SMDIST maps to distributor master (Distributor ID) |
| OUTDA | ROSM1/ROSM2 fields in outlet records reference SMCODE |
| SLSDA | BSSALREP references SMCODE |
| ORD | ORDSALREPID references SMCODE |

## Potential Ohanafy Mapping

Could create `Contact` records for distributor sales reps, or a custom `Distributor_Rep__c` object. The three-level hierarchy (SML1-SML3) could map to a role hierarchy or reporting structure. Division codes could map to `Team` or `Territory` objects. Most useful for enabling rep-level depletion and placement analysis.

## Notes

- 14 fields per record.
- The three-level hierarchy (SML1/SML2/SML3) represents organizational levels above the individual rep, not geographic territories.
- SMDIV (Sales Division Code) is separate from the hierarchy levels and represents functional divisions within the distributor.
- SMPARENT links to the parent distributor for multi-house networks.
- Add/Update method — existing records are updated in place when matching on SMCODE + SMDIST.
- Reps appear in SLSDA (BSSALREP) and OUTDA (ROSM1/ROSM2) — joining these enables rep-level outlet and depletion analysis.
