# OHFY-Data_Model Source Index
> Last synced: 2026-04-07T12:28:31Z | Commit: e084de4 | Repo: Ohanafy/OHFY-Data_Model

## Apex Classes

_No Apex classes found._

## Triggers

_No triggers found._

## Service Methods

_No service classes found._

## Cross-Object Relationships (169)

| From Object | Field | Type | To Object |
|-------------|-------|------|-----------|
| Account_Route__c | Customer__c | MasterDetail | Account |
| Account_Route__c | Route__c | MasterDetail | Route__c |
| Account | Billing_Contact__c | Lookup | Contact |
| Account | Chain_Banner__c | Lookup | Account |
| Account | Delivery_Contact__c | Lookup | Contact |
| Account | Fulfillment_Location__c | Lookup | Location__c |
| Account | Pricelist__c | Lookup | Pricelist__c |
| Account | Sales_Rep__c | Lookup | User |
| Account | Territory__c | Lookup | Territory__c |
| Activity_Goal__c | Goal__c | MasterDetail | Goal__c |
| Allocation__c | Customer__c | Lookup | Account |
| Allocation__c | Item__c | Lookup | Item__c |
| Allocation__c | Location__c | Lookup | Location__c |
| Allocation__c | Sales_Rep__c | Lookup | User |
| Billback__c | Incentive__c | Lookup | Incentive__c |
| Commitment_Item__c | Commitment__c | MasterDetail | Commitment__c |
| Commitment_Item__c | Item__c | MasterDetail | Item__c |
| Commitment__c | Account_Distributor__c | Lookup | Account |
| Commitment__c | Customer__c | Lookup | Account |
| Control_State_Code__c | Item__c | Lookup | Item__c |
| Credit__c | Account__c | MasterDetail | Account |
| Credit__c | Delivery__c | Lookup | Delivery__c |
| Credit__c | Invoice__c | Lookup | Invoice__c |
| Credit__c | Item__c | Lookup | Item__c |
| Credit__c | Return_Location__c | Lookup | Location__c |
| Delivery__c | Driver__c | Lookup | User |
| Delivery__c | Route__c | Lookup | Route__c |
| Delivery__c | Vehicle__c | Lookup | Equipment__c |
| Depletion__c | Customer__c | MasterDetail | Account |
| Depletion__c | Item__c | Lookup | Item__c |
| Display_Item__c | Display__c | MasterDetail | Display__c |
| Display_Item__c | Item__c | Lookup | Item__c |
| Display_Run__c | Chain_Banner__c | MasterDetail | Account |
| Display__c | Account__c | Lookup | Account |
| Display__c | Display_Run__c | MasterDetail | Display_Run__c |
| Equipment__c | Fulfillment_Location__c | MasterDetail | Location__c |
| Equipment__c | Truck_Location__c | Lookup | Location__c |
| Equipment__c | Vendor__c | Lookup | Account |
| Financial_Account__c | Parent_Account__c | Lookup | Financial_Account__c |
| Goal__c | Account__c | Lookup | Account |
| Goal__c | Contact__c | Lookup | Contact |
| Goal__c | Goal_Template__c | Lookup | Goal_Template__c |
| Goal__c | Incentive__c | Lookup | Incentive__c |
| Goal__c | Item_Type__c | Lookup | Item_Type__c |
| Goal__c | Item__c | Lookup | Item__c |
| Goal__c | Supplier__c | Lookup | Item_Line__c |
| Goal__c | Territory__c | Lookup | Territory__c |
| Goal__c | User__c | Lookup | User |
| Incentive__c | Billback__c | Lookup | Billback__c |
| Incentive__c | Goal_Template__c | Lookup | Goal_Template__c |
| Incentive__c | Item_Type__c | Lookup | Item_Type__c |
| Incentive__c | Item__c | Lookup | Item__c |
| Incentive__c | Supplier__c | Lookup | Item_Line__c |
| Integration_Sync_Failure__c | Integration_Sync__c | MasterDetail | Integration_Sync__c |
| Inventory_Adjustment__c | Credit__c | Lookup | Credit__c |
| Inventory_Adjustment__c | Inventory_Log__c | Lookup | Inventory_Log__c |
| Inventory_Adjustment__c | Inventory_Receipt_Item__c | Lookup | Inventory_Receipt_Item__c |
| Inventory_Adjustment__c | Inventory_Receipt__c | Lookup | Inventory_Receipt__c |
| Inventory_Adjustment__c | Inventory__c | MasterDetail | Inventory__c |
| Inventory_Adjustment__c | Invoice_Item__c | Lookup | Invoice_Item__c |
| Inventory_Adjustment__c | Invoice__c | Lookup | Invoice__c |
| Inventory_Adjustment__c | Lot_Inventory__c | Lookup | Lot_Inventory__c |
| Inventory_Adjustment__c | Lot__c | Lookup | Lot__c |
| Inventory_Adjustment__c | Purchase_Order_Item__c | Lookup | Purchase_Order_Item__c |
| Inventory_Adjustment__c | Purchase_Order__c | Lookup | Purchase_Order__c |
| Inventory_Adjustment__c | Transfer__c | Lookup | Transfer__c |
| Inventory_History__c | Inventory__c | MasterDetail | Inventory__c |
| Inventory_History__c | Item__c | MasterDetail | Item__c |
| Inventory_Log_Group__c | Location__c | Lookup | Location__c |
| Inventory_Log__c | Inventory_Log_Group__c | Lookup | Inventory_Log_Group__c |
| Inventory_Log__c | Inventory__c | MasterDetail | Inventory__c |
| Inventory_Log__c | Location__c | Lookup | Location__c |
| Inventory_Log__c | Lot_Inventory__c | Lookup | Lot_Inventory__c |
| Inventory_Receipt_Fee__c | Fee__c | MasterDetail | Fee__c |
| Inventory_Receipt_Fee__c | Inventory_Receipt__c | MasterDetail | Inventory_Receipt__c |
| Inventory_Receipt_Item__c | Inventory_Receipt_Item__c | Lookup | Inventory_Receipt_Item__c |
| Inventory_Receipt_Item__c | Inventory_Receipt__c | MasterDetail | Inventory_Receipt__c |
| Inventory_Receipt_Item__c | Item__c | MasterDetail | Item__c |
| Inventory_Receipt__c | Purchase_Order__c | MasterDetail | Purchase_Order__c |
| Inventory_Receipt__c | Supplier__c | Lookup | Account |
| Inventory__c | Item__c | MasterDetail | Item__c |
| Inventory__c | Location__c | Lookup | Location__c |
| Invoice_Adjustment__c | Adjustment__c | MasterDetail | Adjustment__c |
| Invoice_Adjustment__c | Invoice__c | MasterDetail | Invoice__c |
| Invoice_Fee__c | Fee__c | MasterDetail | Fee__c |
| Invoice_Fee__c | Invoice__c | MasterDetail | Invoice__c |
| Invoice_Goal__c | Goal__c | MasterDetail | Goal__c |
| Invoice_Goal__c | Invoice__c | MasterDetail | Invoice__c |
| Invoice_Group__c | Customer__c | Lookup | Account |
| Invoice_Item__c | Delivery__c | Lookup | Delivery__c |
| Invoice_Item__c | Invoice_Item__c | Lookup | Invoice_Item__c |
| Invoice_Item__c | Invoice__c | MasterDetail | Invoice__c |
| Invoice_Item__c | Item__c | MasterDetail | Item__c |
| Invoice__c | Customer__c | MasterDetail | Account |
| Invoice__c | Delivery__c | Lookup | Delivery__c |
| Invoice__c | Fulfillment_Location__c | Lookup | Location__c |
| Invoice__c | Invoice_Group__c | Lookup | Invoice_Group__c |
| Invoice__c | Pricelist__c | Lookup | Pricelist__c |
| Invoice__c | Sales_Rep__c | Lookup | User |
| Item_Component__c | Child_Item__c | Lookup | Item__c |
| Item_Component__c | Parent_Item__c | MasterDetail | Item__c |
| Item_Group_Rule__c | Customer__c | Lookup | Account |
| Item_Group_Rule__c | Item_Group__c | Lookup | Item_Group__c |
| Item_Line__c | Supplier__c | Lookup | Account |
| Item_Type_Territory_Exclusion__c | Item_Type__c | MasterDetail | Item_Type__c |
| Item_Type_Territory_Exclusion__c | Territory__c | MasterDetail | Territory__c |
| Item_Type__c | Item_Line__c | Lookup | Item_Line__c |
| Item__c | Item_Line__c | Lookup | Item_Line__c |
| Item__c | Item_Type__c | Lookup | Item_Type__c |
| Journal_Entry__c | Financial_Account__c | Lookup | Financial_Account__c |
| Journal_Entry__c | Inventory_Adjustment__c | MasterDetail | Inventory_Adjustment__c |
| Location__c | Parent_Location__c | Lookup | Location__c |
| Lot_Inventory_Receipt_Item__c | Inventory_Receipt_Item__c | Lookup | Inventory_Receipt_Item__c |
| Lot_Inventory_Receipt_Item__c | Lot__c | Lookup | Lot__c |
| Lot_Inventory__c | Inventory__c | MasterDetail | Inventory__c |
| Lot_Inventory__c | Lot__c | MasterDetail | Lot__c |
| Lot_Invoice_Item__c | Invoice_Item__c | Lookup | Invoice_Item__c |
| Lot_Invoice_Item__c | Lot__c | Lookup | Lot__c |
| Lot__c | Item__c | Lookup | Item__c |
| Lot__c | Supplier__c | Lookup | Account |
| Pallet_Item__c | Invoice_Item__c | Lookup | Invoice_Item__c |
| Pallet_Item__c | Pallet__c | MasterDetail | Pallet__c |
| Pallet__c | Delivery__c | Lookup | Delivery__c |
| Pallet__c | Invoice__c | Lookup | Invoice__c |
| Placement__c | Account__c | MasterDetail | Account |
| Placement__c | Item__c | MasterDetail | Item__c |
| Pricelist_Account__c | Account__c | MasterDetail | Account |
| Pricelist_Account__c | Pricelist__c | MasterDetail | Pricelist__c |
| Pricelist_Item__c | Front_Line_Promotion__c | Lookup | Promotion_Item__c |
| Pricelist_Item__c | Item__c | MasterDetail | Item__c |
| Pricelist_Item__c | Pricelist__c | MasterDetail | Pricelist__c |
| Pricelist_Setting__c | Pricelist_Group__c | Lookup | Pricelist_Group__c |
| Pricelist__c | Pricelist_Group__c | Lookup | Pricelist_Group__c |
| Promotion_Invoice_Item__c | Invoice_Item__c | Lookup | Invoice_Item__c |
| Promotion_Invoice_Item__c | Promotion__c | MasterDetail | Promotion__c |
| Promotion_Item_Line__c | Item_Line__c | MasterDetail | Item_Line__c |
| Promotion_Item_Line__c | Promotion__c | MasterDetail | Promotion__c |
| Promotion_Item_Type__c | Item_Type__c | MasterDetail | Item_Type__c |
| Promotion_Item_Type__c | Promotion__c | MasterDetail | Promotion__c |
| Promotion_Item__c | Item__c | MasterDetail | Item__c |
| Promotion_Item__c | Promotion__c | MasterDetail | Promotion__c |
| Promotion__c | Billback__c | Lookup | Billback__c |
| Promotion__c | Customer__c | Lookup | Account |
| Promotion__c | Territory__c | Lookup | Territory__c |
| Purchase_Order_Item__c | Item__c | MasterDetail | Item__c |
| Purchase_Order_Item__c | Purchase_Order_Item__c | Lookup | Purchase_Order_Item__c |
| Purchase_Order_Item__c | Purchase_Order__c | MasterDetail | Purchase_Order__c |
| Purchase_Order__c | Fulfillment_Location__c | Lookup | Location__c |
| Purchase_Order__c | Supplier__c | MasterDetail | Account |
| Related_Financial_Account__c | Accounting_Setting__c | MasterDetail | Accounting_Setting__c |
| Related_Financial_Account__c | Financial_Account__c | Lookup | Financial_Account__c |
| Retail_Inventory__c | Invoice__c | Lookup | Invoice__c |
| Retail_Inventory__c | Item__c | Lookup | Placement__c |
| Route__c | Driver__c | Lookup | User |
| Route__c | Vehicle__c | Lookup | Equipment__c |
| Survey__c | Account__c | MasterDetail | Account |
| Survey__c | Assigned_To__c | Lookup | User |
| Survey__c | Vehicle__c | Lookup | Equipment__c |
| Territory__c | Parent_Territory__c | Lookup | Territory__c |
| Tier_Setting__c | Item_Type__c | Lookup | Item_Type__c |
| Tier_Setting__c | Pricelist_Group__c | Lookup | Pricelist_Group__c |
| Transfer_Group__c | New_Location__c | Lookup | Location__c |
| Transfer_Group__c | Origin_Location__c | Lookup | Location__c |
| Transfer__c | Item__c | MasterDetail | Item__c |
| Transfer__c | New_Location__c | Lookup | Location__c |
| Transfer__c | Origin_Location__c | Lookup | Location__c |
| Transfer__c | Transfer_Group__c | Lookup | Transfer_Group__c |
| Trigger_Configuration__mdt | Trigger_Context__c | MetadataRelationship | Trigger_Context__mdt |
| Trigger_Configuration__mdt | sObject_Trigger__c | MetadataRelationship | sObject_Trigger__mdt |

