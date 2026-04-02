---
name: ohfy-payments-expert
description: |
  Expert knowledge of the Ohanafy Payments system (OHFY-Payments). Apply when:
  - Building or debugging payment processing features
  - Working with payment settlement, refunds, or credit operations
  - Integrating payment gateways or financial systems
  - Understanding payment lifecycle and transaction management
  Covers: Payment processing, settlement workflows, refund handling,
  payment method management, and financial transaction tracking.
---

# OHFY-Payments Expert Skill

## Source Repository

**Repo:** `Ohanafy/OHFY-Payments`
**Version:** 0.32.0 (most mature feature package)
**Languages:** Apex, JavaScript, HTML, CSS
**Dependencies:** OHFY-Core 1.92.0+

### Accessing Current Source

```bash
if [ ! -d /tmp/ohfy-payments ]; then
  gh repo clone Ohanafy/OHFY-Payments /tmp/ohfy-payments -- --depth 1
fi
```

Key paths:
- Apex classes: `force-app/main/default/classes/`
- LWC components: `force-app/main/default/lwc/`

## Domain Coverage

- Payment capture and authorization
- Settlement workflows
- Refund and credit processing
- Payment method management
- Financial transaction tracking
- Gateway integration
- Payment reconciliation
- Integration with OMS for order payment

## Delegates To

- **ohfy-core-expert** — For trigger framework
- **ohfy-oms-expert** — For order-payment integration
- **sf-apex** — For Apex coding patterns
