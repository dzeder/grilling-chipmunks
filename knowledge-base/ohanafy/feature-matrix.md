# Ohanafy Feature Matrix by SKU

<!-- Synthesized from ohfy-*-expert skills -->

## SKU Capabilities

| SKU | Package | Domain | Key Features |
|-----|---------|--------|-------------|
| **Core** | OHFY-Core | Foundation | Triggers, services, bypass patterns, 143+ objects, service layer |
| **Platform** | OHFY-Platform | Shared services | Cross-SKU platform services, utilities |
| **Data Model** | OHFY-Data_Model | Schema | 30+ custom objects, field schemas, value sets, relationships |
| **OMS** | OHFY-OMS + UI | Orders | Order capture, processing, fulfillment, order management workflows |
| **WMS** | OHFY-WMS + UI | Warehouse | Picking, packing, shipping, inventory management, warehouse operations |
| **REX** | OHFY-REX + UI | Retail | Retail execution, POS integration, display compliance, shelf audits |
| **EDI** | OHFY-EDI | B2B Data | X12 850/810/856 processing, OpenText, Transcepta, B2B interchange |
| **Ecom** | OHFY-Ecom | E-Commerce | Shopify/WooCommerce integration, catalog, cart, checkout |
| **Payments** | OHFY-Payments | Payments | Payment processing, settlement, reconciliation |
| **Configure** | OHFY-Configure | Setup | System configuration, feature flags, customer-specific setup |

## Common Technical Patterns

Across all SKUs, Ohanafy follows consistent Salesforce development patterns:

### Trigger Architecture
- **Trigger → Handler** pattern — lightweight triggers delegate to handler classes
- **Trigger bypass** mechanism — configurable bypass for data loads and testing
- Single trigger per object enforced

### Service Layer
- **Service Locator** pattern for cross-service dependencies
- Service classes handle business logic (not triggers or controllers)
- One level of service-to-service calls (no deep chains)

### Async Processing
- **Batch/Schedulable** for large data operations
- **Queueable** for chained async work
- **Platform Events** for cross-package communication

### Data Patterns
- Lookup and master-detail relationships between packages
- External ID fields for integration (Tray.io upserts)
- Custom metadata types for per-customer configuration
- Field-level security and CRUD enforcement

### Testing
- 85%+ Apex coverage target
- Meaningful assertions (not just governor limit checks)
- Test data factories per SKU