## Custom Objects & Fields

### Account (122 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABC_License_Expiration_Date__c | Date | false |  |
| ABC_License_Number__c | Text | false |  |
| AccountNumber |  | false |  |
| AccountSource | Picklist | false |  |
| Account_Balance__c | Currency | false |  |
| AnnualRevenue |  | false |  |
| Average_Case_Equivalents__c | Number | false |  |
| Average_Invoice_Value__c | Currency | false |  |
| BillingAddress |  | false |  |
| Billing_Contact_Email__c | Text | false |  |
| Billing_Contact__c | Lookup | false | Contact |
| Billing_Street_Address__c | Text | false |  |
| Chain_Banner__c | Lookup | false | Account |
| Company_Name__c | Text | false |  |
| Customer_Acknowledgment_Type__c | Picklist | false |  |
| Customer_Number__c | Text | false |  |
| Customer_Priority__c | Picklist | false |  |
| Customer_Since__c | Date | false |  |
| DUNS_Number__c | Text | false |  |
| DandbCompanyId | Lookup | false |  |
| Days_Since_Last_Activity__c | Number | false |  |
| Days_Since_Last_Invoice__c | Number | false |  |
| Delivery_Contact__c | Lookup | false | Contact |
| Delivery_Method__c | Picklist | false |  |
| Description |  | false |  |
| Distributor_Vendor_ID_Number__c | Text | false |  |
| DunsNumber |  | false |  |
| EFT_Customer_ID__c | Text | false |  |
| EFT_Provider__c | Picklist | false |  |
| E_Commerce_Platform__c | Picklist | false |  |
| External_ID__c | Text | false |  |
| Fax |  | false |  |
| First_Sold_Date__c | Date | false |  |
| Fulfillment_Location__c | Lookup | false | Location__c |
| GS1_Prefix__c | Text | false |  |
| Has_Been_Sold_To__c | Checkbox | false |  |
| Highest_Stop_Order__c | Summary | false |  |
| Industry | Picklist | false |  |
| Invoice_Date__c | Date | false |  |
| Invoice_Notes__c | LongTextArea | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Chain_Banner__c | Checkbox | false |  |
| Is_Child_Account__c | Checkbox | false |  |
| Is_Tax_Exempt__c | Checkbox | false |  |
| Jigsaw |  | false |  |
| Keg_Deposit_Credit_Amount__c | Currency | false |  |
| Last_Invoice_Date__c | Date | false |  |
| Last_Purchase_Order_Date__c | Date | false |  |
| Lead_Time__c | Number | false |  |
| Legal_Name__c | Text | false |  |
| License_Expiration_Date__c | Date | false |  |
| Lost_Placement_After_Days__c | Number | false |  |
| Market__c | Picklist | false |  |
| Maximum_DOI__c | Number | false |  |
| NaicsCode |  | false |  |
| NaicsDesc |  | false |  |
| Name |  | false |  |
| NumberOfEmployees |  | false |  |
| NumberofLocations__c | Number | false |  |
| Offline_Commitment__c | LongTextArea | false |  |
| Offline_Contact__c | LongTextArea | false |  |
| Offline_Event__c | LongTextArea | false |  |
| Offline_Record_Type__c | Text | false |  |
| Offline_Task__c | LongTextArea | false |  |
| Ohanafy_Master_ID__c | Text | false |  |
| OwnerId | Lookup | false |  |
| Ownership | Picklist | false |  |
| ParentId | Hierarchy | false |  |
| Payment_Method__c | Picklist | false |  |
| Payment_Partner__c | Picklist | false |  |
| Payment_Terms__c | Picklist | false |  |
| Permit_Number__c | Text | false |  |
| Phone |  | false |  |
| Premise_Type__c | Picklist | false |  |
| Pricelist__c | Lookup | false | Pricelist__c |
| Prospect_Stage__c | Picklist | false |  |
| QuickBooks_Customer_ID__c | Text | false |  |
| Rating | Picklist | false |  |
| Retail_Type__c | Picklist | false |  |
| Retailer_Identification_Number__c | Text | false |  |
| Revenue_Goal__c | Currency | false |  |
| Sales_Rep__c | Lookup | false | User |
| ShippingAddress |  | false |  |
| Shipping_Address__c | Text | false |  |
| Should_Auto_Bill__c | Checkbox | false |  |
| Should_Bypass_Transaction_Fees__c | Checkbox | false |  |
| Should_Charge_Processing_Fee__c | Checkbox | false |  |
| Should_Waive_Item_Deposit__c | Checkbox | false |  |
| Sic |  | false |  |
| SicDesc |  | false |  |
| Site |  | false |  |
| Store_Number__c | Text | false |  |
| Supplier_Keg_Deposit__c | Currency | false |  |
| Target_DOI__c | Number | false |  |
| Territory__c | Lookup | false | Territory__c |
| TickerSymbol |  | false |  |
| Tier |  | false |  |
| Total_Case_Equivalents__c | Summary | false |  |
| Total_Credits_Applied__c | Summary | false |  |
| Total_Credits_Available__c | Summary | false |  |
| Total_Draft_Lines__c | Number | false |  |
| Total_Invoice_Count__c | Summary | false |  |
| Total_Invoice_Revenue__c | Summary | false |  |
| Total_Invoice_Value__c | Summary | false |  |
| Total_Remaining_Credits__c | Currency | false |  |
| Total_Routes__c | Summary | false |  |
| Tradestyle |  | false |  |
| Type | Picklist | false |  |
| WalMart_Customer_Reference_Number__c | Text | false |  |
| Walgreens_Distributor_AP_Number__c | Text | false |  |
| Was_Created_Offline_Commitment__c | Checkbox | false |  |
| Was_Created_Offline_Contact__c | Checkbox | false |  |
| Was_Created_Offline_Event__c | Checkbox | false |  |
| Was_Created_Offline_Task__c | Checkbox | false |  |
| Was_Created_Offline__c | Checkbox | false |  |
| Was_Updated_Offline_Commitment__c | Checkbox | false |  |
| Was_Updated_Offline_Contact__c | Checkbox | false |  |
| Was_Updated_Offline_Event__c | Checkbox | false |  |
| Was_Updated_Offline_Task__c | Checkbox | false |  |
| Was_Updated_Offline__c | Checkbox | false |  |
| Website |  | false |  |
| YearStarted |  | false |  |

