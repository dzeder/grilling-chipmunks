# Org Configuration Matrix

**Environment-Specific Field Mappings and Constraints for OHFY Integrations**

Document org-specific configurations, field mappings, and constraints for the Distro production environment and other OHFY deployments.

---

## 🏢 Distro Production Environment

### Environment Overview
- **Org Type**: Production Salesforce org with OHFY-Core package
- **API Version**: 59.0
- **OHFY Package Version**: 1.90+
- **Total Custom Objects**: 180 (140 from OHFY-Core + 40 org-specific)
- **Managed Packages**: Maps, Geocoding, and additional third-party packages
- **Custom Apex Classes**: 3 unmanaged (B_Maps_RouteBuilder, B_Maps_RouteBuilder_T, WalkthroughController)

### Core OHFY Objects Configuration

#### **ohfy__Order__c**
```javascript
const OrderConfiguration = {
  object: "ohfy__Order__c",

  // Required fields for integration
  requiredFields: [
    "ohfy__External_ID__c",
    "ohfy__Customer__c",        // Master-Detail(Account)
    "ohfy__Order_Date__c",
    "ohfy__Status__c",
    "ohfy__Sales_Rep__c",       // Lookup(User)
    "ohfy__Delivery_Pickup_Date__c"
  ],

  // Status picklist values (exact values from org)
  statusPicklistValues: [
    "New",
    "Scheduled",
    "In Progress",
    "Picking",
    "Loaded",
    "Out For Delivery",
    "Delivered",
    "Complete",
    "Cancelled"
  ],

  // Read-only fields (calculated by Salesforce)
  readOnlyFields: [
    "ohfy__Order_Total__c",      // Formula field
    "ohfy__Sub_Total__c",        // Rollup from Order Items
    "ohfy__Sales_Tax__c",        // Calculated field
    "ohfy__Order_Number__c",     // Auto-number
    "Name",                      // Auto-generated
    "CreatedDate",
    "LastModifiedDate",
    "SystemModstamp"
  ],

  // Field mappings for common external systems
  externalMappings: {
    edi: {
      "ohfy__External_ID__c": "document_number",
      "ohfy__Order_Date__c": "order_date",
      "ohfy__Customer_Reference__c": "customer_po_number",
      "ohfy__Delivery_Instructions__c": "delivery_notes"
    },
    quickbooks: {
      "ohfy__External_ID__c": "qb_transaction_id",
      "ohfy__Order_Date__c": "txn_date",
      "ohfy__QB_Sync_Status__c": "sync_status"
    },
    erp: {
      "ohfy__External_ID__c": "erp_order_id",
      "ohfy__ERP_System_ID__c": "system_identifier",
      "ohfy__Warehouse_Location__c": "fulfillment_location"
    }
  },

  // Validation rules that affect integrations
  validationRules: [
    {
      name: "Order_Date_Not_Future",
      condition: "ohfy__Order_Date__c > TODAY()",
      message: "Order date cannot be in the future"
    },
    {
      name: "Required_Customer",
      condition: "ISBLANK(ohfy__Customer__c)",
      message: "Customer is required"
    }
  ],

  // Automation that triggers on record creation/update
  automationTriggers: [
    "TA_Order_AI_GoalInvoiceCreator",    // Goal tracking and invoice generation
    "TA_Order_AU_NameSetter",            // Order name auto-generation
    "TA_Order_AI_DeliveryAssociator"     // Delivery relationship logic
  ]
};
```

