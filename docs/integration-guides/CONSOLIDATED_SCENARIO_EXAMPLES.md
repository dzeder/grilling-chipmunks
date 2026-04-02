# Consolidated Scenario Examples

**Complete End-to-End Integration Examples Using Single-Script Architecture**

Real-world implementations showing how to consolidate complex multi-workflow integrations into maintainable single Script Connector solutions.

---

## 🏭 Scenario 1: EDI Document Processing (OpenText Integration)

### Original Architecture: 8 Workflows
Based on the actual EDI_OpenTextTBM integration with 43,719 lines of JSON configuration.

```
05.00 Run Dates On Demand → 03.00 810 Daily Schedule → 02.00 856 Every 15 mins
    ↓                            ↓                           ↓
02.01 856 Process Deliveries → 03.01 810 Process Complete Invoices → 04.00 Generate Outbound UFF
    ↓                            ↓                           ↓
04.01 Outbound to OpenText ← 05.00 Manually re-run orders ← Error Handling
```

### Consolidated Architecture: Single Script
```
S3 Trigger → Master EDI Script → Multiple API Operations → Results
```

### Complete Implementation

```javascript
/**
 * Consolidated EDI Integration Script
 * Replaces: 8 workflows with 22 script connectors
 * Handles: 810/856 EDI documents with complete business logic
 */
exports.step = async function(input, fileInput) {
  const config = setupEDIConfiguration(input);
  const logger = createLogger(config);

  try {
    logger.info('Starting consolidated EDI processing', {
      s3Bucket: config.s3_bucket,
      environment: config.environment,
      testRun: config.testRun
    });

    // Phase 1: Document Discovery and Extraction
    const discoveredDocuments = await discoverEDIDocuments(input, config, logger);

    // Phase 2: Document Processing and Validation
    const processedDocuments = await processEDIDocuments(discoveredDocuments, config, logger);

    // Phase 3: OHFY Data Transformation
    const ohfyRecords = await transformEDIToOHFY(processedDocuments, config, logger);

    // Phase 4: Salesforce Synchronization
    const salesforceResults = await syncEDIToSalesforce(ohfyRecords, config, logger);

    // Phase 5: Outbound Document Generation
    const outboundDocuments = await generateOutboundDocuments(salesforceResults, config, logger);

    // Phase 6: Results Processing and Notifications
    const finalResults = await processEDIResults(outboundDocuments, salesforceResults, config, logger);

    logger.info('EDI processing completed successfully', {
      documentsProcessed: discoveredDocuments.length,
      salesforceRecords: salesforceResults.totalRecords,
      outboundGenerated: outboundDocuments.length
    });

    return finalResults;

  } catch (error) {
    return await handleEDIError(error, config, logger);
  }
};

// Phase 1: Document Discovery and Extraction
async function discoverEDIDocuments(input, config, logger) {
  logger.info('Discovering EDI documents');

  // Handle different trigger types
  let s3Objects = [];

  if (input.s3_trigger) {
    // S3 bucket trigger - process specific files
    s3Objects = input.s3_trigger.Records || [];
  } else if (input.manual_run) {
    // Manual execution - discover files by date range
    const dateRange = calculateDateRange(config.invoiceStartDate, config.dateRange);

    s3Objects = await connectors.aws_s3.list_objects({
      authId: config.authIds.aws,
      bucket: config.s3_bucket,
      prefix: "inbound/",
      start_after: dateRange.start,
      end_before: dateRange.end
    });
  } else if (input.scheduled_run) {
    // Scheduled execution - process new files
    const lastRun = await getLastRunTimestamp(config);

    s3Objects = await connectors.aws_s3.list_objects({
      authId: config.authIds.aws,
      bucket: config.s3_bucket,
      prefix: "inbound/",
      modified_after: lastRun
    });
  }

  // Download and parse EDI files
  const documents = [];

  for (const s3Object of s3Objects) {
    try {
      const fileContent = await connectors.aws_s3.download_file({
        authId: config.authIds.aws,
        bucket: config.s3_bucket,
        key: s3Object.key
      });

      const parsedDocument = await parseEDIDocument(fileContent, s3Object.key, config);
      documents.push(parsedDocument);

    } catch (error) {
      logger.error('Failed to process S3 object', {
        key: s3Object.key,
        error: error.message
      });
    }
  }

  return documents;
}

// Phase 2: Document Processing and Validation
async function processEDIDocuments(documents, config, logger) {
  logger.info('Processing EDI documents', { count: documents.length });

  const processedDocuments = [];
  const errors = [];

  for (const document of documents) {
    try {
      // Apply document-specific processing
      let processedDoc;

      switch (document.type) {
        case '810': // Invoice
          processedDoc = await process810Invoice(document, config);
          break;

        case '856': // Advance Ship Notice
          processedDoc = await process856Delivery(document, config);
          break;

        default:
          throw new Error(`Unsupported document type: ${document.type}`);
      }

      // Apply business validations
      const validationResult = await validateEDIDocument(processedDoc, config);

      if (validationResult.isValid) {
        processedDocuments.push({
          ...processedDoc,
          validationPassed: true,
          validationResults: validationResult
        });
      } else {
        errors.push({
          document: document.id,
          errors: validationResult.errors
        });
      }

    } catch (error) {
      errors.push({
        document: document.id,
        error: error.message
      });
    }
  }

  // Store validation errors for review
  if (errors.length > 0) {
    await storeEDIErrors(errors, config);

    // Send Slack notification for critical errors
    await sendSlackNotification(config.channel, `EDI Validation Errors: ${errors.length} documents failed validation`, config);
  }

  return processedDocuments;
}

// Phase 3: OHFY Data Transformation
async function transformEDIToOHFY(documents, config, logger) {
  logger.info('Transforming EDI to OHFY format');

  const ohfyRecords = {
    invoices: [],
    deliveries: [],
    orderItems: [],
    adjustments: []
  };

  for (const document of documents) {
    try {
      switch (document.type) {
        case '810':
          const invoiceRecords = await transformInvoiceEDI(document, config);
          ohfyRecords.invoices.push(...invoiceRecords);
          break;

        case '856':
          const deliveryRecords = await transformDeliveryEDI(document, config);
          ohfyRecords.deliveries.push(...deliveryRecords);
          break;
      }
    } catch (error) {
      logger.error('EDI transformation failed', {
        documentId: document.id,
        error: error.message
      });
    }
  }

  return ohfyRecords;
}

// Phase 4: Salesforce Synchronization
async function syncEDIToSalesforce(ohfyRecords, config, logger) {
  logger.info('Syncing EDI data to Salesforce');

  const results = {
    invoices: { created: [], updated: [], errors: [] },
    deliveries: { created: [], updated: [], errors: [] },
    totalRecords: 0
  };

  // Process invoices first (parent records)
  if (ohfyRecords.invoices.length > 0) {
    results.invoices = await bulkUpsertSalesforce(
      'ohfy__Invoice__c',
      ohfyRecords.invoices,
      'ohfy__External_ID__c',
      config
    );
    results.totalRecords += results.invoices.created.length + results.invoices.updated.length;
  }

  // Process deliveries
  if (ohfyRecords.deliveries.length > 0) {
    results.deliveries = await bulkUpsertSalesforce(
      'ohfy__Delivery__c',
      ohfyRecords.deliveries,
      'ohfy__External_ID__c',
      config
    );
    results.totalRecords += results.deliveries.created.length + results.deliveries.updated.length;
  }

  return results;
}

// Configuration Setup
function setupEDIConfiguration(input) {
  return {
    // Environment settings
    environment: input.config?.environment || 'PROD',
    testRun: input.config?.testRun || false,
    integration: 'OpenText',

    // S3 Configuration
    s3_bucket: input.config?.s3_bucket || 'edi-001px000002obiwyao-production',
    region: 'us-east-1',

    // EDI Processing Configuration
    ediProvider: 'OpenText',
    invoiceStartDate: input.config?.invoiceStartDate || '2025-03-24',
    dateRange: input.config?.dateRange || 'daily',

    // UPC ignore list (from actual configuration)
    upcIgnore: [
      "754527000677", "071990170295", "840245600289", "840245600265",
      "840245600425", "028000231750", "087692012283", "071990005481"
      // ... full list from original config
    ],

    // Custom UPC mapping (from actual configuration)
    customUpcMapping: {
      "34100626396": "34100007683",
      "087692011385": "087692011682",
      "034100626396": "034100007683"
      // ... full mapping from original config
    },

    // Authentication IDs
    authIds: {
      salesforce: input.config?.salesforceAuthId,
      aws: input.config?.awsAuthId,
      slack: input.config?.slackAuthId
    },

    // Notification settings
    channel: input.config?.channel || 'C08NCGKAK27',
    missingDataTaskAssignees: [
      '005Hu00000RWUSlIAP',
      '005Hu00000RWvb5IAD'
    ]
  };
}

// Helper Functions
async function parseEDIDocument(content, filename, config) {
  // Parse EDI X12 format
  const segments = content.split('~');
  const documentType = extractDocumentType(segments);

  return {
    id: generateDocumentId(filename),
    type: documentType,
    filename: filename,
    segments: segments,
    parsedData: parseEDISegments(segments, documentType),
    processedAt: new Date().toISOString()
  };
}

async function process810Invoice(document, config) {
  // Process 810 invoice document
  const invoice = {
    externalId: document.parsedData.invoiceNumber,
    customerPO: document.parsedData.customerPO,
    invoiceDate: document.parsedData.invoiceDate,
    totalAmount: document.parsedData.totalAmount,
    lineItems: document.parsedData.lineItems
  };

  // Apply custom UPC mapping
  invoice.lineItems = invoice.lineItems.map(item => ({
    ...item,
    upc: config.customUpcMapping[item.upc] || item.upc
  }));

  // Filter ignored UPCs
  invoice.lineItems = invoice.lineItems.filter(item =>
    !config.upcIgnore.includes(item.upc)
  );

  return { ...document, processedInvoice: invoice };
}

async function bulkUpsertSalesforce(sobject, records, externalIdField, config) {
  const results = { created: [], updated: [], errors: [] };

  // Process in batches of 100
  const batchSize = 100;
  const batches = chunkArray(records, batchSize);

  for (const batch of batches) {
    try {
      const batchResult = await connectors.salesforce.bulk_upsert_records({
        authId: config.authIds.salesforce,
        sobject: sobject,
        external_id_field: externalIdField,
        records: batch
      });

      // Process results
      if (batchResult.success) {
        results.created.push(...(batchResult.created || []));
        results.updated.push(...(batchResult.updated || []));
      } else {
        results.errors.push(...(batchResult.errors || []));
      }

    } catch (error) {
      results.errors.push({
        batch: batches.indexOf(batch),
        error: error.message
      });
    }
  }

  return results;
}
```

