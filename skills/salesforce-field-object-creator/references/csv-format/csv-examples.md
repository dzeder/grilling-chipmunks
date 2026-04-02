# CSV Examples

This document provides example CSVs for common scenarios.

## Example 1: Simple Fields Only

Basic custom fields on existing Account object:

```csv
Object,Field_Label,API_Name,Type,Length,Required,Unique,Notes
Account,Supplier Code,Supplier_Code__c,Text,50,true,true,"Unique supplier identifier"
Account,Annual Contract Value,Annual_Contract_Value__c,Currency,,,false,"Total annual revenue from account"
Account,Contract Start Date,Contract_Start_Date__c,Date,,,false,"Account activation date"
Account,Active Customer,Active_Customer__c,Checkbox,,,,"Is account currently active"
Account,Support Email,Support_Email__c,Email,,,,"Primary support contact email"
Account,Website,Website__c,Url,,,,"Company website"
```

## Example 2: Custom Object with Fields

New custom object `Product_Review__c` with multiple field types:

```csv
Object,Field_Label,API_Name,Type,Length,Precision,Scale,Required,DefaultValue,Notes
Product_Review__c,Review Title,Review_Title__c,Text,255,,, true,,"Title of customer review"
Product_Review__c,Review Text,Review_Text__c,LongTextArea,32768,,,false,,"Detailed review content"
Product_Review__c,Rating,Rating__c,Number,,2,0,true,5,"Rating out of 5 stars"
Product_Review__c,Review Date,Review_Date__c,Date,,,, true,,"Date review was submitted"
Product_Review__c,Verified Purchase,Verified_Purchase__c,Checkbox,,,,false,false,"Was this a verified purchase"
Product_Review__c,Helpful Count,Helpful_Count__c,Number,,18,0,false,0,"Number of helpful votes"
```

## Example 3: Master-Detail Relationships

Parent-child object pair with roll-up summary:

```csv
Object,Field_Label,API_Name,Type,Notes
Order__c,Order Number,Order_Number__c,Text,"Format: ORD-{0000}"
Order__c,Order Date,Order_Date__c,Date,"Date order was placed"
Order__c,Total Amount,Total_Amount__c,Summary,"Interactive: SUM of Order_Item__c.Amount__c"
Order_Item__c,Order,Order__c,MasterDetail,"Interactive: Link to Order__c (parent)"
Order_Item__c,Product,Product__c,Lookup,"Interactive: Link to Product__c"
Order_Item__c,Quantity,Quantity__c,Number,"Quantity ordered"
Order_Item__c,Unit Price,Unit_Price__c,Currency,"Price per unit"
Order_Item__c,Amount,Amount__c,Formula,"Interactive: Quantity__c * Unit_Price__c"
```

## Example 4: MCBC Salsify Fields (Real Example)

Fields from actual MCBC Salsify integration (partial):

```csv
Object,Field_Label,API_Name,Type,Length,Precision,Scale,Notes
ohfy__Item__c,Outer Pack UPC,Outer_Pack_UPC__c,Text,255,,"UPC code for outer packaging"
ohfy__Item__c,Consumer Pack Count,Consumer_Pack_Count__c,Number,,18,0,"Number of consumer units per pack"
ohfy__Item__c,Retail Start Date,Retail_Start_Date__c,Date,,,"Product availability start date"
ohfy__Item__c,Container Type,Container_Type__c,Picklist,,"Interactive: BOTTLE, CAN, KEG"
ohfy__Item__c,Consumer Unit Volume,Consumer_Unit_Volume__c,Number,,18,4,"Volume of individual consumer unit"
ohfy__Item__c,Consumer Unit Volume UOM,Consumer_Unit_Volume_UOM__c,Picklist,,"Interactive: OZ"
ohfy__Item__c,Ingredients and Fermentation Sources,Ingredients_and_Fermentation_Sources__c,LongTextArea,32768,,"Detailed ingredient list"
ohfy__Item__c,Gluten Free,Gluten_Free__c,Picklist,,"Interactive: Yes, No"
```

