"""Scorer for the tray-expert skill.

Evaluates Tray.io expert responses across 3 modes:
- Q&A: answer accuracy, source citation, specificity
- Build: requirements gathering, architecture, best practices
- Review: dimension scoring, risk assessment, issue identification

Hard checks adapt to the mode specified in each eval case.
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


# Best practices items from the Build mode checklist
BUILD_BEST_PRACTICES = [
    "credentials",
    "batch",
    "pagination",
    "watermark",
    "error_handling",
    "alerting",
    "staggered",
    "task_credit",
    "concurrency",
    "data_storage",
]

# Review dimensions from the audit rubric
REVIEW_DIMENSIONS = [
    "authentication_security",
    "data_integrity",
    "workflow_architecture",
    "performance_cost",
    "environment_deployment",
    "salesforce_specific",
]


class TrayExpertScorer(BaseScorer):
    """Scorer for tray-expert eval cases."""

    agent_name = "tray_expert"

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        mode = case.get("input", {}).get("mode", "qa")

        if mode == "qa":
            return self._check_qa(case, output)
        elif mode == "build":
            return self._check_build(case, output)
        elif mode == "review":
            return self._check_review(case, output)
        else:
            return [CheckResult(
                name="valid_mode",
                passed=False,
                score=0.0,
                max_score=1.0,
                details=f"Unknown mode: {mode}",
            )]

    def _check_qa(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        expected = case.get("expected", {})

        # Check 1: answer_present — non-empty answer
        answer = output.get("answer", "")
        has_answer = bool(answer.strip())
        checks.append(CheckResult(
            name="answer_present",
            passed=has_answer,
            score=1.0 if has_answer else 0.0,
            max_score=1.0,
            details="Answer provided" if has_answer else "No answer in output",
        ))

        if not has_answer:
            return checks

        # Check 2: source_cited — references expert guide or docs
        source = output.get("source", "")
        has_source = bool(source.strip())
        checks.append(CheckResult(
            name="source_cited",
            passed=has_source,
            score=1.0 if has_source else 0.0,
            max_score=1.0,
            details=f"Source: {source}" if has_source else "No source citation",
        ))

        # Check 3: key_terms — answer contains expected key terms
        expected_terms = expected.get("key_terms", [])
        if expected_terms:
            answer_lower = answer.lower()
            found = [t for t in expected_terms if t.lower() in answer_lower]
            term_score = len(found) / len(expected_terms)
            missing = [t for t in expected_terms if t.lower() not in answer_lower]
            checks.append(CheckResult(
                name="key_terms",
                passed=term_score >= 0.75,
                score=term_score,
                max_score=1.0,
                details=f"{len(found)}/{len(expected_terms)} key terms found"
                + (f" — missing: {', '.join(missing)}" if missing else ""),
            ))

        # Check 4: specificity — answer includes concrete values/names, not just generalities
        specificity_indicators = [
            any(char.isdigit() for char in answer),  # contains numbers
            ":" in answer or "|" in answer,  # structured data
            len(answer.split()) >= 20,  # substantive length
        ]
        spec_score = sum(specificity_indicators) / len(specificity_indicators)
        checks.append(CheckResult(
            name="specificity",
            passed=spec_score >= 0.67,
            score=spec_score,
            max_score=1.0,
            details=f"{sum(specificity_indicators)}/{len(specificity_indicators)} specificity indicators",
        ))

        return checks

    def _check_build(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        expected = case.get("expected", {})

        # Check 1: design_present — has a workflow design
        design = output.get("design", {})
        has_design = bool(design)
        checks.append(CheckResult(
            name="design_present",
            passed=has_design,
            score=1.0 if has_design else 0.0,
            max_score=1.0,
            details="Workflow design present" if has_design else "No design in output",
        ))

        if not has_design:
            return checks

        # Check 2: architecture_specified — trigger type and connector strategy present
        has_trigger = bool(design.get("trigger_type"))
        has_steps = bool(design.get("steps")) and len(design.get("steps", [])) > 0
        arch_score = (int(has_trigger) + int(has_steps)) / 2
        arch_details = []
        if not has_trigger:
            arch_details.append("missing trigger_type")
        if not has_steps:
            arch_details.append("missing steps")
        checks.append(CheckResult(
            name="architecture_specified",
            passed=arch_score >= 0.5,
            score=arch_score,
            max_score=1.0,
            details="Architecture complete"
            if arch_score == 1.0
            else f"Incomplete: {'; '.join(arch_details)}",
        ))

        # Check 3: best_practices_checked — checks against the 10-item BP list
        bp_checked = output.get("best_practices_checked", [])
        expected_bp = expected.get("min_best_practices", 5)
        bp_count = len(bp_checked)
        bp_ok = bp_count >= expected_bp
        checks.append(CheckResult(
            name="best_practices_checked",
            passed=bp_ok,
            score=min(bp_count / expected_bp, 1.0) if expected_bp > 0 else 1.0,
            max_score=1.0,
            details=f"{bp_count} best practices checked (min {expected_bp})",
        ))

        # Check 4: error_handling_included — design addresses error handling
        has_error_handling = bool(design.get("error_handling"))
        checks.append(CheckResult(
            name="error_handling_included",
            passed=has_error_handling,
            score=1.0 if has_error_handling else 0.0,
            max_score=1.0,
            details="Error handling strategy present"
            if has_error_handling
            else "No error handling in design",
        ))

        return checks

    def _check_review(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        expected = case.get("expected", {})

        # Check 1: dimensions_scored — all 6 review dimensions have scores
        scores = output.get("scores", {})
        scored_dims = [d for d in REVIEW_DIMENSIONS if d in scores]
        dim_score = len(scored_dims) / len(REVIEW_DIMENSIONS)
        missing_dims = [d for d in REVIEW_DIMENSIONS if d not in scores]
        checks.append(CheckResult(
            name="dimensions_scored",
            passed=dim_score >= 0.83,  # 5 of 6
            score=dim_score,
            max_score=1.0,
            details=f"{len(scored_dims)}/{len(REVIEW_DIMENSIONS)} dimensions scored"
            + (f" — missing: {', '.join(missing_dims)}" if missing_dims else ""),
        ))

        # Check 2: risk_assessed — risk level present and valid
        risk_level = output.get("risk_level", "")
        valid_risks = {"low", "medium", "high"}
        risk_ok = risk_level.lower() in valid_risks
        checks.append(CheckResult(
            name="risk_assessed",
            passed=risk_ok,
            score=1.0 if risk_ok else 0.0,
            max_score=1.0,
            details=f"Risk level: {risk_level}"
            if risk_ok
            else f"Invalid/missing risk level: '{risk_level}'",
        ))

        # Check 3: issues_identified — found expected minimum number of issues
        issues = output.get("issues", [])
        min_issues = expected.get("min_issues", 1)
        issues_ok = len(issues) >= min_issues
        checks.append(CheckResult(
            name="issues_identified",
            passed=issues_ok,
            score=min(len(issues) / min_issues, 1.0) if min_issues > 0 else 1.0,
            max_score=1.0,
            details=f"{len(issues)} issues found (min {min_issues})",
        ))

        # Check 4: fixes_suggested — at least some issues have fix suggestions
        fixes = output.get("recommendations", [])
        has_fixes = len(fixes) > 0
        checks.append(CheckResult(
            name="fixes_suggested",
            passed=has_fixes,
            score=1.0 if has_fixes else 0.0,
            max_score=1.0,
            details=f"{len(fixes)} fix recommendations"
            if has_fixes
            else "No fix recommendations provided",
        ))

        # Check 5: score_accuracy — overall score within expected range
        overall_score = output.get("overall_score")
        expected_range = expected.get("score_range")
        if overall_score is not None and expected_range:
            in_range = expected_range[0] <= overall_score <= expected_range[1]
            checks.append(CheckResult(
                name="score_accuracy",
                passed=in_range,
                score=1.0 if in_range else 0.0,
                max_score=1.0,
                details=f"Score {overall_score} in range {expected_range}"
                if in_range
                else f"Score {overall_score} outside expected range {expected_range}",
            ))

        return checks