#### **ohfy__Order_Item__c**
```javascript
const OrderItemConfiguration = {
  object: "ohfy__Order_Item__c",

  // Required fields for integration
  requiredFields: [
    "ohfy__External_ID__c",
    "ohfy__Order__c",           // Master-Detail(ohfy__Order__c)
    "ohfy__Item__c",            // Lookup(ohfy__Item__c)
    "ohfy__Ordered_Quantity__c",
    "ohfy__Unit_Price__c"
  ],

  // Auto-calculated fields
  calculatedFields: {
    "ohfy__Sub_Total__c": "ohfy__Ordered_Quantity__c * ohfy__Unit_Price__c"
  },

  // Read-only fields
  readOnlyFields: [
    "ohfy__Order_Item_Number__c",  // Auto-number
    "ohfy__Outstanding_Quantity__c", // Formula
    "Name",                        // Auto-generated
    "CreatedDate",
    "LastModifiedDate"
  ],

  // Item validation constraints
  itemConstraints: {
    activeItemsOnly: true,
    excludeTypes: ["Keg Shell"],    // From U_Order_Items.cls logic
    inventoryCheck: true
  },

  // External system mappings
  externalMappings: {
    edi: {
      "ohfy__External_ID__c": "line_item_id",
      "ohfy__UPC_Code__c": "product_upc",
      "ohfy__Ordered_Quantity__c": "quantity_ordered",
      "ohfy__Unit_Price__c": "unit_price"
    },
    inventory: {
      "ohfy__Item_SKU__c": "sku",
      "ohfy__Warehouse_Location__c": "location_code",
      "ohfy__Lot_Number__c": "batch_id"
    }
  }
};
```

#### **ohfy__Credit__c**
```javascript
const CreditConfiguration = {
  object: "ohfy__Credit__c",

  // Required fields for integration
  requiredFields: [
    "ohfy__External_ID__c",
    "ohfy__Account__c",         // Master-Detail(Account)
    "ohfy__Amount__c"
  ],

  // Amount validation
  amountConstraints: {
    minimumAmount: 0,           // Must be non-negative
    maximumAmount: null,        // No upper limit
    decimalPlaces: 2
  },

  // Credit type picklist values
  creditTypeValues: [
    "Payment",
    "Refund",
    "Adjustment",
    "Discount",
    "Write-off"
  ],

  // External system mappings
  externalMappings: {
    accounting: {
      "ohfy__External_ID__c": "payment_id",
      "ohfy__Credit_Type__c": "payment_type",
      "ohfy__Reference_Number__c": "check_number"
    }
  }
};
```

### Extended Objects (Org-Specific)

#### **Maps Integration Objects**
```javascript
const MapsConfiguration = {
  // B_Maps custom classes for route optimization
  customClasses: [
    "B_Maps_RouteBuilder",      // Route optimization logic
    "B_Maps_RouteBuilder_T"     // Test class for route builder
  ],

  // Maps package integration
  mapsObjects: [
    "maps__LiveAsset__c",       // Live tracking assets
    "maps__Route__c",           // Delivery routes
    "maps__Stop__c"             // Route stops
  ],

  // Integration points with OHFY orders
  integrationFields: {
    "ohfy__Order__c": {
      "maps__Route__c": "Route_Assignment__c",
      "maps__Stop_Sequence__c": "Delivery_Sequence__c",
      "maps__Estimated_Arrival__c": "ETA__c"
    }
  }
};
```

### Payment and Finance Configuration

#### **Payment Methods**
```javascript
const PaymentConfiguration = {
  // Valid payment method picklist values
  paymentMethods: [
    "Check",
    "Cash",
    "EFT",
    "Quickbooks Electronic Invoice",
    "Ohanafy"
  ],

  // Valid payment terms
  paymentTerms: [
    "Due on Receipt",
    "10 Days",
    "15 Days",
    "20 Days",
    "30 Days",
    "60 Days",
    "90 Days",
    "Custom"
  ],

  // QuickBooks integration mappings
  quickbooksMapping: {
    "Check": "Check",
    "Cash": "Cash",
    "EFT": "Electronic Bank Transfer",
    "Quickbooks Electronic Invoice": "Electronic Invoice",
    "Ohanafy": "Other"
  }
};
```

---

## 🔧 Environment-Specific Configurations

