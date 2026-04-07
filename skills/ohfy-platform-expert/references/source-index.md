# OHFY-Service_Locator Source Index
> Last synced: 2026-04-07T12:28:51Z | Commit: a3192b4 | Repo: Ohanafy/OHFY-Service_Locator

## Apex Classes (8 production, 0 test/mock excluded)

| Class | Access | Description |
|-------|--------|-------------|
| DeliveryUpdaterService | public |  |
| PromotionsService | public | Service interface for managing promotions and their related junctio |
| AccountOMSTriggerService | public | Service interface for handling Account trigger operations related t |
| EventREXTriggerService | public | Service interface for handling Event trigger operations related to |
| InvoiceREXTriggerService | public |  |
| TaskREXTriggerService | public | Service interface for handling Task trigger operations related to R |
| ServiceLocator | public | Service Locator pattern implementation for dependency injection in |
| ServiceLocator_T | public | Test class for ServiceLocator class. Provides comprehensive test co |

## Triggers

_No triggers found._

## Service Methods

| Class | Method | Signature |
|-------|--------|-----------|
| ServiceLocator | resolve | `public static Object resolve(String serviceName) ` |
| ServiceLocator_T | getValue | `public String getValue() ` |

## Service Layer Graph (one level deep)

> **Coverage Limitations:** Captures static patterns only: `new *Service(`,
> `ServiceLocator.getInstance(`, `System.enqueueJob`. Dynamic dispatch and
> factory patterns are not captured. Treat as a starting map, not exhaustive.

| Service Class | Calls / Instantiates | Pattern |
|--------------|---------------------|---------|
| ServiceLocator | ServiceLocator.resolve | ServiceLocator |
| ServiceLocator_T | ServiceLocator.ServiceLocatorException,ServiceLocator.resolve | ServiceLocator |

## Custom Objects & Fields

_No custom objects found._

## Common Patterns

| Pattern | Files Using It | Notes |
|---------|---------------|-------|
| Trigger Bypass | 0 | Classes referencing bypass mechanisms |
| Service Locator | 2 | Classes using service locator pattern |
| Batch/Schedulable | 0 | Classes implementing batch or schedulable |
| Queueable | 0 | Classes using async queueable jobs |
| Platform Events | 0 | Classes publishing or subscribing to events |

## Test Coverage Summary

| Metric | Count |
|--------|-------|
| Production classes | 7 |
| Test/Mock/Stub classes | 1 |
| Test-to-production ratio | 14% |

### Classes Without Apparent Test Coverage (6)

- `DeliveryUpdaterService`
- `PromotionsService`
- `AccountOMSTriggerService`
- `EventREXTriggerService`
- `InvoiceREXTriggerService`
- `TaskREXTriggerService`

## Known Gotchas

_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._

