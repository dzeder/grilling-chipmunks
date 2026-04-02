# OHFY Business Logic Library

**Reusable JavaScript Modules for OHFY Platform Integration Logic**

Transform OHFY's Apex business rules into portable JavaScript functions for Tray Script Connectors.

---

## 📋 Core Business Logic Modules

### Order Processing Module

#### Order Validation
```javascript
/**
 * OHFY Order Validation Module
 * Implements core OHFY business rules for order creation
 */
const OHFYOrderLogic = {

  /**
   * Validate minimum order requirements
   * Based on INTEGRATION_QUICK_REFERENCE.md requirements
   */
  validateOrderRequirements: function(orderData) {
    const errors = [];
    const requiredFields = [
      'ohfy__External_ID__c',
      'ohfy__Customer__c',
      'ohfy__Order_Date__c',
      'ohfy__Status__c',
      'ohfy__Sales_Rep__c',
      'ohfy__Delivery_Pickup_Date__c'
    ];

    // Check required fields
    for (const field of requiredFields) {
      if (!orderData[field] || orderData[field] === '') {
        errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate date formats
    if (orderData['ohfy__Order_Date__c'] && !this.isValidDate(orderData['ohfy__Order_Date__c'])) {
      errors.push('Order_Date__c must be in YYYY-MM-DD format');
    }

    if (orderData['ohfy__Delivery_Pickup_Date__c'] && !this.isValidDate(orderData['ohfy__Delivery_Pickup_Date__c'])) {
      errors.push('Delivery_Pickup_Date__c must be in YYYY-MM-DD format');
    }

    // Validate status picklist values
    const validStatuses = ['New', 'Scheduled', 'In Progress', 'Picking', 'Loaded', 'Out For Delivery', 'Delivered', 'Complete', 'Cancelled'];
    if (orderData['ohfy__Status__c'] && !validStatuses.includes(orderData['ohfy__Status__c'])) {
      errors.push(`Invalid Status__c value: ${orderData['ohfy__Status__c']}. Must be one of: ${validStatuses.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
      data: orderData
    };
  },

  /**
   * Validate order item requirements
   * Based on Order_Item__c minimum requirements
   */
  validateOrderItemRequirements: function(orderItemData) {
    const errors = [];
    const requiredFields = [
      'ohfy__External_ID__c',
      'ohfy__Order__c',
      'ohfy__Item__c',
      'ohfy__Ordered_Quantity__c',
      'ohfy__Unit_Price__c',
      'ohfy__Sub_Total__c'
    ];

    // Check required fields
    for (const field of requiredFields) {
      if (!orderItemData[field] && orderItemData[field] !== 0) {
        errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate numeric fields
    if (orderItemData['ohfy__Ordered_Quantity__c'] && orderItemData['ohfy__Ordered_Quantity__c'] <= 0) {
      errors.push('Ordered_Quantity__c must be greater than 0');
    }

    if (orderItemData['ohfy__Unit_Price__c'] && orderItemData['ohfy__Unit_Price__c'] < 0) {
      errors.push('Unit_Price__c cannot be negative');
    }

    if (orderItemData['ohfy__Sub_Total__c'] && orderItemData['ohfy__Sub_Total__c'] < 0) {
      errors.push('Sub_Total__c cannot be negative');
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
      data: orderItemData
    };
  },

  /**
   * Calculate order item subtotal
   * Implements: Sub_Total__c = Ordered_Quantity__c * Unit_Price__c
   */
  calculateOrderItemSubTotal: function(orderItem) {
    const quantity = parseFloat(orderItem['ohfy__Ordered_Quantity__c'] || 0);
    const unitPrice = parseFloat(orderItem['ohfy__Unit_Price__c'] || 0);

    return {
      ...orderItem,
      'ohfy__Sub_Total__c': quantity * unitPrice
    };
  },

  /**
   * Validate and format dates
   */
  isValidDate: function(dateString) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateString)) return false;

    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date) && dateString === date.toISOString().split('T')[0];
  },

  /**
   * Apply order processing sequence
   * Based on INTEGRATION_QUICK_REFERENCE.md processing order
   */
  processOrderSequence: async function(orderData, orderItems, connectors, config) {
    const results = {
      order: null,
      orderItems: [],
      errors: []
    };

    try {
      // Step 1: Validate order
      const orderValidation = this.validateOrderRequirements(orderData);
      if (!orderValidation.isValid) {
        results.errors.push(...orderValidation.errors);
        return results;
      }

      // Step 2: Create Order (totals empty - will be calculated by Salesforce rollups)
      const orderResult = await connectors.salesforce.create_record({
        authId: config.authIds.salesforce,
        sobject: 'ohfy__Order__c',
        fields: orderValidation.data
      });

      if (!orderResult.success) {
        results.errors.push(`Order creation failed: ${orderResult.errors.join(', ')}`);
        return results;
      }

      results.order = orderResult;

      // Step 3: Create Order Items (triggers rollups)
      for (const item of orderItems) {
        try {
          // Validate and calculate subtotal
          const itemValidation = this.validateOrderItemRequirements({
            ...item,
            'ohfy__Order__c': orderResult.id
          });

          if (!itemValidation.isValid) {
            results.errors.push(`Order item validation failed: ${itemValidation.errors.join(', ')}`);
            continue;
          }

          const itemWithSubTotal = this.calculateOrderItemSubTotal(itemValidation.data);

          const itemResult = await connectors.salesforce.create_record({
            authId: config.authIds.salesforce,
            sobject: 'ohfy__Order_Item__c',
            fields: itemWithSubTotal
          });

          if (itemResult.success) {
            results.orderItems.push(itemResult);
          } else {
            results.errors.push(`Order item creation failed: ${itemResult.errors.join(', ')}`);
          }

        } catch (error) {
          results.errors.push(`Order item processing error: ${error.message}`);
        }
      }

      return results;

    } catch (error) {
      results.errors.push(`Order processing error: ${error.message}`);
      return results;
    }
  }
};
```

### Customer and Account Validation Module

```javascript
/**
 * OHFY Customer Validation Module
 * Validates customer and account relationships
 */
