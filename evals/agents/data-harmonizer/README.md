# Evals: data-harmonizer

Eval suite for the Excel-to-Salesforce data harmonizer.

## Fixtures

Eval fixtures are **anonymized** copies of real customer Excel files.
Customer names, SKUs, and pricing are replaced with synthetic values
before committing to the repo. Original files remain off-repo per
the "no customer PII in logs" security rule.

## Eval Cases

Each eval case defines:
- An input Excel file (synthetic)
- Expected column mappings (ground truth from manual mapping)
- Expected validation issues (known data quality problems)

## Scoring

Scored by Claude Haiku against a rubric:
- Mapping accuracy: % of columns correctly mapped
- Confidence calibration: high-confidence mappings should be correct >95%
- Unmapped detection: columns marked unmapped should genuinely be unmappable

## Targets

- Mapping accuracy: >=85% (hard fail: <75%)
- False high-confidence rate: <5%
- Zero missed required-field validations
