# VIP Pricing & Promotion Types — Plain English Guide

> Every promotion and pricing mechanism in VIP, explained with real examples
> from Gulf Distributing's data.

---

## 1. Base Price (Deployment Master — the foundation)

**What it is:** Every item has a base case price that depends on *who's buying* (price code) and *which warehouse* ships it. This is the starting point before anything else kicks in.

**Example:** A 24-pack of Bud Light might be:
- **$24.50/case** to a Walmart (price code 14)
- **$25.00/case** to an independent retailer (price code 11)
- **$23.80/case** to a military exchange (price code 12)
- **$22.00/case** to an employee (price code EM)

All from the same warehouse. Different warehouse? Might be a slightly different base price because landed cost differs.

---

## 2. Percentage Rebate (Deployment Method 1)

**What it is:** The supplier sets a front-line price and a rebate percentage. The distributor sells at the front-line price, then gets a percentage back from the supplier.

**Example:** Red Bull 8.4oz 24-pack:
- Front-line price: **$37.69/case**
- Rebate: **50%**
- Distributor's net cost: **$18.85/case**
- The distributor sells at $37.69 and the supplier rebates $18.84 back

This is common for energy drinks and high-margin items where the supplier wants to control the retail price but incentivize the distributor with a big rebate.

---

## 3. Tiered Selling Prices + Rebate Amounts (Deployment Method 2)

**What it is:** VIP supports up to 20 pricing tiers per item. Each tier has its own selling price and its own rebate amount. The tier a retailer falls into depends on their loyalty level or volume commitment.

**Example:** Red Bull 12oz 24-pack with a tiered program:

| Tier | Level | Selling Price | Rebate | Net to Distributor |
|------|-------|--------------|--------|-------------------|
| Tier 1 | Gold retailer | $34.19/case | $1.00/case | $33.19 |
| Tier 2 | Platinum retailer | $33.50/case | $1.50/case | $32.00 |
| Tier 3 | Diamond retailer | $32.80/case | $2.00/case | $30.80 |
| Tier 4 | Triple Diamond | $32.00/case | $2.50/case | $29.50 |

A convenience store that commits to a Gold-level program gets Tier 1 pricing. A chain that hits Triple Diamond volume thresholds gets Tier 4. The selling price gets lower *and* the rebate gets bigger as the retailer moves up.

Gulf has **120+ Red Bull tier levels alone** — that's how granular this gets.

---

## 4. Quantity Deals (QD)

**What it is:** Buy X cases or more and get a per-case discount. These are the bread-and-butter supplier promotions. Time-limited, item-specific.

**Examples from Gulf's actual data:**
- **"RECOVERY 5CS QD $3 OFF"** — Buy 5+ cases of Recovery brand, get $3 off each case
- **"3CS $10 QD"** — Buy 3+ cases, get $10 off the order (or $10 off per case, depending on setup)
- **"LITE 15/16 10CS QD 3/9-12/31"** — Buy 10+ cases of Miller Lite 15-pack or 16-pack, get a deal running March 9 through Dec 31
- **"SAZERAC WELL 5/50 CS QD"** — Two tiers: buy 5+ cases for one discount, buy 50+ cases for a bigger discount
- **"TOPO CHICO 12PK 5CS QD"** — Buy 5+ cases of Topo Chico 12-packs, get a deal
- **"FISHERS ISLAND 4PK 5CS QD"** — Buy 5+ cases of Fishers Island 4-packs

These are set up as discount worksheets (DISCWKSTT) with start/end dates. The supplier funds them and the distributor passes the savings to the retailer.

---

## 5. Post-Off Allowances

**What it is:** The supplier temporarily reduces the distributor's cost by a flat dollar amount per case. The distributor *may or may not* pass the savings to the retailer — that's their call.

**Example:**
- Anheuser-Busch runs a summer post-off: **$2.00/case off** all Bud Light 24-packs for June through August
- The distributor's cost drops from $18.00 to $16.00 per case
- The distributor might drop the retail price by $1.50 and pocket the extra $0.50 margin
- Or they might pass the full $2.00 through

Post-offs show up in PENDPRICT.POSTOFF and on order lines as ORPOST. They're separate from discounts — they're a *cost reduction*, not a *price reduction*.

---

## 6. Front-Line Price Adjustments

**What it is:** A temporary change to the base selling price itself (what the retailer actually pays), usually driven by a supplier program that says "sell this item at exactly $X for this period."

**Example:**
- Supplier says: "We're running a national program — sell our new seltzer at **$22.50/case** to all off-premise accounts from March through September"
- VIP overrides the normal price code-based pricing and sets the front-line price to $22.50
- This is different from a discount — the *actual price* changes, not a discount applied on top

