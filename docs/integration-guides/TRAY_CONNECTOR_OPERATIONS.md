# Tray Connector Operations Reference

**Complete Salesforce and External System Connector Schemas for OHFY Integrations**

---

## 🔧 Salesforce Connector (v8.6)

### Authentication Configuration
```javascript
// AuthId is managed by Tray - reference in connector calls
const authConfig = {
  authId: "your-salesforce-auth-id", // Configured in Tray dashboard
  // No manual authentication handling required
};
```

### Core CRUD Operations

#### **Create Record**
```javascript
// Operation: create_record
const result = await connectors.salesforce.create_record({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  fields: {
    "ohfy__Customer__c": "003XX000004TMM2",
    "ohfy__Order_Date__c": "2024-01-15",
    "ohfy__Status__c": "New",
    "ohfy__Sales_Rep__c": "005XX000001ABC1"
  }
});

// Response Format:
// {
//   id: "a01XX000007ABC1",
//   success: true,
//   errors: []
// }
```

#### **Update Record**
```javascript
// Operation: update_record
const result = await connectors.salesforce.update_record({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  id: "a01XX000007ABC1",
  fields: {
    "ohfy__Status__c": "In Progress",
    "ohfy__Delivery_Date__c": "2024-01-20"
  }
});
```

#### **Upsert Record (Create/Update)**
```javascript
// Operation: upsert_record
const result = await connectors.salesforce.upsert_record({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  external_id_field: "ohfy__External_ID__c",
  external_id_value: "EXT-ORDER-12345",
  fields: {
    "ohfy__Customer__c": "003XX000004TMM2",
    "ohfy__Order_Date__c": "2024-01-15"
  }
});
```

#### **Find Records (Query)**
```javascript
// Operation: find_records
const result = await connectors.salesforce.find_records({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  criteria: {
    "ohfy__Status__c": "New",
    "ohfy__Order_Date__c": "THIS_WEEK"
  },
  fields: ["Id", "Name", "ohfy__Customer__c", "ohfy__Status__c"]
});

// Response Format:
// {
//   records: [
//     {
//       Id: "a01XX000007ABC1",
//       Name: "ORDER-001234",
//       ohfy__Customer__c: "003XX000004TMM2",
//       ohfy__Status__c: "New"
//     }
//   ],
//   totalSize: 1
// }
```

#### **SOQL Query (Advanced)**
```javascript
// Operation: query
const result = await connectors.salesforce.query({
  authId: config.authIds.salesforce,
  query: `
    SELECT Id, Name, ohfy__Customer__r.Name, ohfy__Status__c
    FROM ohfy__Order__c
    WHERE ohfy__Order_Date__c = TODAY
    AND ohfy__Status__c IN ('New', 'Scheduled')
    ORDER BY CreatedDate DESC
    LIMIT 100
  `
});
```

### Bulk Operations (High Volume)

#### **Batch Create Records (Max 200)**
```javascript
// Operation: batch_create_records
const result = await connectors.salesforce.batch_create_records({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order_Item__c",
  records: [
    {
      "ohfy__Order__c": "a01XX000007ABC1",
      "ohfy__Item__c": "a02XX000008DEF2",
      "ohfy__Quantity__c": 10,
      "ohfy__Unit_Price__c": 25.50
    },
    {
      "ohfy__Order__c": "a01XX000007ABC1",
      "ohfy__Item__c": "a02XX000008DEF3",
      "ohfy__Quantity__c": 5,
      "ohfy__Unit_Price__c": 15.75
    }
  ]
});
```

#### **Bulk Upsert Records (CSV Format)**
```javascript
// Operation: bulk_upsert_records
const csvData = `ohfy__External_ID__c,ohfy__Customer__c,ohfy__Status__c
EXT-001,003XX000004TMM2,New
EXT-002,003XX000004TMM3,Scheduled`;

const result = await connectors.salesforce.bulk_upsert_records({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  external_id_field: "ohfy__External_ID__c",
  data: csvData,
  operation: "upsert"
});

// Returns job ID for monitoring
// {
//   id: "7504P00000hLI8xQAG",
//   object: "ohfy__Order__c",
//   state: "JobInProgress"
// }
```

#### **Monitor Bulk Job Status**
```javascript
// Operation: get_job_info
const jobStatus = await connectors.salesforce.get_job_info({
  authId: config.authIds.salesforce,
  job_id: "7504P00000hLI8xQAG"
});

// Response includes job state: JobInProgress, JobComplete, Failed
```

### Object Metadata Operations

#### **Describe Object Structure**
```javascript
// Operation: so_object_describe
const objectInfo = await connectors.salesforce.so_object_describe({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c"
});

// Returns complete field definitions, relationships, permissions
```

#### **Get Picklist Values**
```javascript
// Operation: get_picklist_item_details
const picklistValues = await connectors.salesforce.get_picklist_item_details({
  authId: config.authIds.salesforce,
  sobject: "ohfy__Order__c",
  field_name: "ohfy__Status__c"
});
```