### Development Environment
```javascript
const DevEnvironmentConfig = {
  environment: "development",

  // Modified picklist values for testing
  testStatusValues: [
    "Test - New",
    "Test - In Progress",
    "Test - Complete"
  ],

  // Test data prefixes
  externalIdPrefix: "DEV-",

  // Relaxed validation rules
  skipValidation: [
    "Order_Date_Not_Future",
    "Required_Delivery_Date"
  ],

  // Test user assignments
  defaultSalesRep: "005XX000001TEST",
  defaultCustomer: "003XX000004TEST"
};
```

### Staging Environment
```javascript
const StagingEnvironmentConfig = {
  environment: "staging",

  // Production-like configuration for final testing
  enforceAllValidation: true,

  // Staging-specific external ID prefix
  externalIdPrefix: "STG-",

  // Limited user set for testing
  allowedUsers: [
    "005XX000001STAG1",
    "005XX000001STAG2"
  ]
};
```

---

## 📊 Field Type Reference

### Data Type Mappings
```javascript
const FieldTypeMapping = {
  // Salesforce to JavaScript type conversion
  "Text": "string",
  "Text Area": "string",
  "Rich Text Area": "string",
  "Number": "number",
  "Currency": "number",
  "Percent": "number",
  "Date": "string",          // YYYY-MM-DD format
  "Date/Time": "string",     // ISO 8601 format
  "Checkbox": "boolean",
  "Picklist": "string",      // Must match exact values
  "Multi-Select Picklist": "string", // Semicolon-separated
  "Lookup": "string",        // Salesforce ID (18 chars)
  "Master-Detail": "string", // Salesforce ID (18 chars)
  "Formula": null,           // Read-only, cannot be set
  "Rollup Summary": null,    // Read-only, cannot be set
  "Auto Number": null        // Read-only, system-generated
};
```

### Field Length Limits
```javascript
const FieldLengthLimits = {
  "ohfy__External_ID__c": 255,      // Standard external ID field
  "Name": 80,                       // Standard name field
  "ohfy__Description__c": 32000,    // Long text area
  "ohfy__Notes__c": 1000,           // Standard text area
  "ohfy__Customer_Reference__c": 100 // Customer PO numbers, etc.
};
```

---

## 🚨 Integration Constraints

### API Limits and Considerations
```javascript
const APIConstraints = {
  // Salesforce API limits
  dailyAPILimit: 15000,           // Typical org limit
  bulkAPIBatchSize: 10000,        // Maximum records per batch
  restAPIBatchSize: 200,          // Maximum records per REST call

  // SOQL query limits
  maxSOQLResults: 50000,          // Standard SOQL limit
  maxSOQLComplexity: 20,          // Maximum relationship depth

  // Governor limits in automation
  maxDMLOperations: 150,          // Per transaction
  maxSOQLQueries: 100,            // Per transaction
  maxCPUTime: 10000              // Milliseconds
};
```

### Bulk Operation Configuration
```javascript
const BulkOperationConfig = {
  // Recommended batch sizes by object
  batchSizes: {
    "ohfy__Order__c": 100,        // Conservative due to automation
    "ohfy__Order_Item__c": 200,   // Simpler object, larger batches
    "ohfy__Credit__c": 500,       // Simple object, largest batches
    "Account": 50                 // Complex standard object
  },

  // Retry configuration
  retryConfig: {
    maxRetries: 3,
    retryDelay: 1000,             // Milliseconds
    backoffMultiplier: 2
  },

  // Error handling
  continueOnError: true,          // Process remaining records on partial failure
  storeFailedRecords: true        // Keep failed records for retry
};
```

---

## 🔍 Org-Specific Business Rules

### Distro Production Business Rules
```javascript
const DistroBusinessRules = {
  // Order processing rules
  orderRules: {
    requireDeliveryDate: true,
    allowBackorders: false,
    autoAssignSalesRep: true,
    generateInvoiceOnComplete: true
  },

  // Inventory management
  inventoryRules: {
    checkAvailability: true,
    reserveOnOrder: true,
    allowPartialShipments: false
  },

  // Customer-specific rules
  customerRules: {
    requireAccountSetup: true,
    validateCreditLimit: true,
    enforcePricingTiers: true
  },

  // Integration-specific rules
  integrationRules: {
    requireExternalID: true,
    validateDuplicates: true,
    logAllChanges: true,
    notifyOnFailure: true
  }
};
```

