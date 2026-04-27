---
title: "UFF Per-Retailer Requirement Matrix"
last_updated: "2026-04-23"
relevant_skills: [ohfy-edi-expert, tray-expert, edi-processing-specialist]
---

# UFF — Per-Retailer Requirement Matrix

Each trading partner flips a subset of UFF fields from the base spec's defaults into their own required set. A structurally valid UFF that satisfies 7-Eleven can still reject at Walmart, and vice-versa. Generator logic must evaluate retailer-specific requirements, not just the base spec.

Source: the MillerCoors UFF spec sheet's `7-Eleven` and `Retailer 2` columns. "Retailer 2" is assumed to be **Walmart** based on the customer context (Beverage Market sends UFF to both).

## 7-Eleven

### Required header fields (10)

- Record Type (1–2)
- Miller Assigned Distributor Number (3–8)
- Retailer Identification Number (9–28)
- Document Type (29–34) — literal `INV   `
- File Trace Number (35–43)
- System Date (44–51)
- System Time (52–59)
- **Product Category Invoice Code (60)** — required (most often `2` for beer, `1` for soda)
- Filler (61–76)
- Invoice Number (77–98)
- Invoice Date (121–128)
- Distributor Vendor ID Number (209–228)
- Outlet Number (581–600)

### Required detail fields (20)

- Record Type (1–2)
- Gross Unit Price (3–11)
- Deposit Amount (12–20)
- Charge CRV (21–29)
- Total Tax (102–110)
- Delivery Charge (111–119)
- Freight Charge (120–128)
- Promotional Discount (129–137)
- Quantity Shipped (176–184)
- Shipped Unit of Measure (185–186)
- **UPC — Case (247–260)** — 7-Eleven wants case-level UPC
- **GTIN — Case (289–302)** — matching case-level GTIN

### Required summary fields (30)

- Record Type (1–2)
- Net Invoice Total (3–11)
- **Ticket Adjustment Discount (21–29)** — 7-Eleven requires this be populated
- **Total Number of Detail Lines (196–198)** — 7-Eleven requires the CTT-equivalent count

### Notes

- 7-Eleven's Retailer Identification Number is their assigned trading-partner ID (not necessarily DUNS+4); confirm with their companion guide when onboarding.
- 7-Eleven consumes **case-level** UPC/GTIN. Sending pack or unit in those positions misidentifies the product.

## Walmart (Retailer 2)

### Required header fields (10)

- Record Type (1–2)
- Miller Assigned Distributor Number (3–8)
- Retailer Identification Number (9–28)
- Document Type (29–34)
- File Trace Number (35–43)
- System Date (44–51)
- System Time (52–59)
- Filler (61–76) — note: `Product Category Invoice Code` is **not** flagged required (blank = mixed)
- Invoice Number (77–98)
- Invoice Date (121–128)
- Delivery Date / Return Date (137–144)
- Distributor Vendor ID Number (209–228)
- Outlet Number (581–600)

### Required detail fields (20)

- Record Type (1–2)
- Gross Unit Price (3–11)
- Deposit Amount (12–20)
- Charge CRV (21–29)
- **State Tax per unit (75–83)** — Walmart wants line-level state tax
- **County Tax per unit (84–92)** — line-level county tax
- **City Tax per unit (93–101)** — line-level city tax
- Total Tax (102–110)
- Delivery Charge (111–119)
- Promotional Discount (129–137)
- Quantity Shipped (176–184)
- Shipped Unit of Measure (185–186)
- **UPC — Pack (261–274)** — Walmart wants pack-level UPC
- **GTIN — Pack (303–316)** — matching pack-level GTIN
- **Product Description (399–458)** — line-level product description required

### Required summary fields (30)

- Record Type (1–2)
- (fewer summary fields are flagged required vs. 7-Eleven)

### Notes

- Walmart consumes **pack-level** UPC/GTIN — the opposite of 7-Eleven. A generator that hardcodes case-level UPC for all partners will reject at Walmart.
- Walmart requires tax broken out by jurisdiction at the **line** level, not just summarized. 7-Eleven only requires the summed Total Tax.
- Walmart requires Product Description on every detail line. 7-Eleven does not flag it required (though it's generally provided anyway).

## Differences at a glance

| Field | 7-Eleven | Walmart |
|---|---|---|
| Product Category Invoice Code | Required | Not flagged |
| Delivery Date | Not flagged | Required |
| Line-level State/County/City Tax | Not flagged | Required |
| Freight Charge | Required | Not flagged |
| UPC level | **Case** (247–260) | **Pack** (261–274) |
| GTIN level | **Case** (289–302) | **Pack** (303–316) |
| Product Description (line) | Not flagged | Required |
| Summary Ticket Adjustment Discount | Required | Not flagged |
| Summary Total Number of Detail Lines | Required | Not flagged |

## Implementation pattern

A retailer-aware UFF generator should:

1. Emit the full UFF structure (all fixed-width positions populated) — never omit fields, always include placeholder zero/space values where the spec says a field exists.
2. Validate mandatory-field presence **per retailer**, not just against the base spec. Missing a retailer-flagged field = guaranteed rejection.
3. Key the retailer from either the `Retailer Identification Number` (9–28) or a routing table. Store per-retailer requirement sets as config (YAML/JSON), not hardcoded conditionals.
4. Run a pre-send validator against the generated file: record-length, record-type prefix, ASCII-only, CRLF line endings, mandatory-field presence matching the retailer's profile.

## Other MillerCoors retailers

The sheet only shows 7-Eleven and Retailer 2 (Walmart). Other retailers (Kroger, Target, Albertsons, etc.) each have their own requirement profile. When onboarding a new retailer:

1. Request the retailer's UFF companion guide from MillerCoors or the retailer directly.
2. Extract their required-field set.
3. Add a new profile to the retailer config.
4. Send a test file and work through rejections until clean.
