# Beverage Supply Chain Glossary

Core domain terminology for Ohanafy's beverage supply chain platform.

## 3-Tier System

Supplier → Distributor → Retailer. Ohanafy customers are suppliers.
They do NOT sell to retailers directly in most states. Never confuse Account (retailer)
with Distributor__c in Salesforce — they are different objects.

## Depletion

Distributor sell-through to retailers. The most important metric.
When a customer asks about "sales" they almost always mean depletions.

## TTB

Alcohol and Tobacco Tax and Trade Bureau. Federal regulator. Handles permits,
COLA label approvals, excise tax. NEVER answer TTB or compliance questions in the
support agent — always escalate to a human immediately.

## COLA

Certificate of Label Approval. Required before a new product goes to market.
Takes 2-8 weeks. Delays product launches.

## On-Premise / Off-Premise

On = bars and restaurants. Off = retail stores.

## Chain vs. Independent

Chain = national/regional retailers (Total Wine, Kroger).
Independent = single-location stores. Different sales motions, different data shapes.

## Depletion Report

Monthly distributor report of sell-through to retailers.

## Footprint

Which distributors carry which brands in which states/territories.

## Blitz

Focused sales push in a territory. Short duration, high activity.

## POD (Point of Distribution)

One account carrying one SKU.

## Velocity

Rate of sale at the account level (cases/month).

## Programming

Promotional deals funded by the supplier.

## Allocations

Limited product available to a distributor. Critical for rare releases.

## Chain Authorization

Approval from a chain buyer to carry a product across all doors.

## Vintage / Crop Year

Wine and some spirits tied to harvest year. A SKU may only
exist for one vintage. Doc agents must check availability dates before referencing SKUs.

## Key Salesforce Objects

- `Account` — Retailer (has chain vs. independent flag)
- `Distributor__c` — Distributor record with territory and brand authorizations
- `Brand__c` — Beverage brand, parent of products
- `Product2` / `PricebookEntry` — SKUs and pricing
- `Depletion__c` — Sell-through data: `Volume__c`, `Report_Period__c`, `Brand__c`
- `Order` / `OrderItem` — Distributor orders