### Account_Route__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer__c | MasterDetail | false | Account |
| End_Time__c | Time | false |  |
| Is_Active_Route__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Route__c | MasterDetail | false | Route__c |
| Start_Time__c | Time | false |  |
| Stop_Order__c | Number | false |  |

### Accounting_Mapping__mdt (14 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Category__c | Text | false |  |
| Credit_Memo_ID_Company_2__c | Text | false |  |
| Credit_Memo_ID__c | Text | false |  |
| Holding_ID__c | Text | false |  |
| Is_Active__c | Checkbox | false |  |
| Purchase_ID_Company_2__c | Text | false |  |
| Purchase_ID__c | Text | false |  |
| Return_ID_Company_2__c | Text | false |  |
| Return_ID__c | Text | false |  |
| Sales_ID_Company_2__c | Text | false |  |
| Sales_ID__c | Text | false |  |
| Sub_Type__c | Text | false |  |
| Type__c | Text | false |  |
| Variance_ID__c | Text | false |  |

### Accounting_Setting__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Category__c | Picklist | false |  |
| Count_Bill__c | Summary | false |  |
| Count_Credit_Memo__c | Summary | false |  |
| Count_Customer__c | Summary | false |  |
| Count_Invoice__c | Summary | false |  |
| Count_Journal_Entry__c | Summary | false |  |
| Count_Purchase_Order__c | Summary | false |  |
| Count_Supplier__c | Summary | false |  |
| Key__c | Text | false |  |
| Subtype__c | Picklist | false |  |
| Type__c | Picklist | false |  |

### Activity (1 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Is_Completed__c | Checkbox | false |  |

### Activity_Goal__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Activity_Id__c | Text | false |  |
| Goal__c | MasterDetail | false | Goal__c |
| Type__c | Picklist | false |  |

### Adjustment__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Adjustment_Type__c | Picklist | false |  |
| Cost_Type__c | Picklist | false |  |
| Dollar_Amount__c | Currency | false |  |
| End_Date__c | Date | false |  |
| Is_Active__c | Checkbox | false |  |
| Item_Types__c | MultiselectPicklist | false |  |
| Market__c | MultiselectPicklist | false |  |
| Packaging_Type__c | Picklist | false |  |
| Percent_Amount__c | Percent | false |  |
| Start_Date__c | Date | false |  |
| States__c | MultiselectPicklist | false |  |

### Allocation__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Allocated_Case_Amount__c | Number | false |  |
| Allocated_Cases_Remaining__c | Number | false |  |
| Allocated_Cases_Sold__c | Number | false |  |
| Customer__c | Lookup | false | Account |
| End_Date__c | Date | false |  |
| Is_Active__c | Checkbox | false |  |
| Item__c | Lookup | false | Item__c |
| Location__c | Lookup | false | Location__c |
| Sales_Rep__c | Lookup | false | User |
| Start_Date__c | Date | false |  |

### Billback__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Incentive__c | Lookup | false | Incentive__c |
| Is_Active__c | Checkbox | false |  |
| Outstanding_Cases__c | Currency | false |  |
| Revenue_Amount__c | Currency | false |  |
| Total_Cases__c | Number | false |  |

### Commitment_Item__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Case_Quantity__c | Number | false |  |
| Commitment__c | MasterDetail | false | Commitment__c |
| Item__c | MasterDetail | false | Item__c |

### Commitment__c (8 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Distributor__c | Lookup | false | Account |
| Customer__c | Lookup | false | Account |
| Date__c | Date | false |  |
| Distributor_Status__c | Picklist | false |  |
| Involved_Sales_Rep__c | Text | false |  |
| Notes__c | Text | false |  |
| Offline_Items__c | LongTextArea | false |  |
| Was_Created_Offline__c | Checkbox | false |  |

### Configuration_Preference__mdt (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Description__c | Text | false |  |
| Is_Active__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Value__c | Text | false |  |

### Contact (32 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| AccountId | Lookup | false |  |
| AssistantName |  | false |  |
| AssistantPhone |  | false |  |
| Birthdate |  | false |  |
| Department |  | false |  |
| Description |  | false |  |
| DoNotCall |  | false |  |
| Email |  | false |  |
| Fax |  | false |  |
| GenderIdentity | Picklist | false |  |
| HasOptedOutOfEmail |  | false |  |
| HasOptedOutOfFax |  | false |  |
| HomePhone |  | false |  |
| IndividualId | Lookup | false |  |
| Is_Billing_Contact__c | Checkbox | false |  |
| Is_Delivery_Contact__c | Checkbox | false |  |
| Jigsaw |  | false |  |
| Languages__c | Text | false |  |
| LastCURequestDate |  | false |  |
| LastCUUpdateDate |  | false |  |
| LeadSource | Picklist | false |  |
| Level__c | Picklist | false |  |
| MailingAddress |  | false |  |
| MobilePhone |  | false |  |
| Name |  | false |  |
| OtherAddress |  | false |  |
| OtherPhone |  | false |  |
| OwnerId | Lookup | false |  |
| Phone |  | false |  |
| Pronouns | Picklist | false |  |
| ReportsToId | Lookup | false |  |
| Title |  | false |  |

### Control_State_Code__c (1 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Item__c | Lookup | false | Item__c |