Gulf has 161 front-line price entries, mostly with "permanent" end dates (year 2039), suggesting these are standing retail price recommendations.

---

## 7. Group Discounts (50% of all discounts)

**What it is:** A discount that applies to *every customer* in a given price code or group. It's a blanket promotion — no negotiation, everyone gets it.

**Example:**
- All independent off-premise retailers (price code 11) get **$1.50/case off** on Modelo Especial 24-packs during Cinco de Mayo month
- Every customer with price code 11 automatically gets this pricing
- 18,695 of Gulf's discount records are group-level

---

## 8. Customer-Specific Discounts (39% of all discounts)

**What it is:** A negotiated deal for a specific customer or chain. "We'll give *you* a better price because you committed to volume or prominent shelf placement."

**Example:**
- The distributor negotiates with a large independent bar: "If you put us on 8 taps and buy 20+ kegs/month, we'll give you **$3.00/case off** on all craft brands"
- This pricing only applies to that one account
- 14,439 of Gulf's discount records are customer-specific

---

## 9. Account-Level Discounts (11% of all discounts)

**What it is:** Similar to customer-specific but typically applies at the account/location level rather than chain level. Think of it as a per-store override.

**Example:**
- A grocery chain has 15 stores. Most get standard chain pricing, but their flagship store that does 3x the volume gets an **extra $0.75/case off** on top of the chain deal
- 4,159 of Gulf's discount records are account-level

---

## 10. Performance / Volume Discounts

**What it is:** Discounts that kick in based on how much a retailer buys over a period (month, quarter, year). The more they buy, the bigger the discount.

**Example:**
- "Buy 100 cases of our portfolio this quarter → **$0.50/case rebate**. Buy 250+ → **$1.25/case rebate**. Buy 500+ → **$2.00/case rebate**."
- These are tracked through DSINEXT (performance discount extension) and DSQTYT (quantity break tables)
- The PERFDISC flag on discount worksheets marks these

---

## 11. Billbacks / Supplier Reimbursements

**What it is:** The distributor gives the retailer a deal, then bills the cost back to the supplier. The distributor is the middleman — they front the discount and get reimbursed.

**Example:**
- A supplier runs a program: "If a retailer buys 15+ cases, give them **$1.00 off each case**. We'll also pay you an **extra $0.50/case billback** for executing the promotion"
- Retailer buys 20 cases at $24.00 instead of $25.00 → saves $20
- Distributor bills back $1.00 x 20 = **$20.00** to the supplier (the discount they gave)
- Distributor also gets $0.50 x 20 = **$10.00** as an execution incentive
- **Net:** retailer saves $20, distributor makes an extra $10, supplier spends $30 to move 20 cases

In VIP, the DPMAST1T rebate amounts are essentially the billback — the REBATEAMOUNT columns track what the supplier owes back per case. Ohanafy tracks this through `Billback__c` linked to `Promotion__c`.

---

## 12. Deposits (Keg & Container)

**What it is:** Not a promotion, but a pricing component. When a retailer buys a keg, they pay a deposit that gets refunded when the empty is returned.

**Example:**
- Half-barrel keg of Bud Light: $120.00 product price + **$50.00 keg deposit** = $170.00 on the invoice
- When the empty keg comes back, the $50.00 is credited
- Gulf has 5,389 keg deposit records averaging $50 (range $10–$250)

---

## 13. Marketing Fund Accruals

**What it is:** Suppliers accrue marketing dollars based on distributor sales, then the distributor can spend those dollars on local promotions, displays, events, etc.

**Example:**
- Supplier accrues **$0.25/case** sold into a marketing fund
- Distributor sells 10,000 cases in Q1 → $2,500 in the fund
- Distributor uses $1,500 for a beer festival sponsorship and $1,000 for retail display materials
- Shows up on order lines as ORMAMT (marketing funds amount)

---

## How They All Stack Together

On a single order line, a retailer might benefit from multiple layers at once:

> **Bud Light 24-pack, 20 cases to a Walmart:**
>
> | Layer | Effect |
> |-------|--------|
> | Base price | $24.50/case (Walmart price code) |
> | Summer post-off | -$2.00/case (supplier cost reduction) |
> | Quantity deal | -$1.00/case (10+ case QD) |
> | Keg deposit | N/A (not a keg) |
> | **Final price** | **$21.50/case x 20 = $430.00** |
>
> Behind the scenes, the distributor bills back the $1.00 QD to the supplier
> and keeps the $2.00 post-off margin improvement.

That stacking — and VIP's "best discount" engine that evaluates all applicable discounts and picks the most favorable one for the customer — is why pricing is the most complex part of any migration.
