# Status Transitions

## Order__c (Invoice) Status

### Valid Status Progression

Status must advance forward only (validated by `TA_Invoice_BU_StatusUpdater`):

```
New (1) → Scheduled (1) → In Progress (1) → Picking (2) → Loaded (3) →
Out For Delivery (4) → Delivered (5) → Complete (6)
                                        ↓
                                   Cancelled (7)
```

### Status Values and Codes

| Status | Code | Can Move To |
|--------|------|-------------|
| New | 1 | Scheduled, In Progress, Picking, Cancelled |
| Scheduled | 1 | In Progress, Picking, Cancelled |
| In Progress | 1 | Picking, Cancelled |
| Picking | 2 | Loaded, Cancelled |
| Loaded | 3 | Out For Delivery, Cancelled |
| Out For Delivery | 4 | Delivered, Cancelled |
| Delivered | 5 | Complete |
| Complete | 6 | (terminal state) |
| Cancelled | 7 | (terminal state) |

### Error Message

**"Cannot move to a previous status"**

Attempting to move backward (e.g., Loaded → Picking) will fail validation.

### Bypass Pattern

```apex
U_OrderStatusValidationBypass.isBypassEnabled = true;
try {
    order.Status__c = 'New';  // Can move backward
    update order;
} finally {
    U_OrderStatusValidationBypass.isBypassEnabled = false;
}
```

### Integration Examples

**Safe Forward Progression**:
```javascript
// Current: "New"
{ "ohfy__Status__c": "Picking" }  // Valid

// Current: "Picking"
{ "ohfy__Status__c": "Loaded" }  // Valid

// Current: "Loaded"
{ "ohfy__Status__c": "Complete" }  // Valid
```

**Unsafe Backward Movement**:
```javascript
// Current: "Loaded"
{ "ohfy__Status__c": "Picking" }  // ERROR

// Current: "Complete"
{ "ohfy__Status__c": "New" }  // ERROR
```

---

## Purchase_Order__c Status

### Valid Status Progression

```
Draft → Submitted → Approved → Received → Complete
                              ↓
                         Cancelled
```

### Status Workflow

1. **Draft** - PO being created
2. **Submitted** - Sent to vendor
3. **Approved** - Vendor accepted
4. **Received** - Items received at warehouse
5. **Complete** - PO closed
6. **Cancelled** - PO cancelled

---

## Inventory__c Status

### Valid Status Values

- **Available** - Ready for sale
- **Reserved** - Pre-reserved for order
- **Allocated** - Assigned to specific order
- **Depleted** - Out of stock
- **Damaged** - Damaged goods
- **Expired** - Past expiration date

### Status Progression

```
Available → Reserved → Allocated → (deleted when fulfilled)
          ↓          ↓
      Damaged    Expired
```

### Trigger

`TA_Inventory_BU_StatusChecker` validates status transitions.

---

## See Also

- `../triggers/order-triggers.md` - TA_Invoice_BU_StatusUpdater details
- `../triggers/bypass-patterns.md` - How to bypass validation
- `../triggers/common-errors.md` - Status error messages
