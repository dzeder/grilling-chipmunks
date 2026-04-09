"""Scorer for the tray-discovery skill.

Evaluates connector discovery outputs: connector identification, relevance scoring,
knowledge generation, and integration opportunity detection.

5 hard checks:
1. connectors_found — output has a non-empty connectors list
2. relevance_scored — each connector has a numeric relevance score (0-1)
3. knowledge_generated — knowledge entries produced with required fields
4. opportunities_detected — integration opportunities identified
5. expected_connectors — key expected connectors are present in results
"""

from __future__ import annotations

from evals.scorers.base import BaseScorer, CheckResult


class TrayDiscoveryScorer(BaseScorer):
    """Scorer for tray-discovery eval cases."""

    agent_name = "tray_discovery"

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        expected = case.get("expected", {})

        # --- Check 1: connectors_found ---
        connectors = output.get("connectors", [])
        has_connectors = len(connectors) > 0
        checks.append(CheckResult(
            name="connectors_found",
            passed=has_connectors,
            score=1.0 if has_connectors else 0.0,
            max_score=1.0,
            details=f"{len(connectors)} connectors found"
            if has_connectors
            else "No connectors in output",
        ))

        if not has_connectors:
            return checks

        # --- Check 2: relevance_scored ---
        scored = [c for c in connectors if isinstance(c.get("relevance_score"), (int, float))]
        valid_scores = [c for c in scored if 0 <= c["relevance_score"] <= 1]
        score_rate = len(valid_scores) / len(connectors)
        issues = []
        if len(scored) < len(connectors):
            issues.append(f"{len(connectors) - len(scored)} missing relevance_score")
        if len(valid_scores) < len(scored):
            issues.append(f"{len(scored) - len(valid_scores)} scores out of 0-1 range")
        checks.append(CheckResult(
            name="relevance_scored",
            passed=score_rate >= 0.75,
            score=score_rate,
            max_score=1.0,
            details=f"{len(valid_scores)}/{len(connectors)} properly scored"
            + (f" — {'; '.join(issues)}" if issues else ""),
        ))

        # --- Check 3: knowledge_generated ---
        knowledge = output.get("knowledge_entries", [])
        required_fields = {"connector_name", "category", "operations"}
        if knowledge:
            complete = [
                k for k in knowledge
                if required_fields.issubset(set(k.keys()))
            ]
            kg_score = len(complete) / len(knowledge)
            missing_in = len(knowledge) - len(complete)
            checks.append(CheckResult(
                name="knowledge_generated",
                passed=kg_score >= 0.75,
                score=kg_score,
                max_score=1.0,
                details=f"{len(complete)}/{len(knowledge)} knowledge entries complete"
                + (f" — {missing_in} missing required fields" if missing_in else ""),
            ))
        else:
            checks.append(CheckResult(
                name="knowledge_generated",
                passed=False,
                score=0.0,
                max_score=1.0,
                details="No knowledge entries generated",
            ))

        # --- Check 4: opportunities_detected ---
        opportunities = output.get("opportunities", [])
        min_opp = expected.get("min_opportunities", 1)
        opp_ok = len(opportunities) >= min_opp
        checks.append(CheckResult(
            name="opportunities_detected",
            passed=opp_ok,
            score=min(len(opportunities) / min_opp, 1.0) if min_opp > 0 else 1.0,
            max_score=1.0,
            details=f"{len(opportunities)} opportunities found (min {min_opp})",
        ))

        # --- Check 5: expected_connectors ---
        expected_names = expected.get("must_include_connectors", [])
        if expected_names:
            found_names = {c.get("name", "").lower() for c in connectors}
            matched = [n for n in expected_names if n.lower() in found_names]
            match_score = len(matched) / len(expected_names)
            missing = [n for n in expected_names if n.lower() not in found_names]
            checks.append(CheckResult(
                name="expected_connectors",
                passed=match_score >= 0.75,
                score=match_score,
                max_score=1.0,
                details=f"{len(matched)}/{len(expected_names)} expected connectors found"
                + (f" — missing: {', '.join(missing)}" if missing else ""),
            ))

        return checks
