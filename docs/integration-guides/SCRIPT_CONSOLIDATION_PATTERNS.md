# Script Consolidation Patterns

**Complete JavaScript Templates for Single-Script OHFY Integrations**

Transform complex multi-workflow integrations into maintainable, consolidated Script Connector implementations.

---

## 🎯 Core Consolidation Philosophy

### From This (Complex):
```
Trigger → Script 1 → Connector A → Script 2 → Connector B → Script 3 → Connector C
         ↓
Loop → Script 4 → Condition → Script 5 → Branch → Script 6 → Error Handler
         ↓
Parallel → Script 7 → Storage → Script 8 → Cleanup → Script 9
```

### To This (Consolidated):
```
Trigger → Master Script Connector → [All Logic + API Orchestration] → Results
```

---

## 📋 Base Template Structure

### Master Script Pattern
```javascript
/**
 * Consolidated Integration Script Template
 * Handles complete business process in single execution context
 */
exports.step = async function(input, fileInput) {
  // Configuration and setup
  const config = setupConfiguration(input);
  const logger = createLogger(config);

  try {
    // Phase 1: Data Extraction and Validation
    const sourceData = await extractAndValidateInput(input, config, logger);

    // Phase 2: Business Logic and Transformation
    const processedData = await applyBusinessLogic(sourceData, config, logger);

    // Phase 3: API Orchestration
    const results = await executeAPIOperations(processedData, config, logger);

    // Phase 4: Results Processing and Cleanup
    const finalResults = await processResults(results, config, logger);

    logger.info('Integration completed successfully', { recordCount: finalResults.length });
    return finalResults;

  } catch (error) {
    return await handleIntegrationError(error, config, logger);
  }
};

// Core utility functions
function setupConfiguration(input) {
  return {
    // Environment settings
    environment: input.config?.environment || 'production',
    testMode: input.config?.testRun || false,
    batchSize: input.config?.batchSize || 100,

    // Integration-specific config
    authIds: {
      salesforce: input.config?.salesforceAuthId,
      external: input.config?.externalAuthId
    },

    // Business rules
    fieldMappings: input.config?.fieldMappings || {},
    validationRules: input.config?.validationRules || {},
    transformationRules: input.config?.transformationRules || {}
  };
}

function createLogger(config) {
  return {
    info: (message, data) => console.log(`[INFO] ${message}`, data || ''),
    warn: (message, data) => console.log(`[WARN] ${message}`, data || ''),
    error: (message, data) => console.log(`[ERROR] ${message}`, data || ''),
    debug: (message, data) => {
      if (config.testMode) console.log(`[DEBUG] ${message}`, data || '');
    }
  };
}
```

---

## 🏭 Pattern 1: EDI Document Processing