### Credit__c (32 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | MasterDetail | false | Account |
| Adjustment__c | Currency | false |  |
| Case_Price__c | Currency | false |  |
| Case_Quantity__c | Number | false |  |
| Case_Total__c | Currency | false |  |
| Credit_Date__c | Date | false |  |
| Credit_Type__c | Picklist | false |  |
| Delivery__c | Lookup | false | Delivery__c |
| Has_Integration_Sync__c | Checkbox | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Invoice__c | Lookup | false | Invoice__c |
| Is_Offline_Add_To_Truck__c | Checkbox | false |  |
| Is_Offline_Apply__c | Checkbox | false |  |
| Is_Offline_Deduct_From_Invoice__c | Checkbox | false |  |
| Item__c | Lookup | false | Item__c |
| Keg_Deposit__c | Currency | false |  |
| Offline_Lot__c | Date | false |  |
| Quantity_UOM__c | Text | false |  |
| QuickBooks_Credit_Memo_ID_Company_2__c | Text | false |  |
| QuickBooks_Credit_Memo_ID__c | Text | false |  |
| Reason__c | Picklist | false |  |
| Return_Location__c | Lookup | false | Location__c |
| Rollover_Amount__c | Currency | false |  |
| Total_Quantity_Cases__c | Number | false |  |
| Total_Units__c | Currency | false |  |
| Total__c | Currency | false |  |
| Unit_Price__c | Currency | false |  |
| Unit_Quantity__c | Number | false |  |
| Units_Per_Case__c | Number | false |  |
| Was_Created_Offline__c | Checkbox | false |  |
| Was_Edited_Offline__c | Checkbox | false |  |
| Was_Picked_Up__c | Checkbox | false |  |

### Criteria__c (1 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Field_API_Name__c | Text | false |  |

### Customer_Information__mdt (15 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABC_Number__c | Text | false |  |
| Billing_City__c | Text | false |  |
| Billing_County__c | Text | false |  |
| Billing_Postal_Code__c | Text | false |  |
| Billing_State__c | Text | false |  |
| Billing_Street__c | Text | false |  |
| Customer_Legal_Name__c | Text | false |  |
| Division_Id__c | Text | false |  |
| EIN__c | Text | false |  |
| Entity_Type__c | Text | false |  |
| Is_Active__c | Checkbox | false |  |
| Owner_Name__c | Text | false |  |
| Owner_Title__c | Text | false |  |
| Phone_Number__c | Phone | false |  |
| TTB_Brewery_Number__c | Text | false |  |

### Delivery__c (23 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Appointment_Number__c | Text | false |  |
| Cancelled_Reason__c | Text | false |  |
| Day_Of_Week__c | Picklist | false |  |
| Delivery_Date__c | Date | false |  |
| Delivery_Number__c | AutoNumber | false |  |
| Driver__c | Lookup | false | User |
| Is_Auto_Palletized__c | Checkbox | false |  |
| Is_Locked__c | Checkbox | false |  |
| Route__c | Lookup | false | Route__c |
| Status__c | Picklist | false |  |
| Total_Backordered__c | Number | false |  |
| Total_Cases_Backordered__c | Number | false |  |
| Total_Cases__c | Number | false |  |
| Total_Invoice_Items__c | Number | false |  |
| Total_Invoices__c | Number | false |  |
| Total_Kegs_Backordered__c | Number | false |  |
| Total_Kegs__c | Number | false |  |
| Total_Revenue__c | Currency | false |  |
| Total_Unique_Customers__c | Number | false |  |
| Total_Weight_UOM__c | Text | false |  |
| Total_Weight__c | Number | false |  |
| Vehicle__c | Lookup | false | Equipment__c |
| Was_Returned__c | Checkbox | false |  |

### Depletion__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Case_Quantity__c | Number | false |  |
| Customer__c | MasterDetail | false | Account |
| Date__c | Date | false |  |
| Item__c | Lookup | false | Item__c |
| Type__c | Picklist | false |  |

### Display_Item__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Display__c | MasterDetail | false | Display__c |
| Item__c | Lookup | false | Item__c |
| Sales_Growth_Before_After__c | Percent | false |  |
| Sales_Growth_Before_During__c | Percent | false |  |
| Sales_Growth_During_After__c | Percent | false |  |
| Total_Case_Equivalents_After_Period__c | Number | false |  |
| Total_Case_Equivalents_Before_Period__c | Number | false |  |
| Total_Case_Equivalents_During_Period__c | Number | false |  |
| Total_Sales_After_Period__c | Currency | false |  |
| Total_Sales_Before_Period__c | Currency | false |  |
| Total_Sales_During_Period__c | Currency | false |  |

### Display_Run__c (16 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Chain_Banner__c | MasterDetail | false | Account |
| Display_Compliance__c | Percent | false |  |
| End_Date__c | Date | false |  |
| Is_Active__c | Checkbox | false |  |
| Start_Date__c | Date | false |  |
| Total_Active_Displays__c | Summary | false |  |
| Total_Displays__c | Summary | false |  |
| Total_Item_Case_Equivalents_After__c | Summary | false |  |
| Total_Item_Case_Equivalents_Before__c | Summary | false |  |
| Total_Item_Case_Equivalents_During__c | Summary | false |  |
| Total_Item_Sales_After__c | Summary | false |  |
| Total_Item_Sales_Before__c | Summary | false |  |
| Total_Item_Sales_During__c | Summary | false |  |
| Track_Days_After__c | Number | false |  |
| Track_Days_Before__c | Number | false |  |
| Track_Days_During__c | Number | false |  |

### Display__c (16 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account__c | Lookup | false | Account |
| After_Display_End_Date__c | Date | false |  |
| After_Display_Start_Date__c | Date | false |  |
| Before_Display_End_Date__c | Date | false |  |
| Before_Display_Start_Date__c | Date | false |  |
| Days_Until_End__c | Number | false |  |
| Display_Run__c | MasterDetail | false | Display_Run__c |
| Is_Active__c | Number | false |  |
| Is_Display_Run_Active__c | Checkbox | false |  |
| Status__c | Picklist | false |  |
| Total_Item_Case_Equivalents_After__c | Summary | false |  |
| Total_Item_Case_Equivalents_Before__c | Summary | false |  |
| Total_Item_Case_Equivalents_During__c | Summary | false |  |
| Total_Item_Sales_After__c | Summary | false |  |
| Total_Item_Sales_Before__c | Summary | false |  |
| Total_Item_Sales_During__c | Summary | false |  |

### Equipment__c (15 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Abbreviation__c | Text | false |  |
| Equipment_Cost__c | Currency | false |  |
| Fulfillment_Location__c | MasterDetail | false | Location__c |
| Is_Inventory_Bearing__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Notes__c | LongTextArea | false |  |
| Purchase_Date__c | Date | false |  |
| Serial_Number__c | Text | false |  |
| Status__c | Picklist | false |  |
| System__c | Picklist | false |  |
| Tare_Weight__c | Number | false |  |
| Truck_Location__c | Lookup | false | Location__c |
| Type__c | Picklist | false |  |
| Vendor__c | Lookup | false | Account |
| Warranty_Expiration_Date__c | Date | false |  |

### Fee__c (12 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Allocation_Method__c | Picklist | false |  |
| Amount__c | Currency | false |  |
| Default_Amount__c | Currency | false |  |
| Fee_ID__c | Text | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Inventory_Receipt__c | Checkbox | false |  |
| Is_Invoice__c | Checkbox | false |  |
| Is_Transaction_Fee__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Quantity__c | Number | false |  |
| Type__c | Picklist | false |  |

### Fieldset_Customization__mdt (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Fieldset_Name__c | Text | false |  |
| Fieldset_Purpose__c | Picklist | false |  |
| Object_Name__c | Text | false |  |

### Financial_Account__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Detail_Type__c | Picklist | false |  |
| Parent_Account__c | Lookup | false | Financial_Account__c |
| Type__c | Picklist | false |  |

### Goal_Template__c (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Is_Active__c | Checkbox | false |  |
| Tracking_Object_API__c | Text | false |  |
| Tracking_Object_Field_Value__c | Text | false |  |
| Tracking_Object_Field__c | Text | false |  |

### Goal__c (23 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Type__c | Text | false |  |
| Account__c | Lookup | false | Account |
| Attainment_Percent__c | Percent | false |  |
| Attainment_Revenue__c | Currency | false |  |
| Attainment__c | Number | false |  |
| Case_Amount__c | Number | false |  |
| Completions__c | Number | false |  |
| Contact__c | Lookup | false | Contact |
| End_Date__c | Date | false |  |
| Goal_Template__c | Lookup | false | Goal_Template__c |
| Incentive__c | Lookup | false | Incentive__c |
| Is_Active__c | Checkbox | false |  |
| Is_Incentive_Active__c | Checkbox | false |  |
| Is_Mandate__c | Checkbox | false |  |
| Item_Type__c | Lookup | false | Item_Type__c |
| Item__c | Lookup | false | Item__c |
| Revenue_Amount__c | Currency | false |  |
| Start_Date__c | Date | false |  |
| Supplier__c | Lookup | false | Item_Line__c |
| Territory__c | Lookup | false | Territory__c |
| Total_Completion__c | Number | false |  |
| Type__c | Picklist | false |  |
| User__c | Lookup | false | User |

