"""
Tests for data-harmonizer skill.

Unit tests only — no external API calls. Claude and DynamoDB are mocked.
Integration tests (against real Claude + SF scratch org) run in CI on PR.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the skill directory to sys.path so imports work with hyphenated dir names
_skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_skill_dir))

from schema import (
    Confidence,
    ColumnMapping,
    InputSchema,
    MappingResult,
    StagedRecord,
)
from skill import (
    read_file,
    sample_rows,
    validate_records,
    check_duplicates,
    format_sf_schema,
)

FIXTURES_DIR = Path(__file__).parent.parent.parent.parent.parent / "evals" / "agents" / "data-harmonizer" / "fixtures"


# --- File reading ---


class TestReadFile:
    def test_read_csv_basic(self):
        headers, rows = read_file(str(FIXTURES_DIR / "basic_accounts.csv"), None, 1)
        assert "Store Name" in headers
        assert "City" in headers
        assert len(rows) == 5
        assert rows[0]["Store Name"] == "Sunset Liquors"

    def test_read_csv_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            read_file("test.pdf", None, 1)

    def test_read_csv_depletions(self):
        headers, rows = read_file(str(FIXTURES_DIR / "depletions_nonstandard.csv"), None, 1)
        assert "Cases Sold" in headers
        assert "House" in headers
        assert len(rows) == 5


# --- Sampling ---


class TestSampling:
    def test_small_file_returns_all(self):
        rows = [{"a": i} for i in range(10)]
        result = sample_rows(rows)
        assert len(result) == 10

    def test_large_file_samples(self):
        rows = [{"a": i} for i in range(100)]
        result = sample_rows(rows, max_samples=20)
        assert len(result) == 20
        # First 10 should be from the beginning
        for i in range(10):
            assert result[i]["a"] == i


# --- Validation ---


class TestValidation:
    def _make_mapping(self, col_map: dict) -> MappingResult:
        mappings = []
        for source, (obj, field) in col_map.items():
            mappings.append(
                ColumnMapping(
                    source_column=source,
                    target_object=obj,
                    target_field=field,
                    confidence=Confidence.HIGH,
                    rationale="test",
                )
            )
        return MappingResult(mappings=mappings)

    def test_valid_records(self):
        mapping = self._make_mapping({
            "Store Name": ("Account", "Name"),
            "City": ("Account", "BillingCity"),
        })
        rows = [
            {"Store Name": "Test Store", "City": "Austin"},
            {"Store Name": "Other Store", "City": "Dallas"},
        ]
        staged, issues = validate_records(rows, mapping)
        assert len(staged) == 2
        assert len([i for i in issues if i.severity == "error"]) == 0

    def test_missing_required_field(self):
        mapping = self._make_mapping({
            "City": ("Account", "BillingCity"),
        })
        rows = [{"City": "Austin"}]  # Missing Name, which is required for Account
        staged, issues = validate_records(rows, mapping)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) >= 1
        assert any("Name" in i.issue for i in errors)


# --- Duplicate Detection ---


class TestDuplicateDetection:
    def test_finds_duplicates(self):
        from schema import StagedRecord

        staged = [
            StagedRecord(source_row=2, target_object="Account", fields={"Name": "Sunset Liquors"}, original_values={}),
            StagedRecord(source_row=3, target_object="Account", fields={"Name": "Central Market"}, original_values={}),
            StagedRecord(source_row=4, target_object="Account", fields={"Name": "Sunset Liquors"}, original_values={}),
        ]
        issues = check_duplicates(staged)
        assert len(issues) == 1
        assert "Sunset Liquors" in issues[0].issue

    def test_no_false_positives(self):
        from schema import StagedRecord

        staged = [
            StagedRecord(source_row=2, target_object="Account", fields={"Name": "Store A"}, original_values={}),
            StagedRecord(source_row=3, target_object="Account", fields={"Name": "Store B"}, original_values={}),
        ]
        issues = check_duplicates(staged)
        assert len(issues) == 0


# --- Schema Formatting ---


class TestSchemaFormatting:
    def test_format_includes_all_objects(self):
        schema_text = format_sf_schema()
        assert "Account" in schema_text
        assert "Contact" in schema_text
        assert "Product2" in schema_text
        assert "Distributor__c" in schema_text
        assert "Brand__c" in schema_text
        assert "Depletion__c" in schema_text

    def test_format_includes_required_markers(self):
        schema_text = format_sf_schema()
        assert "(REQUIRED)" in schema_text