---

## 💰 Scenario 2: QuickBooks Accounting Sync

### Original Architecture: 22 Workflows
Based on the actual Quickbooks_V6 integration.

### Consolidated Implementation

```javascript
/**
 * Consolidated QuickBooks Integration Script
 * Replaces: 22 workflows with scattered business logic
 * Handles: Bidirectional sync with complete accounting rules
 */
exports.step = async function(input, fileInput) {
  const config = setupQuickBooksConfiguration(input);
  const logger = createLogger(config);

  try {
    logger.info('Starting consolidated QuickBooks sync', {
      company: config.company,
      syncDirection: config.syncDirection,
      testMode: config.testMode
    });

    // Phase 1: Data Extraction from Both Systems
    const sourceData = await extractAccountingData(config, logger);

    // Phase 2: Business Logic and Data Processing
    const processedData = await applyAccountingBusinessLogic(sourceData, config, logger);

    // Phase 3: Bidirectional Synchronization
    const syncResults = await executeBidirectionalSync(processedData, config, logger);

    // Phase 4: Reconciliation and Reporting
    const reconciliation = await performAccountingReconciliation(syncResults, config, logger);

    // Phase 5: Notifications and Cleanup
    const notifications = await sendAccountingNotifications(reconciliation, config, logger);

    return {
      sourceRecords: sourceData.totalRecords,
      syncResults: syncResults,
      reconciliation: reconciliation,
      notifications: notifications
    };

  } catch (error) {
    return await handleAccountingError(error, config, logger);
  }
};

// Phase 1: Data Extraction
async function extractAccountingData(config, logger) {
  logger.info('Extracting data from both systems');

  const extractionPromises = [];

  // Extract Salesforce data
  extractionPromises.push(extractSalesforceAccountingData(config));

  // Extract QuickBooks data
  extractionPromises.push(extractQuickBooksData(config));

  const [salesforceData, quickbooksData] = await Promise.all(extractionPromises);

  return {
    salesforce: salesforceData,
    quickbooks: quickbooksData,
    totalRecords: salesforceData.length + quickbooksData.length
  };
}

async function extractSalesforceAccountingData(config) {
  // Query invoices for sync
  const invoiceQuery = `
    SELECT Id, Name, ohfy__Invoice_Number__c, ohfy__Invoice_Date__c,
           ohfy__Total_Amount__c, ohfy__Customer__r.Name, ohfy__QB_ID__c,
           ohfy__Status__c, ohfy__Payment_Status__c
    FROM ohfy__Invoice__c
    WHERE ohfy__Invoice_Date__c >= ${config.startDate}
    ${config.invoiceQuery}
    ORDER BY ohfy__Invoice_Date__c DESC
    LIMIT ${config.limit}
  `;

  const invoiceResult = await connectors.salesforce.query({
    authId: config.authIds.salesforce,
    query: invoiceQuery
  });

  // Query payments for sync
  const paymentQuery = `
    SELECT Id, Name, ohfy__Amount__c, ohfy__Payment_Date__c,
           ohfy__Invoice__r.ohfy__QB_ID__c, ohfy__QB_Payment_ID__c
    FROM ohfy__Payment__c
    WHERE ohfy__Payment_Date__c >= ${config.startDate}
    ${config.creditQuery}
    ORDER BY ohfy__Payment_Date__c DESC
    LIMIT ${config.limit}
  `;

  const paymentResult = await connectors.salesforce.query({
    authId: config.authIds.salesforce,
    query: paymentQuery
  });

  return {
    invoices: invoiceResult.records || [],
    payments: paymentResult.records || []
  };
}

async function extractQuickBooksData(config) {
  // Extract QuickBooks invoices
  const qbInvoices = await connectors.quickbooks.query({
    authId: config.authIds.quickbooks,
    query: `
      SELECT * FROM Invoice
      WHERE MetaData.LastUpdatedTime >= '${config.startDate}'
    `
  });

  // Extract QuickBooks payments
  const qbPayments = await connectors.quickbooks.query({
    authId: config.authIds.quickbooks,
    query: `
      SELECT * FROM Payment
      WHERE MetaData.LastUpdatedTime >= '${config.startDate}'
    `
  });

  return {
    invoices: qbInvoices.records || [],
    payments: qbPayments.records || []
  };
}

// Phase 2: Business Logic Processing
async function applyAccountingBusinessLogic(sourceData, config, logger) {
  logger.info('Applying accounting business logic');

  // Apply invoice splitting rules (from actual config)
  const splitInvoices = await applySplitInvoiceLogic(
    sourceData.salesforce.invoices,
    config.splitInvoices,
    config.splitArr,
    config
  );

  // Apply chart of accounts mapping
  const mappedAccounts = await applyChartOfAccountsMapping(
    sourceData,
    config.map,
    config
  );

  // Apply payment matching rules
  const matchedPayments = await applyPaymentMatchingLogic(
    sourceData.salesforce.payments,
    sourceData.quickbooks.payments,
    config
  );

  // Apply customer mapping
  const mappedCustomers = await applyCustomerMapping(
    sourceData,
    config.altAccount,
    config
  );

  return {
    splitInvoices: splitInvoices,
    mappedAccounts: mappedAccounts,
    matchedPayments: matchedPayments,
    mappedCustomers: mappedCustomers,
    originalData: sourceData
  };
}

async function applySplitInvoiceLogic(invoices, splitInvoices, splitArr, config) {
  if (!splitInvoices || !splitArr || splitArr.length === 0) {
    return invoices;
  }

  const splitInvoiceList = [];

  for (const invoice of invoices) {
    const customerName = invoice['ohfy__Customer__r']?.Name;

    // Check if this customer requires invoice splitting
    if (splitArr.includes(customerName)) {
      // Apply splitting logic based on line items
      const splitInvoices = await splitInvoiceByBrand(invoice, config);
      splitInvoiceList.push(...splitInvoices);
    } else {
      splitInvoiceList.push(invoice);
    }
  }

  return splitInvoiceList;
}

async function applyPaymentMatchingLogic(sfPayments, qbPayments, config) {
  const matchedPayments = [];

  for (const sfPayment of sfPayments) {
    // Find matching QuickBooks payment
    const qbMatch = qbPayments.find(qbPayment => {
      return (
        Math.abs(qbPayment.TotalAmt - sfPayment['ohfy__Amount__c']) < 0.01 &&
        areDatesClose(qbPayment.TxnDate, sfPayment['ohfy__Payment_Date__c'])
      );
    });

    matchedPayments.push({
      salesforcePayment: sfPayment,
      quickbooksPayment: qbMatch,
      isMatched: !!qbMatch
    });
  }

  return matchedPayments;
}

// Phase 3: Bidirectional Synchronization
async function executeBidirectionalSync(processedData, config, logger) {
  logger.info('Executing bidirectional sync');

  const results = {
    salesforceToQB: { created: [], updated: [], errors: [] },
    qbToSalesforce: { created: [], updated: [], errors: [] }
  };

  // Sync Salesforce → QuickBooks
  if (config.syncToQuickBooks !== false) {
    results.salesforceToQB = await syncSalesforceToQuickBooks(processedData, config);
  }

  // Sync QuickBooks → Salesforce
  if (config.syncToSalesforce !== false) {
    results.qbToSalesforce = await syncQuickBooksToSalesforce(processedData, config);
  }

  return results;
}

async function syncSalesforceToQuickBooks(processedData, config) {
  const results = { created: [], updated: [], errors: [] };

  // Process split invoices
  for (const invoice of processedData.splitInvoices) {
    try {
      const qbInvoiceData = await transformSFToQBInvoice(invoice, config);

      if (invoice['ohfy__QB_ID__c']) {
        // Update existing QuickBooks invoice
        const updateResult = await connectors.quickbooks.update({
          authId: config.authIds.quickbooks,
          resource: 'Invoice',
          id: invoice['ohfy__QB_ID__c'],
          data: qbInvoiceData
        });

        if (updateResult.success) {
          results.updated.push(updateResult);
        } else {
          results.errors.push({
            invoiceId: invoice.Id,
            error: updateResult.error
          });
        }
      } else {
        // Create new QuickBooks invoice
        const createResult = await connectors.quickbooks.create({
          authId: config.authIds.quickbooks,
          resource: 'Invoice',
          data: qbInvoiceData
        });

        if (createResult.success) {
          results.created.push(createResult);

          // Update Salesforce with QB ID
          await connectors.salesforce.update_record({
            authId: config.authIds.salesforce,
            sobject: 'ohfy__Invoice__c',
            id: invoice.Id,
            fields: {
              'ohfy__QB_ID__c': createResult.data.Id
            }
          });
        } else {
          results.errors.push({
            invoiceId: invoice.Id,
            error: createResult.error
          });
        }
      }
    } catch (error) {
      results.errors.push({
        invoiceId: invoice.Id,
        error: error.message
      });
    }
  }

  return results;
}

// Configuration Setup
function setupQuickBooksConfiguration(input) {
  return {
    // Company configuration (from actual config)
    company: input.config?.company || 'TBM',
    companyKey: input.config?.companyKey || 'TBM',
    companyNumber: input.config?.companyNumber || 1,

    // QuickBooks settings
    accountUrl: input.config?.accountUrl || 'qbo.intuit.com',
    qboCount: input.config?.qboCount || 500,

    // Sync settings
    syncToQuickBooks: input.config?.syncToQuickBooks !== false,
    syncToSalesforce: input.config?.syncToSalesforce !== false,
    linkPayment: input.config?.linkPayment || true,

    // Business logic settings
    splitInvoices: input.config?.splitInvoices || false,
    splitArr: input.config?.splitArr || ['Red Bull'],
    feeLines: input.config?.feeLines || true,
    leadingZeros: input.config?.leadingZeros || false,

    // Date and filtering
    startDate: input.config?.startDate || '2024-09-16 04:00',
    limit: input.config?.limit || 5,
    cronSchedule: input.config?.cronSchedule || '0 3,9,15,21 * * *',

    // Custom mappings (from actual config)
    altAccount: input.config?.altAccount || { 'Red Bull': '114' },
    map: input.config?.map || {
      'Bill': 'BILL',
      'Invoice': 'INV',
      'CreditMemo': 'CRED',
      'JournalEntry': 'JE',
      'AccountCredit': 'ACC'
    },

    // Query filters
    invoiceQuery: input.config?.invoiceQuery || "and ohfy__Sales_Rep__r.Location__c = 'TBM'",
    creditQuery: input.config?.creditQuery || "and ohfy__Invoice__r.ohfy__Sales_Rep__r.Location__c = 'TBM'",

    // Test settings
    testMode: input.config?.testMode || true,
    testRun: input.config?.testRun || true,

    // Authentication
    authIds: {
      salesforce: input.config?.salesforceAuthId,
      quickbooks: input.config?.quickbooksAuthId
    }
  };
}
```

