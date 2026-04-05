# Ohanafy Salesforce Objects — data-harmonizer

Key objects this skill maps customer Excel data into. Never confuse Account with Distributor__c.

## Standard Objects

- `Account` — Retailer (has chain vs. independent flag). NOT the distributor.
- `Contact` — Contacts at retailers and distributors
- `Product2` / `PricebookEntry` — SKUs and pricing
- `Order` / `OrderItem` — Distributor orders

## Custom Objects

- `Distributor__c` — Distributor record with territory and brand authorizations
- `Brand__c` — Beverage brand, parent of products
- `Depletion__c` — Sell-through data: `Volume__c`, `Report_Period__c`, `Brand__c`

## Key Relationships

- Brand__c → Product2 (parent)
- Distributor__c → Account (serves retailers in territory)
- Depletion__c → Brand__c, Distributor__c, Account
- Order → Distributor__c (who ordered), OrderItem → Product2

## Common Excel Column Synonyms

The beverage industry uses many names for the same thing:

| SF Field | Common Excel Column Names |
|----------|--------------------------|
| Account.Name | Store, Location, Outlet, Retailer, Account, Customer |
| Distributor__c.Name | House, Wholesaler, Distributor, Dist, WHS |
| Product2.Name | Item, Product, SKU Name, Description |
| Product2.ProductCode | SKU, UPC, Item Number, Product Code, Item # |
| Brand__c.Name | Brand, Label, Supplier Brand |
| Depletion__c.Volume__c | Cases, Volume, Units, Qty, Cases Sold, Depletions |
| Depletion__c.Report_Period__c | Period, Week, Month, Report Date, Reporting Week |