## Example 5: Mandate Objects (Real Example from D's CSV)

Complete Mandate objects with mixed field types:

```csv
Object,Field_Label,API_Name,Type,Precision,Scale,Notes
Mandate__c,Activity Name,Activity_Name__c,Text,,"From activity_name"
Mandate__c,Brand,Brand__c,Text,,"From brand"
Mandate__c,Brand Pack,Brand_Pack__c,Text,,"From brand_pack"
Mandate__c,Chain Activity ID,Chain_Activity_ID__c,Text,,"From chain_activity_id"
Mandate__c,Chain Execution Detail ID,Chain_Execution_Detail_Id__c,Text,,
Mandate__c,Chain Execution Minimum Product Count,Chain_Execution_Minimum_Product_Count__c,Number,16,2,
Mandate__c,Chain Execution Possible Product Count,Chain_Execution_Possible_Product_Count__c,Number,16,2,
Mandate__c,Dist Location ID,Dist_Location_ID__c,Text,,"From dist_location_id"
Mandate__c,End Date,End_Date__c,Date,,"From end_date"
Mandate__c,Start Date,Start_Date__c,Date,,"From start_date"
Mandate__c,Ship Number,Ship_Number__c,Number,,,"From ship_number"
Mandate__c,Store Number,Store_Number__c,Text,,"From store_number"
Mandate__c,Parent Account,Parent_Account__c,MasterDetail,,"Interactive: Link to Account"
Mandate__c,Total Quantity Fulfilled,Total_Quantity_Fulfilled__c,Summary,,"Interactive: SUM Mandate_Item__c.Quantity_Fulfilled__c"
Mandate_Item__c,Item,Item__c,MasterDetail,,"Interactive: Link to ohfy__Item__c"
Mandate_Item__c,Mandate,Mandate__c,MasterDetail,,"Interactive: Link to Mandate__c"
Mandate_Item__c,Quantity Fulfilled,Quantity_Fulfilled__c,Number,16,2,"Will roll up to Mandate__c"
```

## Example 6: Formula Fields

Various formula field examples:

```csv
Object,Field_Label,API_Name,Type,Notes
Contact,Full Name,Full_Name__c,Formula,"Interactive: FirstName & "" "" & LastName (Text)"
ohfy__Item__c,Total Weight,Total_Weight__c,Formula,"Interactive: Consumer_Pack_Count__c * Consumer_Unit_Net_Weight__c (Number)"
Opportunity,Days Until Close,Days_Until_Close__c,Formula,"Interactive: CloseDate - TODAY() (Number)"
Product__c,Profit Margin,Profit_Margin__c,Formula,"Interactive: (Sale_Price__c - Cost__c) / Sale_Price__c (Percent)"
Account,High Value,High_Value__c,Formula,"Interactive: IF(AnnualRevenue > 1000000, ""Yes"", ""No"") (Text)"
```

## Example 7: Integration External ID Pattern

Fields optimized for integration:

```csv
Object,Field_Label,API_Name,Type,Length,Required,Unique,ExternalId,Notes
Product__c,Supplier SKU,Supplier_SKU__c,Text,100,true,true,true,"External system product ID"
Account,CRM Account ID,CRM_Account_ID__c,Text,50,false,true,true,"Legacy CRM system ID"
Order__c,ERP Order Number,ERP_Order_Number__c,Text,50,true,true,true,"Order number from ERP"
ohfy__Item__c,Salsify Product ID,Salsify_Product_ID__c,Text,100,false,true,true,"Product ID from Salsify PIM"
```

## Example 8: Encrypted and Sensitive Data

Fields with encryption and masking:

```csv
Object,Field_Label,API_Name,Type,Length,MaskChar,MaskType,Notes
Account,API Key,API_Key__c,EncryptedText,175,asterisk,all,"Client API credential"
Contact,SSN,SSN__c,EncryptedText,11,X,ssn,"Social Security Number"
Account,Credit Card Token,Credit_Card_Token__c,EncryptedText,175,asterisk,creditCard,"Tokenized payment info"
```