### Incentive__c (20 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Attainment_Percent__c | Percent | false |  |
| Attainment_Revenue__c | Currency | false |  |
| Attainment__c | Number | false |  |
| Billback__c | Lookup | false | Billback__c |
| Case_Amount__c | Number | false |  |
| Completions__c | Number | false |  |
| End_Date__c | DateTime | false |  |
| Goal_Template__c | Lookup | true | Goal_Template__c |
| Has_Billback__c | Checkbox | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_On_Premises__c | Checkbox | false |  |
| Is_Team_Incentive__c | Checkbox | false |  |
| Item_Type__c | Lookup | false | Item_Type__c |
| Item__c | Lookup | false | Item__c |
| Revenue_Amount__c | Currency | false |  |
| Reward__c | LongTextArea | false |  |
| Should_Include_Inactive_Placements__c | Checkbox | false |  |
| Start_Date__c | Date | false |  |
| Supplier__c | Lookup | false | Item_Line__c |
| Type__c | Picklist | true |  |

### Integration_Sync_Failure__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Failure_Reason__c | LongTextArea | false |  |
| Integration_Sync__c | MasterDetail | false | Integration_Sync__c |
| Link_to_Record__c | Url | false |  |

### Integration_Sync__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Attempted_Record_Count__c | Number | false |  |
| Failure_Record_Count__c | Summary | false |  |
| Integration__c | Picklist | false |  |
| Records_to_Sync__c | MultiselectPicklist | true |  |
| Status__c | Picklist | false |  |
| Succeeded_Record_Count__c | Number | false |  |

### Inventory_Adjustment__c (55 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Key_Calculated__c | LongTextArea | false |  |
| Average_Case_Cost__c | Currency | false |  |
| Case_Cost__c | Currency | false |  |
| Cloned_Adjustment__c | Text | false |  |
| Company_Key__c | Text | false |  |
| Credit__c | Lookup | false | Credit__c |
| Date__c | Date | false |  |
| Inventory_Adjustment_Number__c | Number | false |  |
| Inventory_Log_Key__c | Text | false |  |
| Inventory_Log__c | Lookup | false | Inventory_Log__c |
| Inventory_Receipt_Item__c | Lookup | false | Inventory_Receipt_Item__c |
| Inventory_Receipt__c | Lookup | false | Inventory_Receipt__c |
| Inventory__c | MasterDetail | false | Inventory__c |
| Invoice_Item__c | Lookup | false | Invoice_Item__c |
| Invoice_Key__c | Text | false |  |
| Invoice__c | Lookup | false | Invoice__c |
| Is_Credit_Return__c | Checkbox | false |  |
| Is_Dirty_Keg__c | Checkbox | false |  |
| Is_Inventory_Log__c | Checkbox | false |  |
| Is_Inventory_Receipt_Item__c | Checkbox | false |  |
| Is_Inventory_Receipt__c | Checkbox | false |  |
| Is_Invoice_Item__c | Checkbox | false |  |
| Is_Invoice__c | Checkbox | false |  |
| Is_Purchase_Order_Item__c | Checkbox | false |  |
| Is_Purchase_Order__c | Checkbox | false |  |
| Is_Synced__c | Checkbox | false |  |
| Is_Transfer__c | Checkbox | false |  |
| Is_Unsold__c | Checkbox | false |  |
| Item_Category__c | Text | false |  |
| Item__c | Text | false |  |
| Journal_Entries_Synced__c | Summary | false |  |
| Journal_Entries__c | Summary | false |  |
| Location_Name__c | Text | false |  |
| Log_Type_Subtype_Key__c | Text | false |  |
| Lot_Inventory__c | Lookup | false | Lot_Inventory__c |
| Lot_Name__c | Text | false |  |
| Lot__c | Lookup | false | Lot__c |
| Packaging_Type__c | Text | false |  |
| Positive_Negative_Key__c | Text | false |  |
| Purchase_Order_Item__c | Lookup | false | Purchase_Order_Item__c |
| Purchase_Order__c | Lookup | false | Purchase_Order__c |
| Quantity_Change__c | Number | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| Reason__c | Picklist | false |  |
| Receipt_Key__c | Text | false |  |
| Return_Key__c | Text | false |  |
| Status__c | Picklist | false |  |
| Supplier__c | Text | false |  |
| Total_Quantity_Change_Cases__c | Number | false |  |
| Total_Value__c | Currency | false |  |
| Transfer_Key__c | Text | false |  |
| Transfer__c | Lookup | false | Transfer__c |
| Type__c | Picklist | false |  |
| Unit_Value__c | Currency | false |  |
| Unsold_Reason__c | Text | false |  |

### Inventory_History__c (7 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Inventory_Date__c | Date | false |  |
| Inventory_Value__c | Number | false |  |
| Inventory__c | MasterDetail | false | Inventory__c |
| Item__c | MasterDetail | false | Item__c |
| Quantity_Available__c | Number | false |  |
| Quantity_On_Hand__c | Number | false |  |
| Stamped_Date__c | Date | false |  |

### Inventory_Log_Group__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Is_Approved__c | Checkbox | false |  |
| Is_Cycle_Count__c | Checkbox | false |  |
| Location__c | Lookup | false | Location__c |
| Log_Date__c | Date | false |  |
| Use_Pallets_And_Layers__c | Checkbox | false |  |
| Was_Recounted__c | Checkbox | false |  |

### Inventory_Log__c (19 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Case_Quantity__c | Number | false |  |
| Cost_Variance__c | Currency | false |  |
| Inventory_Log_Group__c | Lookup | false | Inventory_Log_Group__c |
| Inventory__c | MasterDetail | false | Inventory__c |
| Is_Top_Line_Log__c | Checkbox | false |  |
| Item__c | Text | false |  |
| Key__c | Text | false |  |
| Layer_Quantity__c | Number | false |  |
| Location__c | Lookup | false | Location__c |
| Log_Date__c | Date | false |  |
| Lot_Inventory__c | Lookup | false | Lot_Inventory__c |
| Notes__c | Text | false |  |
| Pallet_Quantity__c | Number | false |  |
| Quantity_Adjustment_Units__c | Number | false |  |
| Reason__c | Picklist | false |  |
| Status__c | Picklist | false |  |
| UOM__c | Text | false |  |
| Unit_Quantity__c | Number | false |  |
| Was_Recounted__c | Checkbox | false |  |

### Inventory_Receipt_Fee__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Allocation_Method__c | Picklist | false |  |
| Amount__c | Currency | false |  |
| Cost_Type__c | Picklist | false |  |
| Description__c | Text | false |  |
| Fee_Name__c | Text | false |  |
| Fee__c | MasterDetail | false | Fee__c |
| Inventory_Receipt__c | MasterDetail | false | Inventory_Receipt__c |
| Quantity__c | Number | false |  |
| Total__c | Currency | false |  |

### Inventory_Receipt_Item__c (28 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Variance_ID__c | Text | false |  |
| Apex_Class_Name__c | Text | false |  |
| Case_Cost_Variance__c | Currency | false |  |
| Case_Equivalents__c | Number | false |  |
| Case_Price__c | Currency | false |  |
| Case_Quantity__c | Number | false |  |
| Fee_Amount__c | Currency | false |  |
| Inventory_Receipt_Item__c | Lookup | false | Inventory_Receipt_Item__c |
| Inventory_Receipt__c | MasterDetail | false | Inventory_Receipt__c |
| Item_Name__c | Text | false |  |
| Item_Quantity_On_Hand__c | Number | false |  |
| Item_SKU__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Landed_Case_Cost__c | Currency | false |  |
| Last_Landed_Cost__c | Currency | false |  |
| Lot__c | Text | false |  |
| Packaging_Type__c | Text | false |  |
| Previous_Landed_Cost__c | Currency | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| QuickBooks_Holding_ID__c | Text | false |  |
| QuickBooks_Item_ID_Company_2__c | Text | false |  |
| Quickbooks_Item_ID__c | Text | false |  |
| Sales_Tax_Per_Case__c | Currency | false |  |
| Sales_Tax_Rate__c | Percent | false |  |
| Sales_Tax__c | Currency | false |  |
| Sort_Order__c | Number | false |  |
| Subtotal__c | Currency | false |  |
| Total__c | Currency | false |  |

