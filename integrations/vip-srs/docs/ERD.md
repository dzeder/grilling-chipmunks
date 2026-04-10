# VIP/Encompass Data - Entity Relationship Diagram

```mermaid
erDiagram
    DISTDA {
        string DistributorID PK "e.g. FL01, MA02"
        string SupplierID "e.g. ARG"
        string DistributorName
        string Street
        string City
        string State
        string Zip
        string Phone
        string Contact1Name
        string Contact1Email
        string ParentId FK "self-ref"
        string DistributorRep
        string ISVName "VIP, ENCOMPASS, EOSTAR"
        string DistributorRank
        string CertificationStatus
        string Phase
        string LastAuditMonthEOM
        string LastAuditUser
        string DivisionCode
        string AreaCode
        string MarketCode
        string RepCode
    }

    ITM2DA {
        string SupplierItem PK "e.g. 102312102"
        string SupplierId "e.g. ARG"
        string Desc "e.g. Original Vodka 6/1L"
        string CaseGTIN
        string RetailGTIN
        int ActivationDate
        int DeactivationDate
        int Units
        int SellingUnits
        decimal AlcoholPct
        string BrandCode
        string BrandDesc
        string PackageType "BTL"
        string PackageSize "SNGL 750ML"
        string Status "A/I"
        string ContainerType FK "SRSVALUE ITCTYP"
        string GenericCat3 "Vodka, Flavored Vodka"
        decimal ExtMLpCase
        decimal VolofUnit
        string VolUOM "ML, OZ, LTR"
        string CatgDesc7
        string CatgDesc8
    }

    ITMDA {
        string Distributor FK "FK to DISTDA"
        string SupplierItem FK "FK to ITM2DA"
        string DistItem "Dist internal SKU"
        string Description
        string GTIN
        string Status "A/I"
        int Unit
        int CreationDate
        string DistItemSize
        decimal Proof
        string Repack FK "SRSVALUE RSREPACK"
    }

    CTLDA {
        string DistId FK "FK to DISTDA"
        string SupplierItem FK "FK to ITM2DA"
        string DistName
        int Quantity
        string UnitOfMeasure FK "SRSVALUE INUOM"
        string ControlDate "YYYYMM"
    }

    INVDA {
        string DistId FK "FK to DISTDA"
        string SupplierItem FK "FK to ITM2DA"
        string DistItem FK "FK to ITMDA"
        int PostingDate
        int TransCode FK "SRSVALUE INTRANS"
        int TransDate
        int Quantity
        string UnitOfMeasure FK "SRSVALUE INUOM"
        string PurchaseOrder
        string TransDistName
        int FromDate
        int ToDate
        string Repack FK "SRSVALUE RSREPACK"
    }

    OUTDA {
        string DistId FK "FK to DISTDA"
        string Account PK "unique within DistId"
        string DBA
        string LicName
        string Addr1
        string City
        string State
        string Zip9
        string Phone
        string Chain FK "FK to SRSCHAIN"
        string Chain2 FK "FK to SRSCHAIN"
        string ClassOfTrade FK "SRSVALUE ROCOT"
        string ChainStatus FK "SRSVALUE ROCSTS"
        string IndustryVolume FK "SRSVALUE ROIVOL"
        string Status FK "SRSVALUE ROSTS"
        string Salesman1
        string Buyer
        string LicenseType FK "SRSVALUE ROLICTYPE"
        string WhseDist
        string License
    }

    SLSDA {
        string DistId FK "FK to DISTDA"
        string AcctNbr FK "FK to OUTDA"
        string SuppItem FK "FK to ITM2DA"
        string DistItem FK "FK to ITMDA"
        int InvoiceDate
        string InvoiceNbr
        int Qty
        string UOM FK "SRSVALUE RSUOM"
        decimal Front "list price"
        decimal NetPrice "after discounts"
        decimal NetPrice4
        decimal Deposit
        decimal LocalTax
        decimal AdtlChrg
        string SlsRepId
        string Repack FK "SRSVALUE RSREPACK"
        string WhseId
        int FromDate
        int ToDate
    }

    SRSCHAIN {
        string Chain PK "10-digit zero-padded"
        string Desc "Chain name"
    }

    SRSVALUE {
        string FieldName PK "e.g. INTRANS, ROCOT"
        string FieldDesc "e.g. Inventory Tran Code"
        string Value PK "coded value"
        string ValueDesc "human-readable label"
    }

    DISTDA ||--o{ ITMDA : "has items via"
    ITM2DA ||--o{ ITMDA : "mapped to distributors via"
    DISTDA ||--o{ CTLDA : "has allocations"
    ITM2DA ||--o{ CTLDA : "allocated to distributors"
    DISTDA ||--o{ INVDA : "has inventory at"
    ITM2DA ||--o{ INVDA : "tracked in inventory"
    ITMDA  ||--o{ INVDA : "dist item ref"
    DISTDA ||--o{ OUTDA : "services outlets"
    DISTDA ||--o{ SLSDA : "sells through"
    OUTDA  ||--o{ SLSDA : "purchased by"
    ITM2DA ||--o{ SLSDA : "sold as"
    ITMDA  ||--o{ SLSDA : "dist item ref"
    SRSCHAIN ||--o{ OUTDA : "groups outlets"
    SRSVALUE ||--o{ INVDA : "decodes trans codes"
    SRSVALUE ||--o{ OUTDA : "decodes demographics"
    SRSVALUE ||--o{ SLSDA : "decodes UOM/repack"
    SRSVALUE ||--o{ ITM2DA : "decodes container type"
```

## Relationship Summary

| From | To | Join Key | Cardinality | Purpose |
|------|----|----------|-------------|---------|
| DISTDA | ITMDA | DistributorID = Distributor | 1:many | Which items a distributor carries |
| ITM2DA | ITMDA | SupplierItem = SupplierItem | 1:many | How each distributor maps an item |
| DISTDA | CTLDA | DistributorID = DistId | 1:many | Monthly allocations per distributor |
| ITM2DA | CTLDA | SupplierItem = SupplierItem | 1:many | Which items are allocated |
| DISTDA | INVDA | DistributorID = DistId | 1:many | Inventory at each distributor |
| ITM2DA | INVDA | SupplierItem = SupplierItem | 1:many | Which items have inventory records |
| ITMDA | INVDA | DistItem = DistItem | 1:many | Distributor SKU on inventory rows |
| DISTDA | OUTDA | DistributorID = DistId | 1:many | Outlets serviced by distributor |
| DISTDA | SLSDA | DistributorID = DistId | 1:many | Sales from each distributor |
| OUTDA | SLSDA | Account = AcctNbr | 1:many | Sales to each outlet |
| ITM2DA | SLSDA | SupplierItem = SuppItem | 1:many | Which items were sold |
| ITMDA | SLSDA | DistItem = DistItem | 1:many | Distributor SKU on sales rows |
| SRSCHAIN | OUTDA | Chain = Chain | 1:many | Chain grouping for outlets |
| SRSVALUE | multiple | FieldName + Value | 1:many | Code lookups across all files |