### Complete EDI Integration (810/856 Documents)
```javascript
/**
 * Consolidated EDI Integration
 * Replaces: 8 workflows with 22 script connectors
 * Handles: Document parsing → Validation → OHFY transformation → Salesforce sync
 */
exports.step = async function(input, fileInput) {
  const config = setupEDIConfiguration(input);
  const logger = createLogger(config);

  try {
    // Phase 1: Document extraction and parsing
    const documents = await extractEDIDocuments(input, config, logger);

    // Phase 2: Document validation and business rules
    const validatedDocs = await validateEDIDocuments(documents, config, logger);

    // Phase 3: Transform to OHFY format
    const ohfyRecords = await transformEDIToOHFY(validatedDocs, config, logger);

    // Phase 4: Salesforce operations
    const salesforceResults = await syncToSalesforce(ohfyRecords, config, logger);

    // Phase 5: Generate outbound documents (if required)
    const outboundDocs = await generateOutboundDocuments(salesforceResults, config, logger);

    return {
      documentsProcessed: documents.length,
      recordsCreated: salesforceResults.created.length,
      recordsUpdated: salesforceResults.updated.length,
      outboundGenerated: outboundDocs.length,
      errors: salesforceResults.errors || []
    };

  } catch (error) {
    return await handleEDIError(error, config, logger);
  }
};

// EDI-specific utility functions
async function extractEDIDocuments(input, config, logger) {
  logger.info('Extracting EDI documents');

  // Handle different input types (S3, SFTP, direct payload)
  if (input.s3Objects) {
    return await extractFromS3(input.s3Objects, config);
  } else if (input.ftpFiles) {
    return await extractFromFTP(input.ftpFiles, config);
  } else if (input.payload) {
    return await parseEDIPayload(input.payload, config);
  }

  throw new Error('No valid EDI input source found');
}

async function validateEDIDocuments(documents, config, logger) {
  logger.info('Validating EDI documents', { count: documents.length });

  const validatedDocs = [];
  const errors = [];

  for (const doc of documents) {
    try {
      // Apply EDI validation rules
      const validationResult = await validateEDIStructure(doc, config);

      if (validationResult.isValid) {
        // Apply business-specific validations
        const businessValidation = await applyEDIBusinessRules(doc, config);

        if (businessValidation.isValid) {
          validatedDocs.push({
            ...doc,
            validationResults: { ...validationResult, ...businessValidation }
          });
        } else {
          errors.push({ document: doc.id, errors: businessValidation.errors });
        }
      } else {
        errors.push({ document: doc.id, errors: validationResult.errors });
      }
    } catch (error) {
      errors.push({ document: doc.id, error: error.message });
    }
  }

  if (errors.length > 0) {
    logger.warn('EDI validation errors found', { errorCount: errors.length });
    // Store errors for review but continue processing valid documents
    await storeValidationErrors(errors, config);
  }

  return validatedDocs;
}

async function transformEDIToOHFY(documents, config, logger) {
  logger.info('Transforming EDI to OHFY format');

  const ohfyRecords = {
    invoices: [],
    deliveries: [],
    orderItems: [],
    adjustments: []
  };

  for (const doc of documents) {
    switch (doc.type) {
      case '810': // Invoice
        const invoiceRecords = await transformInvoiceEDI(doc, config);
        ohfyRecords.invoices.push(...invoiceRecords);
        break;

      case '856': // Advance Ship Notice
        const deliveryRecords = await transformDeliveryEDI(doc, config);
        ohfyRecords.deliveries.push(...deliveryRecords);
        break;

      default:
        logger.warn('Unknown EDI document type', { type: doc.type });
    }
  }

  return ohfyRecords;
}

async function syncToSalesforce(ohfyRecords, config, logger) {
  logger.info('Syncing to Salesforce');

  const results = { created: [], updated: [], errors: [] };

  // Process in dependency order: Invoices → Deliveries → Order Items → Adjustments
  if (ohfyRecords.invoices.length > 0) {
    const invoiceResults = await bulkUpsertSalesforce('ohfy__Invoice__c', ohfyRecords.invoices, config);
    results.created.push(...invoiceResults.created);
    results.updated.push(...invoiceResults.updated);
    results.errors.push(...invoiceResults.errors);
  }

  if (ohfyRecords.deliveries.length > 0) {
    const deliveryResults = await bulkUpsertSalesforce('ohfy__Delivery__c', ohfyRecords.deliveries, config);
    results.created.push(...deliveryResults.created);
    results.updated.push(...deliveryResults.updated);
    results.errors.push(...deliveryResults.errors);
  }

  // Continue with other record types...

  return results;
}
```

---

## 🏦 Pattern 2: Accounting System Sync