---

## 📊 Scenario 3: VIP Depletions Data Pipeline

### Original Architecture: Multiple Workflows
Based on the actual VIP_Depletions_v1 integration.

### Consolidated Implementation

```javascript
/**
 * Consolidated VIP Depletions Integration Script
 * Handles: Item depletion tracking with inventory management
 */
exports.step = async function(input, fileInput) {
  const config = setupVIPDepletionsConfiguration(input);
  const logger = createLogger(config);

  try {
    logger.info('Starting VIP depletions processing', {
      itemPrefix: config.itm_prefix,
      ignoredItems: config.itemIgnoreList.length
    });

    // Phase 1: Data Extraction and Filtering
    const sourceData = await extractDepletionData(input, config, logger);

    // Phase 2: Item Validation and Enrichment
    const validatedData = await validateAndEnrichItems(sourceData, config, logger);

    // Phase 3: Depletion Calculations
    const depletionData = await calculateDepletions(validatedData, config, logger);

    // Phase 4: Salesforce Updates
    const updateResults = await updateSalesforceInventory(depletionData, config, logger);

    // Phase 5: Cleanup and Notifications
    const cleanupResults = await performCleanupOperations(updateResults, config, logger);

    return {
      itemsProcessed: validatedData.length,
      depletionsCalculated: depletionData.length,
      salesforceUpdates: updateResults.successful.length,
      errors: updateResults.errors.length
    };

  } catch (error) {
    return await handleDepletionError(error, config, logger);
  }
};

// Phase 1: Data Extraction
async function extractDepletionData(input, config, logger) {
  logger.info('Extracting depletion data');

  let sourceData = [];

  if (input.csvData) {
    // Process CSV input
    sourceData = await parseCSVData(input.csvData, config);
  } else if (input.apiData) {
    // Process API input
    sourceData = input.apiData;
  } else if (input.fileInput) {
    // Process file input
    sourceData = await parseFileInput(input.fileInput, config);
  }

  // Filter out ignored items (from actual config)
  const filteredData = sourceData.filter(item => {
    const itemCode = item.itemCode || item['Item Code'] || item.sku;
    return !config.itemIgnoreList.includes(itemCode);
  });

  logger.info('Data extracted and filtered', {
    originalCount: sourceData.length,
    filteredCount: filteredData.length,
    ignoredCount: sourceData.length - filteredData.length
  });

  return filteredData;
}

// Phase 2: Item Validation and Enrichment
async function validateAndEnrichItems(sourceData, config, logger) {
  logger.info('Validating and enriching items');

  const validatedItems = [];
  const errors = [];

  for (const item of sourceData) {
    try {
      // Standardize item data
      const standardizedItem = {
        itemCode: item.itemCode || item['Item Code'] || item.sku,
        depletionAmount: parseFloat(item.depletionAmount || item['Depletion Amount'] || 0),
        reportDate: item.reportDate || item['Report Date'] || new Date().toISOString().split('T')[0],
        location: item.location || item['Location'] || 'Default'
      };

      // Apply item prefix if configured
      if (config.itm_prefix && !standardizedItem.itemCode.startsWith(config.itm_prefix)) {
        standardizedItem.itemCode = `${config.itm_prefix}${standardizedItem.itemCode}`;
      }

      // Validate required fields
      if (!standardizedItem.itemCode || standardizedItem.depletionAmount < 0) {
        errors.push({
          item: standardizedItem,
          error: 'Invalid item code or negative depletion amount'
        });
        continue;
      }

      // Enrich with Salesforce item data
      const enrichedItem = await enrichWithSalesforceData(standardizedItem, config);

      if (enrichedItem.salesforceItem) {
        validatedItems.push(enrichedItem);
      } else {
        errors.push({
          item: standardizedItem,
          error: 'Item not found in Salesforce'
        });
      }

    } catch (error) {
      errors.push({
        item: item,
        error: error.message
      });
    }
  }

  // Log validation results
  if (errors.length > 0) {
    logger.warn('Item validation errors', { errorCount: errors.length });
    await storeValidationErrors(errors, config);
  }

  return validatedItems;
}

async function enrichWithSalesforceData(item, config) {
  // Find Salesforce item by SKU or external ID
  const itemQuery = `
    SELECT Id, Name, ohfy__SKU__c, ohfy__Quantity_On_Hand__c,
           ohfy__Location__c, ohfy__Active__c
    FROM ohfy__Item__c
    WHERE ohfy__SKU__c = '${item.itemCode}'
    AND ohfy__Active__c = true
    LIMIT 1
  `;

  const itemResult = await connectors.salesforce.query({
    authId: config.authIds.salesforce,
    query: itemQuery
  });

  return {
    ...item,
    salesforceItem: itemResult.records?.[0] || null,
    enrichedAt: new Date().toISOString()
  };
}

// Phase 3: Depletion Calculations
async function calculateDepletions(validatedData, config, logger) {
  logger.info('Calculating depletions');

  const depletionCalculations = [];

  for (const item of validatedData) {
    const currentQuantity = parseFloat(item.salesforceItem['ohfy__Quantity_On_Hand__c'] || 0);
    const depletionAmount = item.depletionAmount;
    const newQuantity = Math.max(0, currentQuantity - depletionAmount);

    const calculation = {
      itemId: item.salesforceItem.Id,
      itemCode: item.itemCode,
      currentQuantity: currentQuantity,
      depletionAmount: depletionAmount,
      newQuantity: newQuantity,
      calculatedAt: new Date().toISOString(),
      needsUpdate: currentQuantity !== newQuantity
    };

    depletionCalculations.push(calculation);
  }

  return depletionCalculations;
}

// Phase 4: Salesforce Updates
async function updateSalesforceInventory(depletionData, config, logger) {
  logger.info('Updating Salesforce inventory');

  const updateRecords = depletionData
    .filter(calc => calc.needsUpdate)
    .map(calc => ({
      Id: calc.itemId,
      'ohfy__Quantity_On_Hand__c': calc.newQuantity
    }));

  if (updateRecords.length === 0) {
    logger.info('No inventory updates needed');
    return { successful: [], errors: [] };
  }

  // Process updates in batches
  const results = await bulkUpdateSalesforce(
    'ohfy__Item__c',
    updateRecords,
    config
  );

  logger.info('Inventory updates completed', {
    successful: results.successful.length,
    errors: results.errors.length
  });

  return results;
}

async function bulkUpdateSalesforce(sobject, records, config) {
  const results = { successful: [], errors: [] };
  const batchSize = 100;

  // Process in batches
  for (let i = 0; i < records.length; i += batchSize) {
    const batch = records.slice(i, i + batchSize);

    try {
      const batchResult = await connectors.salesforce.batch_update_records({
        authId: config.authIds.salesforce,
        sobject: sobject,
        records: batch
      });

      if (batchResult.success) {
        results.successful.push(...batchResult.records);
      } else {
        results.errors.push(...batchResult.errors);
      }

    } catch (error) {
      results.errors.push({
        batch: i / batchSize,
        error: error.message,
        records: batch
      });
    }
  }

  return results;
}

// Configuration Setup
function setupVIPDepletionsConfiguration(input) {
  return {
    // Item configuration (from actual config)
    itm_prefix: input.config?.itm_prefix || 'ITM2DA',
    itemIgnoreList: input.config?.itemIgnoreList || [
      '240032', '240031', '240040', '240041', '240048',
      'HONCRI6416', 'CDHC64', 'RASP6416', '240043',
      'HON16', '240058', '240064', 'RAS016'
      // ... full list from actual config
    ],

    // Processing settings
    batchSize: input.config?.batchSize || 100,
    validateItems: input.config?.validateItems !== false,
    updateInventory: input.config?.updateInventory !== false,

    // Authentication
    authIds: {
      salesforce: input.config?.salesforceAuthId
    },

    // Error handling
    continueOnError: input.config?.continueOnError !== false,
    logErrors: input.config?.logErrors !== false
  };
}
```