const OHFYCustomerLogic = {

  /**
   * Validate account exists and is active
   */
  validateAccountExists: async function(accountId, connectors, config) {
    try {
      const accountResult = await connectors.salesforce.find_records({
        authId: config.authIds.salesforce,
        sobject: 'Account',
        criteria: {
          'Id': accountId,
          'IsActive__c': true
        },
        fields: ['Id', 'Name', 'Type', 'IsActive__c']
      });

      if (accountResult.records && accountResult.records.length > 0) {
        return {
          isValid: true,
          account: accountResult.records[0]
        };
      } else {
        return {
          isValid: false,
          error: `Account ${accountId} not found or inactive`
        };
      }
    } catch (error) {
      return {
        isValid: false,
        error: `Account validation error: ${error.message}`
      };
    }
  },

  /**
   * Find or create customer account
   */
  findOrCreateCustomer: async function(customerData, connectors, config) {
    try {
      // First, try to find existing customer by external ID
      if (customerData.externalId) {
        const existingResult = await connectors.salesforce.find_records({
          authId: config.authIds.salesforce,
          sobject: 'Account',
          criteria: {
            'External_ID__c': customerData.externalId
          },
          fields: ['Id', 'Name', 'External_ID__c']
        });

        if (existingResult.records && existingResult.records.length > 0) {
          return {
            success: true,
            account: existingResult.records[0],
            created: false
          };
        }
      }

      // Create new customer account
      const createResult = await connectors.salesforce.create_record({
        authId: config.authIds.salesforce,
        sobject: 'Account',
        fields: {
          'Name': customerData.name,
          'External_ID__c': customerData.externalId,
          'Type': 'Customer',
          'BillingStreet': customerData.billingAddress?.street,
          'BillingCity': customerData.billingAddress?.city,
          'BillingState': customerData.billingAddress?.state,
          'BillingPostalCode': customerData.billingAddress?.postalCode,
          'Phone': customerData.phone,
          'Website': customerData.website
        }
      });

      if (createResult.success) {
        return {
          success: true,
          account: createResult,
          created: true
        };
      } else {
        return {
          success: false,
          error: `Customer creation failed: ${createResult.errors.join(', ')}`
        };
      }

    } catch (error) {
      return {
        success: false,
        error: `Customer processing error: ${error.message}`
      };
    }
  }
};
```

### Item and Inventory Validation Module

```javascript
/**
 * OHFY Item Validation Module
 * Validates items and inventory availability
 */
