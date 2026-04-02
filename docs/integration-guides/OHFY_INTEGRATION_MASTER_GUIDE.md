# OHFY Integration Master Guide

**The Complete Guide to Building Consolidated OHFY Platform Integrations**

---

## 🚀 Quick Start: Single Script Integration Pattern

### New Architecture: One Script Rules All
```
External Trigger → Master Script Connector → Multiple API Calls → OHFY Platform
```

**Replace this complexity:**
- 8-22 scattered workflows
- 20+ script connectors with fragmented logic
- Cross-workflow dependencies and state management

**With this simplicity:**
- 1 comprehensive Script Connector per integration
- Complete business logic in one maintainable place
- All API orchestration and error handling unified

---

## 📋 Integration Checklist (5-Minute Setup)

### ✅ Pre-Integration Requirements
- [ ] **OHFY Org Access**: Salesforce org with OHFY-Core package installed
- [ ] **Tray Authentication**: AuthId configured for target Salesforce org
- [ ] **External System**: API credentials for source/destination system
- [ ] **Business Requirements**: Clear understanding of data flow and transformation rules

### ✅ Development Resources
- [ ] **Script Templates**: Choose from consolidated patterns (EDI, Accounting, Data Sync)
- [ ] **API Schemas**: Reference Tray connector operation schemas
- [ ] **OHFY Business Logic**: Leverage pre-built validation and transformation modules
- [ ] **Field Mappings**: Use org-specific configuration matrices

### ✅ Testing and Deployment
- [ ] **CAPI Testing**: Validate connector operations using command-line tool
- [ ] **Integration Testing**: Test complete end-to-end flow
- [ ] **Error Handling**: Verify all failure scenarios and recovery logic
- [ ] **Performance Validation**: Confirm bulk operation efficiency

---

## 🏗️ Architecture Overview

### Three-Layer Integration Foundation

#### **Layer 1: Tray Connector Operations**
```javascript
// Pure connector operations with schemas
const salesforceResult = await connectors.salesforce.create_record({
  authId: "your-sf-auth-id",
  sobject: "ohfy__Order__c",
  fields: transformedData
});
```

#### **Layer 2: OHFY Business Logic**
```javascript
// Reusable business logic modules
const orderData = await OHFYBusinessLogic.validateOrderRequirements(inputData);
const transformedFields = OHFYBusinessLogic.mapExternalToOHFY(orderData);
```

#### **Layer 3: Org-Specific Configuration**
```javascript
// Environment-specific field mappings
const fieldMapping = OrgConfig.getFieldMapping('distro-production', 'Order');
const picklistValues = OrgConfig.getPicklistValues('ohfy__Status__c');
```

### Integration Flow Pattern
```javascript
exports.step = async function(input, fileInput) {
  try {
    // 1. Extract and validate input data
    const sourceData = await extractSourceData(input);

    // 2. Apply OHFY business logic and validation
    const validatedData = await applyBusinessRules(sourceData);

    // 3. Transform to OHFY format using org config
    const ohfyRecords = await transformToOHFY(validatedData);

    // 4. Execute Salesforce operations
    const results = await executeSalesforceOperations(ohfyRecords);

    // 5. Handle results and cleanup
    return await processResults(results);

  } catch (error) {
    return await handleIntegrationError(error);
  }
};
```

---

## 📚 Developer Resources

### Integration Pattern Libraries

#### **Core Patterns**
- **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** - Complete JavaScript templates for common integrations
- **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)** - Full connector schema reference and examples
- **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)** - Reusable validation and transformation modules

#### **Configuration References**
- **[Org Configuration Matrix](./ORG_CONFIGURATION_MATRIX.md)** - Environment-specific field mappings and constraints
- **[Integration Migration Guide](./INTEGRATION_MIGRATION_GUIDE.md)** - Convert existing multi-workflow integrations

#### **Complete Examples**
- **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** - End-to-end implementations for EDI, Accounting, and Data Sync

### Command-Line Tools

#### **CAPI (Connector API) Tool**
```bash
# Schema discovery
node capi.js schema salesforce create_record
node capi.js schema quickbooks create_customer

# Live testing
node capi.js salesforce create_record '{"sobject":"ohfy__Order__c","fields":{"Name":"Test Order"}}'

# Connector catalog
node capi.js list                    # All available connectors
node capi.js info salesforce         # Salesforce connector details
```

#### **Tray Script Tester**
```bash
# Test script logic locally
npm install                          # Install dependencies
node run.js                         # Test script.js with input.json
```

---

## 🎯 Integration Types and Patterns

### 1. **EDI Document Processing**
**Single Script Pattern**: Process 810/856 documents with complete business logic
```javascript
// Handles: Document parsing → Validation → OHFY transformation → Salesforce sync
// Replaces: 8 separate workflows with 22 script connectors
```