### Inventory_Receipt__c (16 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Apex_Class_Name__c | Text | false |  |
| Bill_Due_Date__c | Date | false |  |
| Case_Quantity_Received__c | Summary | false |  |
| Has_Integration_Sync__c | Checkbox | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Inventory_Receipt_Date__c | Date | false |  |
| Invoice_Number__c | Text | false |  |
| Payment_Status__c | Picklist | false |  |
| Purchase_Order__c | MasterDetail | false | Purchase_Order__c |
| Sales_Tax__c | Summary | false |  |
| Status__c | Picklist | false |  |
| Subtotal__c | Summary | false |  |
| Supplier__c | Lookup | false | Account |
| Total_Case_Cost__c | Summary | false |  |
| Total_Due__c | Currency | false |  |
| Total_Fees__c | Summary | false |  |

### Inventory__c (46 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Cases_Available__c | Number | false |  |
| Cases_On_Hand__c | Number | false |  |
| Counter_Difference__c | Number | false |  |
| Credit_Returns_Complete__c | Summary | false |  |
| Inventory_Receipt_Complete__c | Summary | false |  |
| Inventory_Receipt_In_Progress__c | Summary | false |  |
| Inventory_Value_Lot_Tracked__c | Currency | false |  |
| Inventory_Value__c | Currency | false |  |
| Invoice_Complete__c | Summary | false |  |
| Invoice_In_Progress__c | Summary | false |  |
| Invoice_Picked__c | Summary | false |  |
| Invoice_Unsold__c | Summary | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Default_Inventory__c | Checkbox | false |  |
| Is_Force_Update__c | Checkbox | false |  |
| Is_Lot_Tracked__c | Checkbox | false |  |
| Is_Offline_Resellable__c | Checkbox | false |  |
| Item_Classification__c | Text | false |  |
| Item_Name__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Layer_Quantity__c | Number | false |  |
| Location_Name__c | Text | false |  |
| Location__c | Lookup | false | Location__c |
| Lot_Quantity_On_Hand__c | Summary | false |  |
| Offline_Sellable_Quantity__c | Number | false |  |
| Packaging_Type__c | Text | false |  |
| Pallet_Quantity__c | Number | false |  |
| Parent_Location__c | Text | false |  |
| Purchase_Order_In_Progress__c | Summary | false |  |
| Quantity_Available__c | Number | false |  |
| Quantity_Dev__c | Number | false |  |
| Quantity_Incoming__c | Number | false |  |
| Quantity_On_Hand__c | Number | false |  |
| Reason__c | Picklist | false |  |
| Total_Available_Cases__c | Number | false |  |
| Total_Dirty_Kegs__c | Summary | false |  |
| Total_Inventory_Logs__c | Summary | false |  |
| Total_On_Hand__c | Number | false |  |
| Transfer_Complete__c | Summary | false |  |
| Transfer_In_Progress__c | Summary | false |  |
| Type__c | Text | false |  |
| Units_Available__c | Number | false |  |
| Units_On_Hand__c | Number | false |  |
| Units_Per_Case__c | Number | false |  |
| Warehouse__c | Text | false |  |
| Was_Created_Offline__c | Checkbox | false |  |

### Invoice_Adjustment__c (5 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Adjustment__c | MasterDetail | false | Adjustment__c |
| Case_Price__c | Currency | false |  |
| Case_Quantity__c | Number | false |  |
| Invoice__c | MasterDetail | false | Invoice__c |
| Total__c | Currency | false |  |

### Invoice_Fee__c (11 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_System_ID__c | Text | false |  |
| Allocation_Method__c | Picklist | false |  |
| Amount__c | Currency | false |  |
| Cost_Type__c | Picklist | false |  |
| Description__c | Text | false |  |
| Fee_Name__c | Text | false |  |
| Fee__c | MasterDetail | false | Fee__c |
| Invoice__c | MasterDetail | false | Invoice__c |
| Is_Transaction_Fee__c | Checkbox | false |  |
| Quantity__c | Number | false |  |
| Total__c | Currency | false |  |

### Invoice_Goal__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Goal__c | MasterDetail | false | Goal__c |
| Invoice__c | MasterDetail | false | Invoice__c |

### Invoice_Group__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer__c | Lookup | true | Account |
| Total_Cases__c | Number | false |  |
| Total__c | Currency | false |  |

### Invoice_Item__c (79 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Adjustment__c | Currency | false |  |
| Adjustments_Applied__c | LongTextArea | false |  |
| Average_Landed_Case_Cost__c | Currency | false |  |
| Average_Landed_Unit_Cost__c | Currency | false |  |
| Backorder_Case_Quantity__c | Number | false |  |
| Backorder_Quantity_Total_Cases__c | Number | false |  |
| Backorder_Unit_Quantity__c | Number | false |  |
| Barrels__c | Number | false |  |
| Case_Equivalents__c | Number | false |  |
| Case_Price__c | Currency | false |  |
| Case_Quantity__c | Number | false |  |
| Customer_Name__c | Text | false |  |
| Delivery_Sorting__c | Text | false |  |
| Delivery__c | Lookup | false | Delivery__c |
| Difference_Case_Quantity__c | Number | false |  |
| Discounted_Case_Price__c | Currency | false |  |
| External_ID__c | Text | false |  |
| External_Item_ID__c | Text | false |  |
| External_Order_ID__c | Text | false |  |
| Invoice_Date__c | Date | false |  |
| Invoice_Item_Number__c | AutoNumber | false |  |
| Invoice_Item__c | Lookup | false | Invoice_Item__c |
| Invoice__c | MasterDetail | false | Invoice__c |
| Invoiced_Case_Quantity__c | Number | false |  |
| Invoiced_Unit_Quantity__c | Number | false |  |
| Is_Fully_Backordered__c | Checkbox | false |  |
| Is_Imperfect_Invoice__c | Checkbox | false |  |
| Is_Keg_Deposit__c | Checkbox | false |  |
| Is_New__c | Checkbox | false |  |
| Is_Offline_Add_To_Truck__c | Checkbox | false |  |
| Is_Offline_Sell_From_Truck__c | Checkbox | false |  |
| Item_Case_UPC__c | Text | false |  |
| Item_Description__c | Text | false |  |
| Item_Keg_Deposit__c | Currency | false |  |
| Item_Name__c | Text | false |  |
| Item_Number__c | Text | false |  |
| Item_SKU__c | Text | false |  |
| Item_Short_Name__c | Text | false |  |
| Item_Type_Name__c | Text | false |  |
| Item__c | MasterDetail | false | Item__c |
| Keg_Deposit_Amount__c | Currency | false |  |
| Loaded_Case_Quantity__c | Number | false |  |
| Loaded_Quantity_Total_Cases__c | Number | false |  |
| Loaded_Unit_Quantity__c | Number | false |  |
| Offline_Lot_Inventory_Id__c | Text | false |  |
| Offline_Lot_Name__c | Text | false |  |
| Offline_Mispick_Truck_Qty__c | Number | false |  |
| Offline_Mispick__c | Text | false |  |
| Offline_Remove_Lot_Quantity__c | Text | false |  |
| Ordered_Case_Quantity__c | Number | false |  |
| Ordered_Unit_Quantity__c | Number | false |  |
| Original_Order_Case_Quantity__c | Number | false |  |
| Original_Order_Unit_Quantity__c | Number | false |  |
| Outstanding_Case_Quantity__c | Number | false |  |
| Outstanding_Unit_Quantity__c | Number | false |  |
| Packaging_Type__c | Text | false |  |
| Picked_Case_Quantity__c | Number | false |  |
| Picked_Quantity_Total_Cases__c | Number | false |  |
| Picked_Unit_Quantity__c | Number | false |  |
| QuickBooks_Item_ID_Company_2__c | Text | false |  |
| QuickBooks_Item_ID__c | Text | false |  |
| Retail_Case_Quantity__c | Number | false |  |
| Sales_Tax_Rate__c | Percent | false |  |
| Sales_Tax__c | Currency | false |  |
| Sort_Order__c | Number | false |  |
| Subtotal__c | Currency | false |  |
| Total_Case_Equivalents__c | Number | false |  |
| Total_Discount_Dollars__c | Currency | false |  |
| Total_Discount_Percent__c | Percent | false |  |
| Total_Invoice_Weight__c | Number | false |  |
| Total_Order_Weight__c | Number | false |  |
| Total_Unit_Cost__c | Currency | false |  |
| Total__c | Currency | false |  |
| Type_Of_Item__c | Text | false |  |
| Unit_Price__c | Currency | false |  |
| Unsold_Reason__c | Picklist | false |  |
| Was_Created_Offline__c | Checkbox | false |  |
| Was_Edited_Offline__c | Checkbox | false |  |
| Week__c | Number | false |  |

