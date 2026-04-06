"""Scorer for the data-harmonizer skill.

Evaluates Excel-to-Salesforce column mapping quality with 5 hard checks:
1. mapping_accuracy — correct target_object + target_field per column
2. confidence_calibration — high-confidence mappings are actually correct
3. unmapped_detection — expected unmapped columns flagged correctly
4. validation_completeness — validation issues (dupes, etc.) detected
5. no_false_high_confidence — unmapped columns not mapped with high confidence
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}


class DataHarmonizerScorer(BaseScorer):
    """Scorer for data-harmonizer eval cases."""

    agent_name = "data_harmonizer"

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        expected_mappings = case.get("expected_mappings", {})
        expected_unmapped = case.get("expected_unmapped", [])
        expected_validation = case.get("expected_validation_issues", {})

        output_mappings = output.get("mappings", [])
        output_unmapped = output.get("unmapped_columns", [])
        output_validations = output.get("validation_issues", [])

        # Build lookup: source_column -> output mapping dict
        output_by_column = {}
        for m in output_mappings:
            col = m.get("source_column", "")
            output_by_column[col] = m

        # --- Check 1: mapping_accuracy ---
        correct = 0
        total = len(expected_mappings)
        mapping_details = []
        for col, expected in expected_mappings.items():
            actual = output_by_column.get(col)
            if actual is None:
                mapping_details.append(f"{col}: not found in output")
                continue
            obj_match = actual.get("target_object") == expected["target_object"]
            field_match = actual.get("target_field") == expected["target_field"]
            if obj_match and field_match:
                correct += 1
            else:
                actual_target = f"{actual.get('target_object')}.{actual.get('target_field')}"
                expected_target = f"{expected['target_object']}.{expected['target_field']}"
                mapping_details.append(f"{col}: expected {expected_target}, got {actual_target}")

        accuracy = correct / total if total > 0 else 1.0
        checks.append(CheckResult(
            name="mapping_accuracy",
            passed=accuracy >= 0.75,
            score=accuracy,
            max_score=1.0,
            details=f"{correct}/{total} mappings correct"
            + (f" — {'; '.join(mapping_details)}" if mapping_details else ""),
        ))

        # --- Check 2: confidence_calibration ---
        calibrated = 0
        checked = 0
        cal_details = []
        for col, expected in expected_mappings.items():
            min_conf = expected.get("min_confidence")
            if not min_conf:
                continue
            actual = output_by_column.get(col)
            if actual is None:
                continue
            checked += 1
            actual_conf = actual.get("confidence", "low")
            if CONFIDENCE_ORDER.get(actual_conf, 0) >= CONFIDENCE_ORDER.get(min_conf, 0):
                calibrated += 1
            else:
                cal_details.append(f"{col}: expected >={min_conf}, got {actual_conf}")

        cal_score = calibrated / checked if checked > 0 else 1.0
        checks.append(CheckResult(
            name="confidence_calibration",
            passed=cal_score >= 0.75,
            score=cal_score,
            max_score=1.0,
            details=f"{calibrated}/{checked} confidence levels met"
            + (f" — {'; '.join(cal_details)}" if cal_details else ""),
        ))

        # --- Check 3: unmapped_detection ---
        if expected_unmapped:
            detected = sum(1 for col in expected_unmapped if col in output_unmapped)
            detect_score = detected / len(expected_unmapped)
            missing = [col for col in expected_unmapped if col not in output_unmapped]
            checks.append(CheckResult(
                name="unmapped_detection",
                passed=detect_score >= 0.75,
                score=detect_score,
                max_score=1.0,
                details=f"{detected}/{len(expected_unmapped)} unmapped columns detected"
                + (f" — missing: {', '.join(missing)}" if missing else ""),
            ))
        else:
            checks.append(CheckResult(
                name="unmapped_detection",
                passed=True,
                score=1.0,
                max_score=1.0,
                details="No unmapped columns expected (0/0)",
            ))

        # --- Check 4: validation_completeness ---
        if expected_validation:
            val_passed = True
            val_details = []
            min_dupes = expected_validation.get("min_duplicate_warnings", 0)
            if min_dupes > 0:
                actual_dupes = sum(
                    1 for v in output_validations if v.get("type") == "duplicate"
                )
                if actual_dupes < min_dupes:
                    val_passed = False
                    val_details.append(
                        f"duplicates: expected >={min_dupes}, got {actual_dupes}"
                    )
                else:
                    val_details.append(f"duplicates: {actual_dupes} (>={min_dupes} required)")

            checks.append(CheckResult(
                name="validation_completeness",
                passed=val_passed,
                score=1.0 if val_passed else 0.0,
                max_score=1.0,
                details="; ".join(val_details) if val_details else "No validation checks required",
            ))

        # --- Check 5: no_false_high_confidence ---
        false_highs = []
        for col in expected_unmapped:
            actual = output_by_column.get(col)
            if actual and actual.get("confidence") == "high":
                false_highs.append(col)

        no_false = len(false_highs) == 0
        checks.append(CheckResult(
            name="no_false_high_confidence",
            passed=no_false,
            score=1.0 if no_false else 0.0,
            max_score=1.0,
            details="No false high-confidence mappings"
            if no_false
            else f"False high-confidence on: {', '.join(false_highs)}",
        ))

        return checks