const OHFYItemLogic = {

  /**
   * Validate item exists and is active
   */
  validateItemExists: async function(itemId, connectors, config) {
    try {
      const itemResult = await connectors.salesforce.find_records({
        authId: config.authIds.salesforce,
        sobject: 'ohfy__Item__c',
        criteria: {
          'Id': itemId,
          'ohfy__Active__c': true
        },
        fields: ['Id', 'Name', 'ohfy__Active__c', 'ohfy__Type__c', 'ohfy__Quantity_On_Hand__c']
      });

      if (itemResult.records && itemResult.records.length > 0) {
        return {
          isValid: true,
          item: itemResult.records[0]
        };
      } else {
        return {
          isValid: false,
          error: `Item ${itemId} not found or inactive`
        };
      }
    } catch (error) {
      return {
        isValid: false,
        error: `Item validation error: ${error.message}`
      };
    }
  },

  /**
   * Check inventory availability
   * Based on U_Order_Items.cls logic
   */
  checkInventoryAvailability: async function(itemId, requestedQuantity, connectors, config) {
    try {
      const itemResult = await this.validateItemExists(itemId, connectors, config);

      if (!itemResult.isValid) {
        return itemResult;
      }

      const item = itemResult.item;
      const onHandQuantity = parseFloat(item['ohfy__Quantity_On_Hand__c'] || 0);
      const requested = parseFloat(requestedQuantity);

      return {
        isValid: true,
        item: item,
        available: onHandQuantity >= requested,
        onHandQuantity: onHandQuantity,
        requestedQuantity: requested,
        shortfall: Math.max(0, requested - onHandQuantity)
      };

    } catch (error) {
      return {
        isValid: false,
        error: `Inventory check error: ${error.message}`
      };
    }
  },

  /**
   * Find items by external identifiers (UPC, SKU, etc.)
   */
  findItemsByExternalId: async function(externalIds, connectors, config) {
    try {
      const results = [];

      for (const externalId of externalIds) {
        const itemResult = await connectors.salesforce.query({
          authId: config.authIds.salesforce,
          query: `
            SELECT Id, Name, ohfy__UPC__c, ohfy__SKU__c, ohfy__Active__c, ohfy__Quantity_On_Hand__c
            FROM ohfy__Item__c
            WHERE (ohfy__UPC__c = '${externalId}' OR ohfy__SKU__c = '${externalId}')
            AND ohfy__Active__c = true
            LIMIT 1
          `
        });

        if (itemResult.records && itemResult.records.length > 0) {
          results.push({
            externalId: externalId,
            found: true,
            item: itemResult.records[0]
          });
        } else {
          results.push({
            externalId: externalId,
            found: false,
            error: `Item not found for external ID: ${externalId}`
          });
        }
      }

      return {
        success: true,
        results: results
      };

    } catch (error) {
      return {
        success: false,
        error: `Item lookup error: ${error.message}`
      };
    }
  }
};
```

### Credit and Payment Validation Module

```javascript
/**
 * OHFY Credit Validation Module
 * Validates credits and payment processing
 */