---

## 🚀 Benefits Demonstrated

### Complexity Reduction
```
EDI Integration:       8 workflows → 1 script connector (87.5% reduction)
QuickBooks Sync:      22 workflows → 1 script connector (95.5% reduction)
VIP Depletions:        6 workflows → 1 script connector (83.3% reduction)
```

### Maintenance Improvement
```
Before: Business logic scattered across 20+ script connectors
After:  All logic in single, searchable, maintainable script

Before: Complex workflow dependencies requiring careful sequencing
After:  Linear execution with explicit dependencies and error handling

Before: Difficult debugging across multiple workflows
After:  Single execution context with complete visibility
```

### Developer Experience Enhancement
```
Before: Multiple files to understand integration
After:  Single file with complete business logic

Before: AI development requires context across many workflows
After:  AI has complete integration context in one place

Before: Changes require coordinating across multiple workflows
After:  Changes made in single location with unified testing
```

---

## 📚 Usage Instructions

### 1. **Choose Your Scenario**
- **EDI Processing**: Use for document-based integrations with parsing and transformation
- **Accounting Sync**: Use for bidirectional financial data synchronization
- **Data Pipeline**: Use for high-volume data processing with validation

### 2. **Customize Configuration**
- Copy the configuration setup function
- Modify field mappings and business rules for your specific use case
- Add org-specific validation and transformation logic

### 3. **Implement Business Logic**
- Copy relevant business logic modules from OHFY_BUSINESS_LOGIC_LIBRARY.md
- Customize validation and transformation functions
- Add error handling specific to your integration requirements

### 4. **Test and Deploy**
- Use Tray Script Tester for local development and testing
- Deploy as single Script Connector workflow in Tray
- Monitor performance and error rates

---

**Related Guides:**
- **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** - Base templates used in these examples
- **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)** - Business logic modules referenced in examples
- **[Integration Migration Guide](./INTEGRATION_MIGRATION_GUIDE.md)** - Step-by-step migration process for your own integrations
- **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)** - API operations used in these examples