### Invoice_LWC_Configuration__mdt (4 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Is_Active_Tile__c | Checkbox | false |  |
| Item_Types__c | Text | false |  |
| Tile_Name__c | Text | false |  |
| Tile_Order__c | Number | false |  |

### Invoice__c (96 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABC_License_Number__c | Text | false |  |
| ACH_Payout_Fee__c | Percent | false |  |
| Accounting_System_ID__c | Text | false |  |
| Adjustment__c | Summary | false |  |
| BOL_Tax_Type__c | Picklist | false |  |
| Billing_Contact_Name__c | Text | false |  |
| Billing_Contact__c | Text | false |  |
| Cancelled_Reason__c | Picklist | false |  |
| Cases_Invoiced__c | Summary | false |  |
| Cases_Ordered__c | Summary | false |  |
| Chain_Banner__c | Text | false |  |
| Check_Number__c | Text | false |  |
| Credits_Applied__c | Currency | false |  |
| Customer_Name__c | Text | false |  |
| Customer_Number__c | Text | false |  |
| Customer_PO_Number__c | Text | false |  |
| Customer_Phone_Number__c | Text | false |  |
| Customer__c | MasterDetail | false | Account |
| Date_Completed__c | Date | false |  |
| Day_Of_Week__c | Text | false |  |
| Delivery_Contact_Name__c | Text | false |  |
| Delivery_Contact__c | Text | false |  |
| Delivery_Driver_Name__c | Text | false |  |
| Delivery_Method__c | Picklist | false |  |
| Delivery_Pickup_Date__c | Date | false |  |
| Delivery__c | Lookup | false | Delivery__c |
| External_Distributor_ID__c | Text | false |  |
| External_ID__c | Text | false |  |
| Forms_Mailing_Address_City_State_Zip__c | Text | false |  |
| Forms_Mailing_Address_Street__c | Text | false |  |
| Forms_Physical_Address_City_State_Zip__c | Text | false |  |
| Forms_Physical_Address_Street__c | Text | false |  |
| Fulfillment_Location__c | Lookup | false | Location__c |
| GS1_Prefix__c | Text | false |  |
| Has_Integration_Sync__c | Checkbox | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Invoice_Date_Month__c | Number | false |  |
| Invoice_Date__c | Date | false |  |
| Invoice_Group__c | Lookup | false | Invoice_Group__c |
| Invoice_Name__c | Text | false |  |
| Invoice_Number__c | AutoNumber | false |  |
| Invoice_Revenue__c | Summary | false |  |
| Invoice_Total__c | Currency | false |  |
| Is_Credit_Invoice__c | Checkbox | false |  |
| Is_Dock_Sale__c | Checkbox | false |  |
| Is_EDI_Invoice__c | Checkbox | false |  |
| Is_External_Invoice__c | Checkbox | false |  |
| Is_Locked__c | Checkbox | false |  |
| Is_Off_Day_Invoice__c | Checkbox | false |  |
| Is_Offline_Sell_From_Truck__c | Checkbox | false |  |
| Is_Picked__c | Checkbox | false |  |
| Is_Signed__c | Checkbox | false |  |
| License__c | Text | false |  |
| Mailing_Address__c | Text | false |  |
| Offline_Items__c | LongTextArea | false |  |
| Offline_Sell_From_Truck_Items__c | LongTextArea | false |  |
| PO_Number__c | Text | false |  |
| Payment_Due_Date__c | Date | false |  |
| Payment_Method__c | Picklist | false |  |
| Payment_Partner__c | Picklist | false |  |
| Payment_Status__c | Picklist | false |  |
| Payment_Terms__c | Picklist | false |  |
| Physical_Address_Report__c | Text | false |  |
| Physical_Address__c | Text | false |  |
| Pricelist__c | Lookup | false | Pricelist__c |
| Processing_Fee__c | Currency | false |  |
| QuickBooks_Class_ID__c | Text | false |  |
| Quickbooks_Electronic_Invoice__c | Picklist | false |  |
| Route_Name__c | Text | false |  |
| Sales_Rep_Name__c | Text | false |  |
| Sales_Rep__c | Lookup | false | User |
| Sales_Tax_Rate__c | Percent | false |  |
| Sales_Tax__c | Summary | false |  |
| Should_Charge_Processing_Fee__c | Checkbox | false |  |
| Special_Instructions__c | Text | false |  |
| Status__c | Picklist | false |  |
| Subtotal__c | Summary | false |  |
| Subtypes__c | Text | false |  |
| Total_Case_Equivalents__c | Number | false |  |
| Total_Cases__c | Number | false |  |
| Total_Credits__c | Currency | false |  |
| Total_Due__c | Currency | false |  |
| Total_Fee_Amount__c | Summary | false |  |
| Total_Fees__c | Currency | false |  |
| Total_Invoice_Items__c | Summary | false |  |
| Total_Invoice_Value__c | Currency | false |  |
| Total_Invoice_Weight__c | Summary | false |  |
| Total_Keg_Deposits_Collected__c | Summary | false |  |
| Total_Units__c | Number | false |  |
| Transaction_Fees__c | Summary | false |  |
| Units_Invoiced__c | Summary | false |  |
| Units_Ordered__c | Summary | false |  |
| Was_Created_Offline__c | Checkbox | false |  |
| Was_Edited_Offline__c | Checkbox | false |  |
| Was_Reassigned__c | Checkbox | false |  |
| Was_Returned__c | Checkbox | false |  |

### Item_Component__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Child_Item__c | Lookup | false | Item__c |
| Item_Line__c | Text | false |  |
| Key__c | Text | false |  |
| Packaging_Type__c | Text | false |  |
| Parent_Item__c | MasterDetail | false | Item__c |
| Quantity__c | Number | false |  |

### Item_Group_Rule__c (6 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Customer__c | Lookup | true | Account |
| GS1_Prefix__c | Text | false |  |
| Item_Group__c | Lookup | true | Item_Group__c |
| Payment_Method__c | Picklist | false |  |
| Payment_Partner__c | Picklist | false |  |
| Payment_Terms__c | Picklist | true |  |

### Item_Group__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Split_Criteria__c | MultiselectPicklist | false |  |
| Subtype_Criteria__c | Text | true |  |

### Item_Line__c (3 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Key__c | Text | false |  |
| Supplier__c | Lookup | false | Account |
| Type__c | Picklist | false |  |

### Item_Type_Territory_Exclusion__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Item_Type__c | MasterDetail | false | Item_Type__c |
| Territory__c | MasterDetail | false | Territory__c |

### Item_Type__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| ABV__c | Percent | false |  |
| Category__c | Picklist | false |  |
| Item_Line__c | Lookup | false | Item_Line__c |
| Key__c | Text | false |  |
| Packaging_Styles__c | MultiselectPicklist | false |  |
| Short_Name__c | Text | false |  |
| Subtype__c | Picklist | false |  |
| Supplier_Number__c | Text | false |  |
| Supplier__c | Text | false |  |
| Type__c | Picklist | false |  |