---

## 📊 QuickBooks Connector

### Basic Operations
```javascript
// Create Customer
const customer = await connectors.quickbooks.create_customer({
  authId: config.authIds.quickbooks,
  customer: {
    Name: "ACME Corporation",
    CompanyName: "ACME Corp",
    BillAddr: {
      Line1: "123 Main St",
      City: "Anytown",
      CountrySubDivisionCode: "CA",
      PostalCode: "90210"
    }
  }
});

// Create Invoice
const invoice = await connectors.quickbooks.create_invoice({
  authId: config.authIds.quickbooks,
  invoice: {
    CustomerRef: { value: customer.id },
    Line: [
      {
        Amount: 100.00,
        DetailType: "SalesItemLineDetail",
        SalesItemLineDetail: {
          ItemRef: { value: "1" }
        }
      }
    ]
  }
});
```

---

## 📁 File and Storage Connectors

### AWS S3 Operations
```javascript
// List files
const files = await connectors.aws_s3.list_objects({
  authId: config.authIds.aws,
  bucket: "edi-001px000002obiwyao-production",
  prefix: "inbound/810/"
});

// Download file
const fileContent = await connectors.aws_s3.download_file({
  authId: config.authIds.aws,
  bucket: "edi-001px000002obiwyao-production",
  key: "inbound/810/invoice-12345.edi"
});
```

### Google Sheets Operations
```javascript
// Read spreadsheet data
const sheetData = await connectors.sheets.read_values({
  authId: config.authIds.google,
  spreadsheet_id: "1xOXYf4BpsWg7wrCGr0PG2Wj0HTlGsKr8MgiMPZmovHA",
  range: "Sheet1!A1:Z1000"
});

// Write data to sheet
const writeResult = await connectors.sheets.append_values({
  authId: config.authIds.google,
  spreadsheet_id: "1xOXYf4BpsWg7wrCGr0PG2Wj0HTlGsKr8MgiMPZmovHA",
  range: "Sheet1!A1",
  values: [
    ["Order ID", "Customer", "Status", "Amount"],
    ["ORD-001", "ACME Corp", "New", "1250.00"]
  ]
});
```

---

## 🔗 HTTP Client Connector

### External API Calls
```javascript
// Generic HTTP request
const apiResponse = await connectors.http_client.make_request({
  url: "https://api.external-system.com/v1/orders",
  method: "POST",
  headers: {
    "Authorization": "Bearer " + config.externalApiToken,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    order_id: "EXT-12345",
    customer_id: "CUST-001",
    items: orderItems
  })
});
```

---

## 🛠️ Utility Connectors

### Script Connector
```javascript
// Already implemented in consolidation patterns
// See SCRIPT_CONSOLIDATION_PATTERNS.md for complete examples
```

### Storage Connector (Session Data)
```javascript
// Store temporary data
await connectors.storage.set({
  key: "processing_batch_" + batchId,
  value: {
    startTime: Date.now(),
    recordCount: records.length,
    status: "processing"
  },
  ttl: 3600 // 1 hour expiration
});

// Retrieve stored data
const batchInfo = await connectors.storage.get({
  key: "processing_batch_" + batchId
});
```

### Loop Connector (Iteration)
```javascript
// Note: In consolidated scripts, use JavaScript loops instead
// This is only for traditional multi-step workflows

for (const record of records) {
  // Process each record in consolidated script
  await processRecord(record);
}
```

### Boolean Condition (Conditional Logic)
```javascript
// Note: In consolidated scripts, use JavaScript conditionals instead
// This is only for traditional multi-step workflows

if (record.status === "New" && record.amount > 1000) {
  await processHighValueOrder(record);
} else {
  await processStandardOrder(record);
}
```

---

## 📋 Common Connector Usage Patterns

### Error Handling in Connector Calls
```javascript
async function safeSalesforceOperation(operation, params) {
  try {
    const result = await connectors.salesforce[operation](params);

    if (result.success === false) {
      throw new Error(`Salesforce operation failed: ${result.errors.join(', ')}`);
    }

    return result;
  } catch (error) {
    logger.error(`Salesforce ${operation} failed`, {
      params: params,
      error: error.message
    });

    // Handle specific error types
    if (error.message.includes('DUPLICATE_VALUE')) {
      return await handleDuplicateError(operation, params);
    } else if (error.message.includes('REQUIRED_FIELD_MISSING')) {
      return await handleMissingFieldError(operation, params);
    }

    throw error;
  }
}
```