### Complete QuickBooks Integration
```javascript
/**
 * Consolidated QuickBooks Integration
 * Replaces: 22 workflows with scattered business logic
 * Handles: Bidirectional sync with complete business rules
 */
exports.step = async function(input, fileInput) {
  const config = setupAccountingConfiguration(input);
  const logger = createLogger(config);

  try {
    // Phase 1: Extract data from both systems
    const sourceData = await extractAccountingData(config, logger);

    // Phase 2: Apply business rules and mapping
    const processedData = await applyAccountingBusinessLogic(sourceData, config, logger);

    // Phase 3: Execute bidirectional sync
    const syncResults = await executeBidirectionalSync(processedData, config, logger);

    // Phase 4: Reconciliation and reporting
    const reconciliation = await performReconciliation(syncResults, config, logger);

    return {
      salesforceUpdates: syncResults.salesforce,
      quickbooksUpdates: syncResults.quickbooks,
      reconciliation: reconciliation,
      summary: generateSyncSummary(syncResults)
    };

  } catch (error) {
    return await handleAccountingError(error, config, logger);
  }
};

async function extractAccountingData(config, logger) {
  logger.info('Extracting data from both systems');

  // Parallel data extraction
  const [salesforceData, quickbooksData] = await Promise.all([
    extractSalesforceData(config),
    extractQuickBooksData(config)
  ]);

  return {
    salesforce: {
      invoices: salesforceData.invoices,
      payments: salesforceData.payments,
      customers: salesforceData.customers,
      items: salesforceData.items
    },
    quickbooks: {
      invoices: quickbooksData.invoices,
      payments: quickbooksData.payments,
      customers: quickbooksData.customers,
      items: quickbooksData.items
    }
  };
}

async function applyAccountingBusinessLogic(sourceData, config, logger) {
  logger.info('Applying accounting business rules');

  // Business rule: Split invoices by company/division
  const splitInvoices = await applySplitInvoiceRules(sourceData.salesforce.invoices, config);

  // Business rule: Map chart of accounts
  const mappedAccounts = await applyChartOfAccountsMapping(sourceData, config);

  // Business rule: Handle payment matching
  const matchedPayments = await applyPaymentMatchingRules(sourceData, config);

  // Business rule: Apply customer/vendor mapping
  const mappedEntities = await applyEntityMapping(sourceData, config);

  return {
    ...sourceData,
    processed: {
      splitInvoices,
      mappedAccounts,
      matchedPayments,
      mappedEntities
    }
  };
}

async function executeBidirectionalSync(processedData, config, logger) {
  logger.info('Executing bidirectional sync');

  const results = {
    salesforce: { created: [], updated: [], errors: [] },
    quickbooks: { created: [], updated: [], errors: [] }
  };

  // Sync Salesforce → QuickBooks
  if (config.syncToQuickBooks) {
    const qbResults = await syncSalesforceToQuickBooks(processedData, config, logger);
    results.quickbooks = qbResults;
  }

  // Sync QuickBooks → Salesforce
  if (config.syncToSalesforce) {
    const sfResults = await syncQuickBooksToSalesforce(processedData, config, logger);
    results.salesforce = sfResults;
  }

  return results;
}

async function syncSalesforceToQuickBooks(processedData, config, logger) {
  const results = { created: [], updated: [], errors: [] };

  // Process invoices
  for (const invoice of processedData.processed.splitInvoices) {
    try {
      const qbInvoiceData = await transformSFToQBInvoice(invoice, config);

      if (invoice.qbId) {
        // Update existing
        const updateResult = await connectors.quickbooks.update_invoice({
          authId: config.authIds.quickbooks,
          id: invoice.qbId,
          invoice: qbInvoiceData
        });
        results.updated.push(updateResult);
      } else {
        // Create new
        const createResult = await connectors.quickbooks.create_invoice({
          authId: config.authIds.quickbooks,
          invoice: qbInvoiceData
        });
        results.created.push(createResult);

        // Update Salesforce with QB ID
        await connectors.salesforce.update_record({
          authId: config.authIds.salesforce,
          sobject: 'ohfy__Invoice__c',
          id: invoice.id,
          fields: { 'QuickBooks_ID__c': createResult.id }
        });
      }
    } catch (error) {
      results.errors.push({ invoice: invoice.id, error: error.message });
    }
  }

  return results;
}
```

---

## 🔄 Pattern 3: Real-Time Data Pipeline