const OHFYCreditLogic = {

  /**
   * Validate credit requirements
   */
  validateCreditRequirements: function(creditData) {
    const errors = [];
    const requiredFields = [
      'ohfy__External_ID__c',
      'ohfy__Account__c',
      'ohfy__Amount__c'
    ];

    // Check required fields
    for (const field of requiredFields) {
      if (!creditData[field] && creditData[field] !== 0) {
        errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate amount is positive
    if (creditData['ohfy__Amount__c'] && creditData['ohfy__Amount__c'] < 0) {
      errors.push('Credit amount must be positive (>= 0)');
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
      data: creditData
    };
  },

  /**
   * Validate payment method picklist values
   */
  validatePaymentMethod: function(paymentMethod) {
    const validMethods = [
      'Check',
      'Cash',
      'EFT',
      'Quickbooks Electronic Invoice',
      'Ohanafy'
    ];

    return {
      isValid: validMethods.includes(paymentMethod),
      validMethods: validMethods
    };
  },

  /**
   * Validate payment terms picklist values
   */
  validatePaymentTerms: function(paymentTerms) {
    const validTerms = [
      'Due on Receipt',
      '10 Days',
      '15 Days',
      '20 Days',
      '30 Days',
      '60 Days',
      '90 Days',
      'Custom'
    ];

    return {
      isValid: validTerms.includes(paymentTerms),
      validTerms: validTerms
    };
  }
};
```

### User and Sales Rep Validation Module

```javascript
/**
 * OHFY User Validation Module
 * Validates users and sales rep assignments
 */
const OHFYUserLogic = {

  /**
   * Validate user exists and is active
   */
  validateUserExists: async function(userId, connectors, config) {
    try {
      const userResult = await connectors.salesforce.find_records({
        authId: config.authIds.salesforce,
        sobject: 'User',
        criteria: {
          'Id': userId,
          'IsActive': true
        },
        fields: ['Id', 'Name', 'Email', 'IsActive', 'Profile.Name']
      });

      if (userResult.records && userResult.records.length > 0) {
        return {
          isValid: true,
          user: userResult.records[0]
        };
      } else {
        return {
          isValid: false,
          error: `User ${userId} not found or inactive`
        };
      }
    } catch (error) {
      return {
        isValid: false,
        error: `User validation error: ${error.message}`
      };
    }
  },

  /**
   * Find sales rep by email or external ID
   */
  findSalesRepByEmail: async function(email, connectors, config) {
    try {
      const userResult = await connectors.salesforce.query({
        authId: config.authIds.salesforce,
        query: `
          SELECT Id, Name, Email, IsActive, Profile.Name
          FROM User
          WHERE Email = '${email}'
          AND IsActive = true
          AND Profile.Name LIKE '%Sales%'
          LIMIT 1
        `
      });

      if (userResult.records && userResult.records.length > 0) {
        return {
          success: true,
          user: userResult.records[0]
        };
      } else {
        return {
          success: false,
          error: `Sales rep not found for email: ${email}`
        };
      }

    } catch (error) {
      return {
        success: false,
        error: `Sales rep lookup error: ${error.message}`
      };
    }
  }
};
```

---

## 🛠️ Data Transformation Utilities

### Field Mapping Utilities
```javascript
/**
 * OHFY Field Mapping Utilities
 * Transform external data formats to OHFY field requirements
 */
const OHFYFieldMapping = {

  /**
   * Map external order data to OHFY format
   */
  mapExternalOrderToOHFY: function(externalOrder, mappingConfig) {
    const ohfyOrder = {};

    // Apply field mappings
    for (const [ohfyField, externalField] of Object.entries(mappingConfig.orderFieldMappings)) {
      if (externalOrder[externalField] !== undefined) {
        ohfyOrder[ohfyField] = externalOrder[externalField];
      }
    }

    // Apply transformations
    if (ohfyOrder['ohfy__Order_Date__c']) {
      ohfyOrder['ohfy__Order_Date__c'] = this.formatDateForSalesforce(ohfyOrder['ohfy__Order_Date__c']);
    }

    if (ohfyOrder['ohfy__Delivery_Pickup_Date__c']) {
      ohfyOrder['ohfy__Delivery_Pickup_Date__c'] = this.formatDateForSalesforce(ohfyOrder['ohfy__Delivery_Pickup_Date__c']);
    }

    // Set defaults
    if (!ohfyOrder['ohfy__Status__c']) {
      ohfyOrder['ohfy__Status__c'] = 'New';
    }

    return ohfyOrder;
  },

  /**
   * Format date for Salesforce (YYYY-MM-DD)
   */
  formatDateForSalesforce: function(dateInput) {
    let date;

    if (typeof dateInput === 'string') {
      date = new Date(dateInput);
    } else if (dateInput instanceof Date) {
      date = dateInput;
    } else {
      throw new Error(`Invalid date format: ${dateInput}`);
    }

    if (isNaN(date.getTime())) {
      throw new Error(`Invalid date: ${dateInput}`);
    }

    return date.toISOString().split('T')[0];
  },

  /**
   * Clean and validate external ID
   */
  formatExternalId: function(externalId, prefix = '') {
    if (!externalId) return null;

    // Remove special characters and spaces
    const cleaned = externalId.toString().replace(/[^\w-]/g, '');

    // Add prefix if provided
    return prefix ? `${prefix}-${cleaned}` : cleaned;
  },

  /**
   * Transform currency values
   */
  formatCurrency: function(value) {
    if (value === null || value === undefined || value === '') return 0;

    const numericValue = parseFloat(value.toString().replace(/[^\d.-]/g, ''));
    return isNaN(numericValue) ? 0 : Math.round(numericValue * 100) / 100;
  }
};
```

### Error Handling Utilities
```javascript
/**
 * OHFY Error Handling Utilities
 * Standardized error handling for OHFY integrations
 */
const OHFYErrorHandling = {

  /**
   * Parse Salesforce API errors
   */
  parseSalesforceError: function(error) {
    const errorInfo = {
      type: 'UNKNOWN',
      message: error.message || 'Unknown error',
      field: null,
      code: null,
      retry: false
    };

    // Parse common Salesforce error patterns
    if (error.message) {
      const message = error.message.toLowerCase();

      if (message.includes('duplicate value')) {
        errorInfo.type = 'DUPLICATE_VALUE';
        errorInfo.retry = false;
      } else if (message.includes('required field missing')) {
        errorInfo.type = 'REQUIRED_FIELD_MISSING';
        errorInfo.retry = false;
      } else if (message.includes('invalid picklist')) {
        errorInfo.type = 'INVALID_PICKLIST_VALUE';
        errorInfo.retry = false;
      } else if (message.includes('unable to lock row')) {
        errorInfo.type = 'UNABLE_TO_LOCK_ROW';
        errorInfo.retry = true;
      } else if (message.includes('timeout')) {
        errorInfo.type = 'TIMEOUT';
        errorInfo.retry = true;
      } else if (message.includes('too many apex')) {
        errorInfo.type = 'APEX_LIMIT_EXCEEDED';
        errorInfo.retry = true;
      }
    }

    return errorInfo;
  },

  /**
   * Handle integration errors with appropriate response
   */
  handleIntegrationError: async function(error, config, logger, context = {}) {
    const errorInfo = this.parseSalesforceError(error);

    logger.error('Integration error occurred', {
      type: errorInfo.type,
      message: errorInfo.message,
      context: context,
      retry: errorInfo.retry
    });

    // Store error for review if needed
    if (config.storeErrors) {
      await this.storeErrorForReview(error, context, config);
    }

    // Return structured error response
    return {
      success: false,
      error: {
        type: errorInfo.type,
        message: errorInfo.message,
        retry: errorInfo.retry,
        context: context
      }
    };
  },

  /**
   * Store error for later review
   */
  storeErrorForReview: async function(error, context, config) {
    try {
      // Store in Tray storage for review
      await connectors.storage.set({
        key: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        value: {
          error: error.message,
          context: context,
          timestamp: new Date().toISOString(),
          integration: config.integration || 'unknown'
        },
        ttl: 86400 * 7 // 7 days
      });
    } catch (storageError) {
      console.error('Failed to store error for review:', storageError);
    }
  }
};
```

---

## 🔧 Usage Examples in Consolidated Scripts

### Complete Order Processing Example
```javascript
// In your consolidated Script Connector
exports.step = async function(input, fileInput) {
  const config = setupConfiguration(input);
  const logger = createLogger(config);

  try {
    // Use OHFY business logic modules
    const orderValidation = OHFYOrderLogic.validateOrderRequirements(input.orderData);

    if (!orderValidation.isValid) {
      throw new Error(`Order validation failed: ${orderValidation.errors.join(', ')}`);
    }

    // Validate customer exists
    const customerValidation = await OHFYCustomerLogic.validateAccountExists(
      input.orderData['ohfy__Customer__c'],
      connectors,
      config
    );

    if (!customerValidation.isValid) {
      throw new Error(customerValidation.error);
    }

    // Process complete order with business logic
    const orderResults = await OHFYOrderLogic.processOrderSequence(
      orderValidation.data,
      input.orderItems,
      connectors,
      config
    );

    return {
      success: true,
      order: orderResults.order,
      orderItems: orderResults.orderItems,
      errors: orderResults.errors
    };

  } catch (error) {
    return await OHFYErrorHandling.handleIntegrationError(error, config, logger, {
      operation: 'order_processing',
      inputData: input
    });
  }
};
```

### Data Transformation Example
```javascript
// Transform external system data to OHFY format
const mappingConfig = {
  orderFieldMappings: {
    'ohfy__External_ID__c': 'external_order_id',
    'ohfy__Customer__c': 'customer_account_id',
    'ohfy__Order_Date__c': 'order_date',
    'ohfy__Status__c': 'order_status',
    'ohfy__Sales_Rep__c': 'sales_rep_id'
  }
};

const transformedOrder = OHFYFieldMapping.mapExternalOrderToOHFY(
  externalOrderData,
  mappingConfig
);

const validation = OHFYOrderLogic.validateOrderRequirements(transformedOrder);
```

---

## 📚 Integration with Other Guides

### Loading Business Logic in Scripts
```javascript
// At the top of your consolidated Script Connector
// Copy the relevant modules from this library

// Use in your main processing function
const processedData = await OHFYOrderLogic.processOrderSequence(
  orderData,
  orderItems,
  connectors,
  config
);
```

### Configuration Integration
```javascript
// Load org-specific configurations
const orgConfig = {
  picklistValues: {
    'ohfy__Status__c': ['New', 'Scheduled', 'In Progress'], // From ORG_CONFIGURATION_MATRIX.md
    'ohfy__Payment_Method__c': ['Check', 'Cash', 'EFT']     // From ORG_CONFIGURATION_MATRIX.md
  },
  fieldMappings: {} // From ORG_CONFIGURATION_MATRIX.md
};

// Use with business logic
OHFYOrderLogic.validateOrderRequirements(orderData, orgConfig);
```

---

**Related Guides:**
- **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** - Complete implementation examples using these modules
- **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)** - API operations called by these modules
- **[Org Configuration Matrix](./ORG_CONFIGURATION_MATRIX.md)** - Environment-specific configurations for business logic
- **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** - Real-world usage of these business logic modules