## Example 9: Geolocation and Special Types

Special field types with advanced configurations:

```csv
Object,Field_Label,API_Name,Type,Scale,Notes
Location__c,Warehouse Location,Warehouse_Location__c,Location,5,"GPS coordinates for warehouse"
Location__c,Store Location,Store_Location__c,Location,5,"GPS coordinates for store"
Custom_Case__c,Case Number,Case_Number__c,AutoNumber,,"Format: CASE-{0000}, Starting: 1"
```

## Example 10: Multi-Object Comprehensive CSV

Multiple objects with various field types in single CSV:

```csv
Object,Field_Label,API_Name,Type,Length,Precision,Scale,Required,Unique,ExternalId,DefaultValue,Notes
Project__c,Project Name,Project_Name__c,Text,255,,,true,false,false,,"Project identifier"
Project__c,Start Date,Start_Date__c,Date,,,, true,false,false,,"Project kickoff date"
Project__c,Budget,Budget__c,Currency,,18,2,true,false,false,0,"Total project budget"
Project__c,Completion Rate,Completion_Rate__c,Percent,,5,2,false,false,false,0,"Percent complete"
Project__c,Status,Status__c,Picklist,,,,false,,,,"Interactive: Planning, Active, Completed, On Hold"
Task__c,Project,Project__c,MasterDetail,,,,,,,"Interactive: Link to Project__c (parent)"
Task__c,Task Name,Task_Name__c,Text,255,,,true,,,,"Task description"
Task__c,Due Date,Due_Date__c,Date,,,, true,,,,"Task deadline"
Task__c,Assigned To,Assigned_To__c,Lookup,,,,false,,,,"Interactive: Link to User"
Task__c,Completed,Completed__c,Checkbox,,,,false,,, false,"Is task complete"
Task__c,Hours Logged,Hours_Logged__c,Number,,5,2,false,,,0,"Time spent on task"
Project__c,Total Hours,Total_Hours__c,Summary,,,,,,,"Interactive: SUM Task__c.Hours_Logged__c"
Project__c,Tasks Completed,Tasks_Completed__c,Summary,,,,,,,"Interactive: COUNT Task__c where Completed__c = true"
```

---

## CSV Best Practices

1. **Group by Object**: Keep all fields for same object together
2. **Order Logically**: List objects before their child objects
3. **Document Relationships**: Use Notes column to explain MasterDetail/Lookup connections
4. **Mark Interactive**: Note "Interactive:" for fields requiring prompts
5. **Provide Defaults**: Include DefaultValue for fields that should have initial values
6. **Use External IDs**: Mark integration key fields as ExternalId=true
7. **Be Specific in Notes**: Include format, source system, or business rules

---

## Template CSV

Use this template to start your own CSV:

```csv
Object,Field_Label,API_Name,Type,Length,Precision,Scale,Required,Unique,ExternalId,DefaultValue,Notes
Custom_Object__c,Example Text,Example_Text__c,Text,255,,,false,false,false,,"Description here"
Custom_Object__c,Example Number,Example_Number__c,Number,,18,2,false,false,false,0,"Description here"
Custom_Object__c,Example Date,Example_Date__c,Date,,,, false,false,false,,"Description here"
Custom_Object__c,Example Checkbox,Example_Checkbox__c,Checkbox,,,,false,,,false,"Description here"
Custom_Object__c,Example Picklist,Example_Picklist__c,Picklist,,,,false,,,,"Interactive: Enter values"
Custom_Object__c,Example Lookup,Example_Lookup__c,Lookup,,,,false,,,,"Interactive: Specify related object"
```

---

## Source
Based on real integration CSVs from:
- MCBC Salsify integration (63 fields across 3 objects)
- Mandate Object specification (29 fields)
- Ohanafy integration patterns