### Webhook Processing with Multiple Destinations
```javascript
/**
 * Consolidated Real-Time Data Pipeline
 * Replaces: Multiple workflows with complex dependencies
 * Handles: Webhook → Validation → Transformation → Multiple destinations
 */
exports.step = async function(input, fileInput) {
  const config = setupPipelineConfiguration(input);
  const logger = createLogger(config);

  try {
    // Phase 1: Webhook payload processing
    const webhook = await processWebhookPayload(input, config, logger);

    // Phase 2: Business logic and validation
    const validatedData = await validateAndTransform(webhook, config, logger);

    // Phase 3: Parallel destination updates
    const destinationResults = await updateMultipleDestinations(validatedData, config, logger);

    // Phase 4: Status reporting and notifications
    const notifications = await sendStatusNotifications(destinationResults, config, logger);

    return {
      webhook: webhook.metadata,
      destinations: destinationResults,
      notifications: notifications,
      processingTime: Date.now() - webhook.timestamp
    };

  } catch (error) {
    return await handlePipelineError(error, config, logger);
  }
};

async function processWebhookPayload(input, config, logger) {
  logger.info('Processing webhook payload');

  // Extract webhook metadata
  const webhook = {
    source: input.headers?.['x-webhook-source'] || 'unknown',
    eventType: input.headers?.['x-event-type'] || input.data?.eventType,
    timestamp: Date.now(),
    payload: input.data || input.body,
    metadata: {
      id: input.headers?.['x-request-id'] || generateRequestId(),
      retryCount: parseInt(input.headers?.['x-retry-count'] || '0'),
      signature: input.headers?.['x-signature']
    }
  };

  // Validate webhook signature if required
  if (config.requireSignatureValidation) {
    await validateWebhookSignature(webhook, config);
  }

  // Deduplicate webhook if required
  if (config.enableDeduplication) {
    const isDuplicate = await checkForDuplicate(webhook.metadata.id, config);
    if (isDuplicate) {
      throw new Error(`Duplicate webhook detected: ${webhook.metadata.id}`);
    }
  }

  return webhook;
}

async function validateAndTransform(webhook, config, logger) {
  logger.info('Validating and transforming data');

  // Apply event-specific validation
  const validationRules = config.validationRules[webhook.eventType] || config.validationRules.default;
  const validationResult = await applyValidationRules(webhook.payload, validationRules);

  if (!validationResult.isValid) {
    throw new Error(`Validation failed: ${validationResult.errors.join(', ')}`);
  }

  // Apply transformations for each destination
  const transformedData = {};

  for (const destination of config.destinations) {
    const transformationRules = config.transformationRules[destination.name];
    transformedData[destination.name] = await applyTransformation(
      webhook.payload,
      transformationRules,
      destination.schema
    );
  }

  return {
    webhook,
    transformedData,
    validationResult
  };
}

async function updateMultipleDestinations(data, config, logger) {
  logger.info('Updating multiple destinations');

  const destinationPromises = config.destinations.map(async (destination) => {
    try {
      const destinationData = data.transformedData[destination.name];

      switch (destination.type) {
        case 'salesforce':
          return await updateSalesforceDestination(destinationData, destination, config);

        case 'external-api':
          return await updateExternalAPIDestination(destinationData, destination, config);

        case 'database':
          return await updateDatabaseDestination(destinationData, destination, config);

        case 'storage':
          return await updateStorageDestination(destinationData, destination, config);

        default:
          throw new Error(`Unknown destination type: ${destination.type}`);
      }
    } catch (error) {
      return {
        destination: destination.name,
        success: false,
        error: error.message
      };
    }
  });

  const results = await Promise.allSettled(destinationPromises);

  return results.map((result, index) => ({
    destination: config.destinations[index].name,
    success: result.status === 'fulfilled',
    data: result.status === 'fulfilled' ? result.value : null,
    error: result.status === 'rejected' ? result.reason : null
  }));
}
```

---

## 📊 Pattern 4: Batch Data Synchronization