### Batch Processing Pattern
```javascript
async function processBatchWithConnector(records, batchSize = 100) {
  const batches = chunkArray(records, batchSize);
  const results = [];

  for (const batch of batches) {
    try {
      const batchResult = await connectors.salesforce.batch_create_records({
        authId: config.authIds.salesforce,
        sobject: "ohfy__Order__c",
        records: batch
      });

      results.push(...batchResult);

      // Rate limiting
      await sleep(1000); // 1 second between batches

    } catch (error) {
      logger.error(`Batch processing failed`, {
        batchIndex: batches.indexOf(batch),
        error: error.message
      });

      // Process individual records in failed batch
      for (const record of batch) {
        try {
          const singleResult = await connectors.salesforce.create_record({
            authId: config.authIds.salesforce,
            sobject: "ohfy__Order__c",
            fields: record
          });
          results.push(singleResult);
        } catch (singleError) {
          results.push({ error: singleError.message, record: record });
        }
      }
    }
  }

  return results;
}
```

### Parallel Connector Operations
```javascript
async function executeParallelOperations(data) {
  // Execute multiple connector operations in parallel
  const [salesforceResult, quickbooksResult, sheetsResult] = await Promise.allSettled([
    connectors.salesforce.create_record({
      authId: config.authIds.salesforce,
      sobject: "ohfy__Order__c",
      fields: data.salesforceOrder
    }),

    connectors.quickbooks.create_invoice({
      authId: config.authIds.quickbooks,
      invoice: data.quickbooksInvoice
    }),

    connectors.sheets.append_values({
      authId: config.authIds.google,
      spreadsheet_id: config.auditSpreadsheetId,
      range: "Audit!A1",
      values: [data.auditRow]
    })
  ]);

  return {
    salesforce: salesforceResult.status === 'fulfilled' ? salesforceResult.value : salesforceResult.reason,
    quickbooks: quickbooksResult.status === 'fulfilled' ? quickbooksResult.value : quickbooksResult.reason,
    audit: sheetsResult.status === 'fulfilled' ? sheetsResult.value : sheetsResult.reason
  };
}
```

---

## 🎯 Integration-Specific Connector Combinations

### EDI Processing Stack
```javascript
// Typical EDI integration connector sequence
const ediProcessingStack = {
  input: "aws_s3",           // Download EDI files
  processing: "script",      // Parse and transform EDI
  validation: "script",      // Business rule validation
  destination: "salesforce", // Create OHFY records
  output: "aws_s3",         // Upload response documents
  notification: "slack"      // Status notifications
};
```

### Accounting Sync Stack
```javascript
// Typical accounting integration connector sequence
const accountingSyncStack = {
  extraction: ["salesforce", "quickbooks"], // Parallel data extraction
  processing: "script",                     // Business logic and mapping
  sync: ["salesforce", "quickbooks"],       // Bidirectional updates
  reconciliation: "script",                 // Verify consistency
  reporting: "sheets"                       // Generate reports
};
```

### Real-time Pipeline Stack
```javascript
// Typical real-time integration connector sequence
const realtimePipelineStack = {
  trigger: "webhook",                    // External system trigger
  processing: "script",                  // Validation and transformation
  destinations: ["salesforce", "external"], // Multiple target systems
  storage: "storage",                    // Session data management
  notification: "slack"                  // Success/failure alerts
};
```

---

## 📚 Testing Connector Operations

### Using CAPI Tool for Testing
```bash
# Test Salesforce operations directly
cd /path/to/tray-connector-explorer/trayConnectorExplorer

# List available connectors
node capi.js list

# Get connector information
node capi.js info salesforce

# Test create operation
node capi.js salesforce create_record '{
  "sobject": "Account",
  "fields": {
    "Name": "Test Company",
    "Type": "Customer"
  }
}'

# Test query operation
node capi.js salesforce find_records '{
  "sobject": "Account",
  "criteria": {"Type": "Customer"},
  "fields": ["Id", "Name", "Type"]
}'
```

### Using Script Tester for Integration Testing
```bash
# Test complete integration logic
cd /path/to/tray-connector-explorer/trayConnectorExplorer

# Set up test data in input.json
# Add your script logic to script.js
# Run integration test
node run.js
```

---

## 🔧 Connector Configuration Best Practices

### 1. **AuthId Management**
- Use environment-specific AuthIds (dev, staging, production)
- Store AuthIds in Tray configuration, not hardcoded in scripts
- Validate AuthId availability before executing operations

### 2. **Error Handling**
- Always wrap connector calls in try-catch blocks
- Implement specific handling for common Salesforce errors
- Log sufficient detail for troubleshooting without exposing sensitive data

### 3. **Performance Optimization**
- Use batch operations for high-volume processing
- Implement rate limiting between API calls
- Use parallel operations where possible (Promise.allSettled)

### 4. **Data Validation**
- Validate data before sending to connectors
- Use object describe operations to understand field requirements
- Implement fallback values for optional fields

### 5. **Monitoring and Logging**
- Log all connector operations with sufficient detail
- Track success/failure rates for monitoring
- Implement alerting for critical operation failures

---

**Related Guides:**
- **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** - Complete JavaScript implementation examples
- **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)** - Business rule implementations
- **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** - End-to-end integration examples