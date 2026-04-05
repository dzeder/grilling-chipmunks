"""
Schema definitions for data-harmonizer skill.

Defines the SF target schema, input/output types, and mapping structures.
Customer Excel data maps to these Pydantic models before writing to Salesforce.
"""

from enum import Enum
from pydantic import BaseModel, Field


# --- Confidence scoring ---


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ColumnMapping(BaseModel):
    """A single column mapping from source Excel to SF field."""

    source_column: str = Field(..., description="Column header from the Excel file")
    target_object: str = Field(..., description="SF object API name (e.g. Account, Product2)")
    target_field: str = Field(..., description="SF field API name (e.g. Name, Volume__c)")
    confidence: Confidence = Field(..., description="Mapping confidence: high/medium/low")
    rationale: str = Field(..., description="Why this mapping was chosen")
    transform: str | None = Field(None, description="Optional transform (e.g. 'uppercase', 'date:MM/DD/YYYY')")


class MappingResult(BaseModel):
    """Full mapping result for an Excel file."""

    mappings: list[ColumnMapping] = Field(default_factory=list)
    unmapped_columns: list[str] = Field(default_factory=list, description="Columns that could not be mapped")
    source_row_count: int = Field(0, description="Total rows in the source file")
    sample_rows_analyzed: int = Field(0, description="Rows sent to Claude for analysis")


# --- SF Target Schema (stub — finalize in discovery sprint) ---


class AccountRecord(BaseModel):
    """Account (Retailer) — NOT the distributor."""

    Name: str = Field(..., description="Retailer name")
    Type: str | None = Field(None, description="Chain or Independent")
    BillingCity: str | None = Field(None)
    BillingState: str | None = Field(None)
    BillingPostalCode: str | None = Field(None)
    Phone: str | None = Field(None)
    Website: str | None = Field(None)


class ContactRecord(BaseModel):
    """Contact at retailer or distributor."""

    FirstName: str | None = Field(None)
    LastName: str = Field(..., description="Required by SF")
    Email: str | None = Field(None)
    Phone: str | None = Field(None)
    Title: str | None = Field(None)
    AccountId: str | None = Field(None, description="FK to Account")


class Product2Record(BaseModel):
    """Product (SKU)."""

    Name: str = Field(..., description="Product name")
    ProductCode: str | None = Field(None, description="SKU code")
    Family: str | None = Field(None, description="Product family/category")
    IsActive: bool = Field(True)
    Description: str | None = Field(None)
    # Brand__c relationship populated via Brand__c lookup
    Brand__c: str | None = Field(None, description="FK to Brand__c")


class DistributorRecord(BaseModel):
    """Distributor__c — distributor with territory and brand authorizations."""

    Name: str = Field(..., description="Distributor name")
    Territory__c: str | None = Field(None, description="Geographic territory")
    # Additional fields TBD in discovery sprint


class BrandRecord(BaseModel):
    """Brand__c — beverage brand, parent of products."""

    Name: str = Field(..., description="Brand name")
    # Additional fields TBD in discovery sprint


class DepletionRecord(BaseModel):
    """Depletion__c — sell-through data."""

    Volume__c: float = Field(..., description="Depletion volume")
    Report_Period__c: str = Field(..., description="Reporting period (date or period string)")
    Brand__c: str | None = Field(None, description="FK to Brand__c")
    Distributor__c: str | None = Field(None, description="FK to Distributor__c")
    Account__c: str | None = Field(None, description="FK to Account")


# --- Required fields per object (validation rules) ---

REQUIRED_FIELDS: dict[str, list[str]] = {
    "Account": ["Name"],
    "Contact": ["LastName"],
    "Product2": ["Name"],
    "Distributor__c": ["Name"],
    "Brand__c": ["Name"],
    "Depletion__c": ["Volume__c", "Report_Period__c"],
}

SF_OBJECTS: dict[str, type[BaseModel]] = {
    "Account": AccountRecord,
    "Contact": ContactRecord,
    "Product2": Product2Record,
    "Distributor__c": DistributorRecord,
    "Brand__c": BrandRecord,
    "Depletion__c": DepletionRecord,
}


# --- Skill input/output ---


class InputSchema(BaseModel):
    """Input parameters for the data-harmonizer skill."""

    file_path: str = Field(..., description="Path to the uploaded Excel/CSV file")
    customer_id: str = Field(..., description="Ohanafy customer identifier for mapping retrieval")
    target_object: str | None = Field(
        None,
        description="Target SF object if known (e.g. 'Account'). If None, auto-detect from columns.",
    )
    sheet_name: str | None = Field(
        None, description="Sheet name for multi-sheet workbooks. Defaults to first sheet."
    )
    header_row: int = Field(1, description="Row number containing column headers (1-indexed)")
    dry_run: bool = Field(False, description="If True, map and validate but do not stage to SF")


class ValidationIssue(BaseModel):
    """A single validation issue found in the data."""

    row: int = Field(..., description="Row number in the source file (1-indexed)")
    column: str = Field(..., description="Column name")
    issue: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="'error' (blocks import) or 'warning' (flag for review)")


class StagedRecord(BaseModel):
    """A record staged for SF import."""

    source_row: int = Field(..., description="Row number in the source file")
    target_object: str = Field(..., description="SF object to write to")
    fields: dict = Field(..., description="Mapped field values")
    original_values: dict = Field(..., description="Original values from the Excel row")


class OutputSchema(BaseModel):
    """Output format for the data-harmonizer skill."""

    status: str = Field(..., description="'success', 'needs_review', or 'error'")
    batch_id: str | None = Field(None, description="Unique batch identifier for rollback")
    mapping: MappingResult | None = Field(None, description="Column mapping results")
    staged_records: list[StagedRecord] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    stats: dict | None = Field(
        None,
        description="Summary stats: total_rows, mapped_rows, error_rows, warning_rows",
    )
    error: dict | None = Field(None, description="Error details on failure")