### Scheduled Bulk Operations
```javascript
/**
 * Consolidated Batch Synchronization
 * Replaces: Nested loops across multiple workflows
 * Handles: Bulk extraction → Processing → Validation → Upload → Reconciliation
 */
exports.step = async function(input, fileInput) {
  const config = setupBatchConfiguration(input);
  const logger = createLogger(config);

  try {
    // Phase 1: Bulk data extraction
    const sourceData = await extractBulkData(config, logger);

    // Phase 2: Parallel processing with batching
    const processedBatches = await processBulkDataInBatches(sourceData, config, logger);

    // Phase 3: Bulk upload operations
    const uploadResults = await executeBulkUploads(processedBatches, config, logger);

    // Phase 4: Reconciliation and reporting
    const reconciliation = await performBulkReconciliation(uploadResults, config, logger);

    return {
      totalRecords: sourceData.length,
      batchesProcessed: processedBatches.length,
      uploadResults: uploadResults,
      reconciliation: reconciliation,
      executionTime: Date.now() - config.startTime
    };

  } catch (error) {
    return await handleBatchError(error, config, logger);
  }
};

async function extractBulkData(config, logger) {
  logger.info('Extracting bulk data');

  const extractionTasks = [];

  // Add data sources based on configuration
  if (config.sources.includes('salesforce')) {
    extractionTasks.push(extractSalesforceData(config));
  }

  if (config.sources.includes('external-api')) {
    extractionTasks.push(extractExternalAPIData(config));
  }

  if (config.sources.includes('file')) {
    extractionTasks.push(extractFileData(config));
  }

  if (config.sources.includes('database')) {
    extractionTasks.push(extractDatabaseData(config));
  }

  const results = await Promise.all(extractionTasks);

  // Combine and deduplicate data
  const combinedData = results.flat();
  const deduplicatedData = await deduplicateRecords(combinedData, config);

  logger.info('Data extraction completed', {
    totalRecords: combinedData.length,
    afterDeduplication: deduplicatedData.length
  });

  return deduplicatedData;
}

async function processBulkDataInBatches(sourceData, config, logger) {
  logger.info('Processing data in batches', { batchSize: config.batchSize });

  const batches = chunkArray(sourceData, config.batchSize);
  const processedBatches = [];

  // Process batches with concurrency control
  const concurrencyLimit = config.maxConcurrentBatches || 3;

  for (let i = 0; i < batches.length; i += concurrencyLimit) {
    const batchGroup = batches.slice(i, i + concurrencyLimit);

    const batchPromises = batchGroup.map(async (batch, batchIndex) => {
      const actualBatchIndex = i + batchIndex;
      logger.debug(`Processing batch ${actualBatchIndex + 1}/${batches.length}`);

      try {
        const processedRecords = [];
        const errors = [];

        for (const record of batch) {
          try {
            // Apply business logic and validation
            const validatedRecord = await validateRecord(record, config);

            if (validatedRecord.isValid) {
              const transformedRecord = await transformRecord(validatedRecord.data, config);
              processedRecords.push(transformedRecord);
            } else {
              errors.push({ record: record.id, errors: validatedRecord.errors });
            }
          } catch (error) {
            errors.push({ record: record.id, error: error.message });
          }
        }

        return {
          batchIndex: actualBatchIndex,
          processed: processedRecords,
          errors: errors,
          processedAt: new Date().toISOString()
        };

      } catch (error) {
        logger.error(`Batch ${actualBatchIndex} processing failed`, { error: error.message });
        throw error;
      }
    });

    const batchResults = await Promise.allSettled(batchPromises);

    batchResults.forEach((result, idx) => {
      if (result.status === 'fulfilled') {
        processedBatches.push(result.value);
      } else {
        logger.error(`Batch ${i + idx} failed`, { error: result.reason });
        // Store failed batch for retry
        processedBatches.push({
          batchIndex: i + idx,
          processed: [],
          errors: [{ batch: i + idx, error: result.reason }],
          failed: true
        });
      }
    });

    // Rate limiting between batch groups
    if (i + concurrencyLimit < batches.length) {
      await sleep(config.batchDelayMs || 1000);
    }
  }

  return processedBatches;
}

async function executeBulkUploads(processedBatches, config, logger) {
  logger.info('Executing bulk uploads');

  const uploadResults = {
    successful: [],
    failed: [],
    summary: {
      totalBatches: processedBatches.length,
      recordsProcessed: 0,
      recordsUploaded: 0,
      errors: []
    }
  };

  for (const batch of processedBatches) {
    if (batch.failed || batch.processed.length === 0) {
      uploadResults.failed.push(batch);
      continue;
    }

    try {
      // Execute bulk upload based on destination type
      let uploadResult;

      switch (config.destination.type) {
        case 'salesforce':
          uploadResult = await bulkUploadToSalesforce(batch.processed, config, logger);
          break;

        case 'external-api':
          uploadResult = await bulkUploadToExternalAPI(batch.processed, config, logger);
          break;

        case 'database':
          uploadResult = await bulkUploadToDatabase(batch.processed, config, logger);
          break;

        default:
          throw new Error(`Unknown destination type: ${config.destination.type}`);
      }

      uploadResults.successful.push({
        ...batch,
        uploadResult
      });

      uploadResults.summary.recordsProcessed += batch.processed.length;
      uploadResults.summary.recordsUploaded += uploadResult.successful?.length || 0;

      if (uploadResult.errors) {
        uploadResults.summary.errors.push(...uploadResult.errors);
      }

    } catch (error) {
      logger.error(`Bulk upload failed for batch ${batch.batchIndex}`, { error: error.message });
      uploadResults.failed.push({
        ...batch,
        uploadError: error.message
      });
    }
  }

  return uploadResults;
}

// Utility functions
function chunkArray(array, chunkSize) {
  const chunks = [];
  for (let i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize));
  }
  return chunks;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function generateRequestId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
```

