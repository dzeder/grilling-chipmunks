# Shipyard Brewing Company — Notes

Running notes from debugging sessions, design decisions, and gotchas.

<!-- Add entries with dates. Most recent first. -->

## 2026-04-09 — Project kickoff

- VIP SRS integration is the first real project built in the daniels-ohanafy monorepo
- Handoff doc produced in yangon workspace with 11 days of sample data
- Building fresh from spec + pattern library (not adapting existing VIP_Depletions_1GP scripts)
- Key design decision: immutable external IDs using colon-delimited prefix format (CHN:, ACT:, ITM:, etc.)
- Supplier code in sample data: `ARG`
- Data model uses `Placement__c` (not `Distributor_Placement__c` as referenced in some older docs)