### Item__c (77 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Accounting_Variance_ID__c | Text | false |  |
| Average_Case_Cost__c | Currency | false |  |
| Average_Case_Price__c | Currency | false |  |
| Average_Cost_Counter__c | Number | false |  |
| Average_Cost_Total__c | Currency | false |  |
| Average_Sale_Counter__c | Number | false |  |
| Average_Sale_Total__c | Currency | false |  |
| Can_Credit_In_Units__c | Checkbox | false |  |
| Carrier_UPC__c | Text | false |  |
| Case_GTIN__c | Text | false |  |
| Case_Quantity__c | Number | false |  |
| Case_UPC__c | Text | false |  |
| Cases_Per_Layer__c | Number | false |  |
| Cases_Per_Pack__c | Number | false |  |
| Cases_Per_Pallet__c | Number | false |  |
| Category__c | Text | false |  |
| Credit_Type__c | Text | false |  |
| Default_Case_Price__c | Currency | false |  |
| External_ID__c | Text | false |  |
| FinTech_UOM__c | Picklist | false |  |
| GPA_External_ID__c | Text | false |  |
| Inventory_Value__c | Currency | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Lot_Tracked__c | Checkbox | false |  |
| Is_Sold_In_Units__c | Checkbox | false |  |
| Is_Tax_Exempt__c | Checkbox | false |  |
| Is_Template__c | Checkbox | false |  |
| Item_Line__c | Lookup | false | Item_Line__c |
| Item_Number__c | Text | false |  |
| Item_Purposes__c | MultiselectPicklist | false |  |
| Item_Type_Subtype__c | Text | false |  |
| Item_Type__c | Lookup | false | Item_Type__c |
| Keg_Deposit__c | Currency | false |  |
| Key__c | Text | false |  |
| Last_Case_Price__c | Currency | false |  |
| Last_Invoice_Date__c | Date | false |  |
| Last_Landed_Case_Cost__c | Currency | false |  |
| Last_vs_Average_Cost_Percentage__c | Percent | false |  |
| Last_vs_Average_Cost_Price__c | Currency | false |  |
| Last_vs_Average_Sale_Percentage__c | Percent | false |  |
| Layers_Per_Pallet__c | Number | false |  |
| Logo_URL__c | LongTextArea | false |  |
| Pack_GTIN__c | Text | false |  |
| Package_Type__c | Picklist | false |  |
| Packaging_Type_Short_Name__c | Text | false |  |
| Packaging_Type__c | Picklist | false |  |
| Quantity_Available__c | Summary | false |  |
| Quantity_Incoming__c | Summary | false |  |
| Quantity_On_Hand__c | Summary | false |  |
| QuickBooks_Credit_Memo_ID_Company_2__c | Text | false |  |
| QuickBooks_Credit_Memo_ID__c | Text | false |  |
| QuickBooks_Holding_ID__c | Text | false |  |
| QuickBooks_Item_ID_Company_2__c | Text | false |  |
| QuickBooks_Purchase_ID_Company_2__c | Text | false |  |
| QuickBooks_Purchase_ID__c | Text | false |  |
| QuickBooks_Return_ID_Company_2__c | Text | false |  |
| QuickBooks_Return_ID__c | Text | false |  |
| Quickbooks_Item_ID__c | Text | false |  |
| Retail_Units_Per_Case__c | Number | false |  |
| Retailer_UPC__c | Text | false |  |
| SKU_Number__c | Text | false |  |
| Short_Name__c | Text | false |  |
| State_Item_Code__c | Text | false |  |
| Straight_Average_Case_Cost__c | Currency | false |  |
| Supplier_Name__c | Text | false |  |
| Supplier_Number__c | Text | false |  |
| Supplier__c | Text | false |  |
| Type__c | Picklist | false |  |
| UOM_In_Fluid_Ounces__c | Number | false |  |
| UOM__c | Picklist | false |  |
| UPC__c | Text | false |  |
| Unit_GTIN__c | Text | false |  |
| Unit_UPC__c | Text | false |  |
| Units_Per_Case__c | Number | false |  |
| VIP_External_ID__c | Text | false |  |
| Weight_UOM__c | Picklist | false |  |
| Weight__c | Number | false |  |

### Journal_Entry__c (35 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Account_Billing_City__c | Text | false |  |
| Account_Billing_Postal_Code__c | Text | false |  |
| Account_Billing_State__c | Text | false |  |
| Account_Billing_Street__c | Text | false |  |
| Account_Phone__c | Text | false |  |
| Account_Quickbooks_Customer_ID__c | Text | false |  |
| Accounting_System_ID__c | Text | false |  |
| Category__c | Picklist | false |  |
| Entry_Type__c | Picklist | false |  |
| Financial_Account__c | Lookup | false | Financial_Account__c |
| Has_Integration_Sync__c | Checkbox | false |  |
| ID_Account__c | Text | false |  |
| ID_Invoice_Credit__c | Text | false |  |
| ID_Invoice_Item__c | Text | false |  |
| ID_Invoice__c | Text | false |  |
| ID_Item__c | Text | false |  |
| ID_Item_del__c | Text | false |  |
| Integration_Sync_Date__c | DateTime | false |  |
| Inventory_Adjustment__c | MasterDetail | false | Inventory_Adjustment__c |
| Item_Name__c | Text | false |  |
| Item_Quantity__c | Number | false |  |
| Item_QuickBooks_Credit_Memo_ID__c | Text | false |  |
| Item_QuickBooks_ID__c | Text | false |  |
| Item_Subtotal__c | Currency | false |  |
| N_Account_del__c | Text | false |  |
| N_Inventory_Adjustment__c | Text | false |  |
| N_Invoice_Credit__c | Text | false |  |
| N_Invoice_Item__c | Text | false |  |
| N_Invoice__c | Text | false |  |
| N_Item_del__c | Text | false |  |
| Quantity__c | Number | false |  |
| QuickBooks_Adjustment_Type__c | Text | false |  |
| QuickBooks_Customer_ID_del__c | Text | false |  |
| Type__c | Picklist | false |  |
| Value__c | Currency | false |  |

### Location__c (27 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Company__c | Picklist | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Dirty_Keg_Location__c | Checkbox | false |  |
| Is_Finished_Good__c | Checkbox | false |  |
| Is_Keg_Shell__c | Checkbox | false |  |
| Is_Merchandise__c | Checkbox | false |  |
| Is_Sellable__c | Checkbox | false |  |
| Is_Shelf_Tag_Enabled__c | Checkbox | false |  |
| Is_Tap_Handle__c | Checkbox | false |  |
| Is_Truck__c | Checkbox | false |  |
| Key__c | Text | false |  |
| Location_City__c | Text | false |  |
| Location_Code__c | Text | false |  |
| Location_County__c | Text | false |  |
| Location_Hierarchy_Dev__c | Text | false |  |
| Location_Hierarchy__c | Text | false |  |
| Location_Number__c | Text | false |  |
| Location_Postal_Code__c | Text | false |  |
| Location_State__c | Text | false |  |
| Location_Street__c | Text | false |  |
| Notes__c | LongTextArea | false |  |
| Parent_Location__c | Lookup | false | Location__c |
| QuickBooks_Class_ID__c | Text | false |  |
| QuickBooks_Parent_Class_ID__c | Text | false |  |
| Type__c | Picklist | false |  |
| Warehouse_Location_Id__c | Text | false |  |
| Warehouse__c | Text | false |  |

### Lot_Inventory_Receipt_Item__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Inventory_Receipt_Item__c | Lookup | true | Inventory_Receipt_Item__c |
| Lot__c | Lookup | true | Lot__c |

### Lot_Inventory__c (10 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Cases_On_Hand__c | Number | false |  |
| Expiration_Date__c | Date | false |  |
| Inventory_Location__c | Text | false |  |
| Inventory_Value__c | Currency | false |  |
| Inventory__c | MasterDetail | false | Inventory__c |
| Lot__c | MasterDetail | false | Lot__c |
| Quantity_On_Hand__c | Number | false |  |
| Receipt_Date__c | Date | false |  |
| Total_On_Hand__c | Number | false |  |
| Units_On_Hand__c | Number | false |  |

### Lot_Invoice_Item__c (2 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Invoice_Item__c | Lookup | true | Invoice_Item__c |
| Lot__c | Lookup | true | Lot__c |

### Lot__c (13 fields)

| Field | Type | Required | Reference |
|-------|------|----------|-----------|
| Cases_On_Hand__c | Number | false |  |
| Cost_Per_Unit__c | Currency | false |  |
| Expiration_Date__c | Date | false |  |
| Inventory_Value__c | Currency | false |  |
| Is_Active__c | Checkbox | false |  |
| Is_Sellable__c | Checkbox | false |  |
| Item__c | Lookup | false | Item__c |
| Lot_Identifier__c | Text | false |  |
| Quantity_On_Hand__c | Summary | false |  |
| Receipt_Date__c | Date | false |  |
| Supplier__c | Lookup | false | Account |
| Total_On_Hand__c | Number | false |  |
| Units_On_Hand__c | Number | false |  |

## Common Patterns

| Pattern | Files Using It | Notes |
|---------|---------------|-------|
| Trigger Bypass | 0 | Classes referencing bypass mechanisms |
| Service Locator | 0 | Classes using service locator pattern |
| Batch/Schedulable | 0 | Classes implementing batch or schedulable |
| Queueable | 0 | Classes using async queueable jobs |
| Platform Events | 0 | Classes publishing or subscribing to events |

## Test Coverage Summary

| Metric | Count |
|--------|-------|
| Production classes | 0 |
| Test/Mock/Stub classes | 0 |
| Test-to-production ratio | N/A |

## Known Gotchas

_No known gotchas recorded yet. This section is populated by operational learnings from debugging sessions._