---

## 🛠️ Common Utility Functions

### Error Handling Framework
```javascript
async function handleIntegrationError(error, config, logger) {
  logger.error('Integration error occurred', {
    message: error.message,
    stack: error.stack
  });

  // Categorize error type
  const errorType = categorizeError(error);

  // Apply error handling strategy
  switch (errorType) {
    case 'VALIDATION_ERROR':
      return await handleValidationError(error, config, logger);

    case 'API_ERROR':
      return await handleAPIError(error, config, logger);

    case 'BUSINESS_LOGIC_ERROR':
      return await handleBusinessLogicError(error, config, logger);

    case 'SYSTEM_ERROR':
      return await handleSystemError(error, config, logger);

    default:
      return await handleUnknownError(error, config, logger);
  }
}

function categorizeError(error) {
  if (error.message.includes('validation')) return 'VALIDATION_ERROR';
  if (error.message.includes('API') || error.code >= 400) return 'API_ERROR';
  if (error.message.includes('business rule')) return 'BUSINESS_LOGIC_ERROR';
  if (error.message.includes('system') || error.code < 0) return 'SYSTEM_ERROR';
  return 'UNKNOWN_ERROR';
}
```

### Configuration Management
```javascript
function setupConfiguration(input) {
  // Merge default config with input config
  const defaultConfig = {
    environment: 'production',
    testMode: false,
    batchSize: 100,
    maxRetries: 3,
    timeoutMs: 30000,
    logLevel: 'info'
  };

  const userConfig = input.config || {};

  return {
    ...defaultConfig,
    ...userConfig,
    // Ensure required fields are present
    authIds: {
      salesforce: userConfig.salesforceAuthId || input.authId,
      ...userConfig.authIds
    },
    startTime: Date.now()
  };
}
```

---

## 📈 Performance Optimization Tips

### 1. **Batch Processing**
- Always process records in configurable batches
- Use Promise.allSettled() for parallel processing with error isolation
- Implement rate limiting between batch groups

### 2. **Memory Management**
- Process large datasets in streams rather than loading everything into memory
- Clear processed data from memory after each batch
- Use garbage collection hints in long-running scripts

### 3. **API Efficiency**
- Use bulk operations whenever possible (Salesforce Bulk API, etc.)
- Implement connection pooling for multiple API calls
- Cache frequently accessed reference data

### 4. **Error Recovery**
- Implement partial failure handling - continue processing valid records
- Store failed records for later retry
- Use exponential backoff for transient failures

---

## 🔍 Testing and Validation

### Unit Testing Pattern
```javascript
// Add to your script for testing individual functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    extractAndValidateInput,
    applyBusinessLogic,
    executeAPIOperations,
    processResults,
    handleIntegrationError
  };
}
```

### Integration Testing
```javascript
// Use CAPI tool to test connector operations
// node capi.js salesforce create_record '{"sobject":"ohfy__Order__c","fields":{"Name":"Test"}}'

// Use Tray Script Tester for complete script validation
// node run.js (with appropriate input.json)
```

---

**Next Steps:**
1. Choose appropriate pattern for your integration type
2. Customize configuration and business logic sections
3. Test with CAPI tool and Tray Script Tester
4. Deploy as single Script Connector workflow in Tray

**Related Guides:**
- **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)** - API schemas and examples
- **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)** - Reusable business logic modules
- **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** - Complete working examples