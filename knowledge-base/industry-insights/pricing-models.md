# Pricing Models — Beverage Industry

<!-- Populated by Content Watcher insights, beverage-erp-expert knowledge, and team input -->

## Front-Line Pricing

Front-line pricing (the price the retailer pays per case) is the single most complex
operational domain in beverage distribution. A single SKU might have 15 different valid
prices depending on multiple factors.

### Price Determinants

- **Account type**: on-premise (bars/restaurants) vs. off-premise (retail stores) — different price lists
- **Account sub-type**: chain account vs. independent — different negotiated rates
- **Package size**: same brand in 24-pack bottles vs. 15-pack cans vs. half-barrel keg
- **Volume tier**: buy 10 cases and price drops; buy 50 and it drops again
- **Promotional pricing**: supplier-funded promotions that change weekly or monthly
- **State posting requirements**: posted price floor that cannot be undercut
- **Split case pricing** (wine): individual bottles at different per-unit cost than full cases
- **Deposit fees**: per-container deposit added on top in bottle bill states (~10 states)
- **Excise tax pass-through**: some states require excise tax as a separate line item

### FOB (Free on Board) Pricing

FOB pricing defines the point at which ownership transfers from supplier to distributor.
The FOB price is the base cost to the distributor, on top of which the distributor adds
their margin. FOB pricing varies by:
- Geography (shipping distance from production facility)
- Volume commitments (annual contracted volumes)
- Payment terms (net 30 vs. net 60)

### Distributor Margin Expectations

Typical distributor margins by category:
- **Domestic beer**: 20-28% gross margin
- **Import beer**: 25-35% gross margin
- **Craft beer**: 28-40% gross margin (higher margin, lower volume)
- **Wine**: 30-40% gross margin (varies dramatically by price point)
- **Spirits**: 20-30% gross margin (higher dollar value per case offsets lower percentage)
- **Non-alcoholic**: 15-25% gross margin (high volume, low margin)

### Programming and Promotional Pricing

"Programming" in beverage distribution refers to supplier-funded promotional pricing programs:
- **Scan-backs**: retailer scans product at register, supplier reimburses distributor for discount
- **Post-offs**: temporary price reductions funded by the supplier
- **Display programs**: discounted pricing tied to in-store display placement
- **Volume incentives**: rebates triggered when distributor hits volume targets

Programming changes frequently (weekly or monthly) and creates enormous complexity
in the pricing engine. Most distributors have at least one person whose full-time job
is managing pricing in the ERP.

### State-by-State Regulation

- **Price posting states**: distributor must publicly post prices and hold them for a set period (typically 30 days)
- **Price maintenance states**: once posted, prices cannot change mid-period
- **Minimum markup laws**: some states require minimum markup above cost
- **Franchise pricing**: some franchise laws restrict a distributor's ability to set prices independently

## Ohanafy Pricing Implications

Ohanafy does not own the pricing engine (that lives in the ERP — typically Encompass or VIP),
but Ohanafy must:
- Display current pricing to sales reps in the field
- Show promotional pricing windows and program details
- Track pricing compliance (did the retailer receive the correct price?)
- Support price quote workflows for new accounts or volume changes
- Integrate with the ERP's pricing engine via API for real-time price lookups