### Custom Validation Rules
```javascript
const CustomValidationRules = {
  // Order validation
  "Order_Date_Required": {
    object: "ohfy__Order__c",
    condition: "ISBLANK(ohfy__Order_Date__c)",
    message: "Order Date is required",
    bypassProfiles: ["System Administrator"]
  },

  // Order Item validation
  "Positive_Quantity_Required": {
    object: "ohfy__Order_Item__c",
    condition: "ohfy__Ordered_Quantity__c <= 0",
    message: "Ordered quantity must be greater than zero"
  },

  // Credit validation
  "Positive_Credit_Amount": {
    object: "ohfy__Credit__c",
    condition: "ohfy__Amount__c < 0",
    message: "Credit amount must be positive"
  }
};
```

---

## 🛠️ Usage in Integration Scripts

### Loading Org Configuration
```javascript
// In your consolidated Script Connector
function loadOrgConfiguration(environment = 'production') {
  const configs = {
    production: {
      orders: OrderConfiguration,
      orderItems: OrderItemConfiguration,
      credits: CreditConfiguration,
      payments: PaymentConfiguration,
      businessRules: DistroBusinessRules,
      apiConstraints: APIConstraints
    },
    development: {
      ...ProductionConfig,
      ...DevEnvironmentConfig
    },
    staging: {
      ...ProductionConfig,
      ...StagingEnvironmentConfig
    }
  };

  return configs[environment] || configs.production;
}

// Usage in script
const orgConfig = loadOrgConfiguration(input.config.environment);

// Validate against org-specific picklist values
if (!orgConfig.orders.statusPicklistValues.includes(orderData['ohfy__Status__c'])) {
  throw new Error(`Invalid status: ${orderData['ohfy__Status__c']}`);
}
```

### Dynamic Field Validation
```javascript
function validateFieldConstraints(sobject, fieldData, orgConfig) {
  const objectConfig = orgConfig[sobject.toLowerCase().replace('ohfy__', '').replace('__c', '')];
  const errors = [];

  // Check required fields
  for (const requiredField of objectConfig.requiredFields) {
    if (!fieldData[requiredField] && fieldData[requiredField] !== 0) {
      errors.push(`Missing required field: ${requiredField}`);
    }
  }

  // Check read-only fields
  for (const readOnlyField of objectConfig.readOnlyFields) {
    if (fieldData.hasOwnProperty(readOnlyField)) {
      errors.push(`Cannot set read-only field: ${readOnlyField}`);
    }
  }

  // Check picklist values
  if (sobject === 'ohfy__Order__c' && fieldData['ohfy__Status__c']) {
    if (!objectConfig.statusPicklistValues.includes(fieldData['ohfy__Status__c'])) {
      errors.push(`Invalid status: ${fieldData['ohfy__Status__c']}`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
}
```

### Environment-Specific Processing
```javascript
function processWithOrgConstraints(records, orgConfig) {
  const batchSize = orgConfig.apiConstraints.restAPIBatchSize;
  const batches = chunkArray(records, batchSize);

  return Promise.all(batches.map(async (batch) => {
    // Apply org-specific business rules
    const processedBatch = batch.map(record => {
      if (orgConfig.businessRules.requireExternalID) {
        record['ohfy__External_ID__c'] = record['ohfy__External_ID__c'] || generateExternalId();
      }

      return record;
    });

    return await connectors.salesforce.batch_create_records({
      authId: config.authIds.salesforce,
      sobject: 'ohfy__Order__c',
      records: processedBatch
    });
  }));
}
```

---

**Related Guides:**
- **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)** - Business logic that uses these configurations
- **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** - Implementation patterns using org configurations
- **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)** - API operations with org-specific parameters