### 2. **Accounting System Sync**
**Single Script Pattern**: Complete QuickBooks ↔ Salesforce synchronization
```javascript
// Handles: Data extraction → Mapping → Validation → Bidirectional sync → Reconciliation
// Replaces: 22 workflows with scattered business logic
```

### 3. **Real-time Data Pipeline**
**Single Script Pattern**: External system → OHFY transformation → Multiple destinations
```javascript
// Handles: Webhook processing → Business rules → Parallel updates → Status reporting
// Replaces: Multiple workflows with complex dependencies
```

### 4. **Batch Data Synchronization**
**Single Script Pattern**: Scheduled bulk operations with comprehensive error handling
```javascript
// Handles: Data extraction → Bulk validation → Transformation → Batch upload → Reconciliation
// Replaces: Nested loops across multiple workflows
```

---

## 🛠️ Development Workflow

### 1. **Choose Integration Pattern**
- Review **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** for similar use cases
- Select appropriate base template from **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)**

### 2. **Configure Business Logic**
- Import required modules from **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)**
- Apply org-specific configurations from **[Org Configuration Matrix](./ORG_CONFIGURATION_MATRIX.md)**

### 3. **Implement and Test**
- Use **CAPI tool** for connector operation testing
- Test complete integration flow with **Tray Script Tester**
- Validate against **OHFY field requirements** and **org constraints**

### 4. **Deploy and Monitor**
- Deploy single Script Connector workflow to Tray
- Monitor execution through Tray dashboard
- Use consolidated error handling for troubleshooting

---

## 🔧 Migration from Existing Integrations

### Assessment Questions
- **How many workflows** does your current integration use?
- **Where is business logic scattered** across script connectors?
- **What external systems** are involved in the integration?
- **What OHFY objects** are created/updated in the process?

### Migration Steps
1. **Analyze Current Integration** - Map all workflows and extract business logic
2. **Choose Consolidation Pattern** - Select appropriate single-script template
3. **Extract and Combine Logic** - Merge scattered scripts into unified implementation
4. **Test and Validate** - Ensure all functionality is preserved in consolidated form
5. **Deploy and Monitor** - Replace multi-workflow with single consolidated workflow

**Detailed migration instructions**: **[Integration Migration Guide](./INTEGRATION_MIGRATION_GUIDE.md)**

---

## 🚨 Common Pitfalls and Solutions

### **Pitfall**: Trying to preserve existing multi-workflow structure
**Solution**: Embrace consolidation - all logic should be in one script for maintainability

### **Pitfall**: Mixing authentication patterns across connectors
**Solution**: Use consistent AuthId patterns from **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)**

### **Pitfall**: Hardcoding org-specific values in scripts
**Solution**: Use configuration matrices from **[Org Configuration Matrix](./ORG_CONFIGURATION_MATRIX.md)**

### **Pitfall**: Insufficient error handling in consolidated scripts
**Solution**: Implement comprehensive error handling patterns from **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)**

---

## 📞 Support and Resources

### **Documentation Navigation**
- **New to OHFY Integration?** → Start with **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)**
- **Need API Reference?** → Check **[Tray Connector Operations](./TRAY_CONNECTOR_OPERATIONS.md)**
- **Looking for Business Logic?** → Browse **[OHFY Business Logic Library](./OHFY_BUSINESS_LOGIC_LIBRARY.md)**
- **Environment-Specific Issues?** → Reference **[Org Configuration Matrix](./ORG_CONFIGURATION_MATRIX.md)**
- **Migrating Existing Integration?** → Follow **[Integration Migration Guide](./INTEGRATION_MIGRATION_GUIDE.md)**

### **Testing and Validation Tools**
- **CAPI Tool**: `/Integrations/04-utilities/tray-connector-explorer/trayConnectorExplorer/`
- **Script Tester**: Same directory, use for local JavaScript testing
- **Salesforce Integration Framework**: `/SalesforceIntegrationFramework/` for advanced patterns

### **Example Code and Templates**
- **Working Integrations**: `/Integrations/01-tray/Embedded/` for reference (multi-workflow examples)
- **OHFY-Core Source**: `/github-repos/OHFY-Core/` for business logic understanding
- **Consolidated Examples**: **[Consolidated Scenario Examples](./CONSOLIDATED_SCENARIO_EXAMPLES.md)** for complete implementations

---

**🎯 Goal**: Transform complex, distributed integration architectures into streamlined, maintainable single-script solutions that retain all functionality while dramatically simplifying development, testing, and maintenance.

**Next Step**: Choose your integration type and dive into **[Script Consolidation Patterns](./SCRIPT_CONSOLIDATION_PATTERNS.md)** to get started!