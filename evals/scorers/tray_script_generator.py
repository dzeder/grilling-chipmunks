"""Scorer for the tray-script-generator skill.

Evaluates generated Tray.io scripts against FP patterns, structure rules,
library compliance, Salesforce-specific requirements, and error handling.

6 hard checks:
1. script_exists — output has a non-empty script field
2. structure_compliance — constants at top, exports.step present, helpers below
3. fp_compliance — no inline functions, no mutations, no console.log, no imperative loops
4. library_compliance — only uses available Tray libraries
5. sf_url_encoding — uses encodeURIComponent when SF external IDs are present (conditional)
6. error_handling — structured error handling present when expected
"""

from __future__ import annotations

import re

from evals.scorers.base import BaseScorer, CheckResult


# Libraries available in Tray.io script runtime
AVAILABLE_LIBS = {"lodash", "moment-timezone", "crypto"}
# Buffer and URL are globals, not require'd


class TrayScriptGeneratorScorer(BaseScorer):
    """Scorer for tray-script-generator eval cases."""

    agent_name = "tray_script_generator"

    def hard_checks(self, case: dict, output: dict) -> list[CheckResult]:
        checks = []
        script = output.get("script", "")
        expected = case.get("expected", {})

        # --- Check 1: script_exists ---
        has_script = bool(script.strip())
        checks.append(CheckResult(
            name="script_exists",
            passed=has_script,
            score=1.0 if has_script else 0.0,
            max_score=1.0,
            details="Script present" if has_script else "No script in output",
        ))

        if not has_script:
            return checks

        # --- Check 2: structure_compliance ---
        structure_issues = []
        structure_score = 0.0
        max_structure = 3.0  # 3 sub-checks

        # 2a: exports.step exists
        has_exports_step = bool(re.search(r"exports\.step\s*=", script))
        if has_exports_step:
            structure_score += 1.0
        else:
            structure_issues.append("missing exports.step")

        # 2b: constants defined before exports.step
        exports_pos = _find_exports_step_pos(script)
        if exports_pos is not None and exports_pos > 0:
            before_step = script[:exports_pos]
            has_const_before = bool(re.search(r"\bconst\s+[A-Z_]+\s*=", before_step))
            if has_const_before:
                structure_score += 1.0
            else:
                structure_issues.append("no constants defined before exports.step")
        elif exports_pos == 0:
            structure_issues.append("exports.step at file start, no constants before it")
        else:
            structure_score += 1.0  # skip if no exports.step (already flagged above)

        # 2c: helper functions defined (anywhere — the key rule is they exist outside exports.step)
        helper_funcs = re.findall(r"\nfunction\s+\w+\s*\(", script)
        if helper_funcs:
            structure_score += 1.0
        else:
            structure_issues.append("no helper functions found outside exports.step")

        norm_score = structure_score / max_structure
        checks.append(CheckResult(
            name="structure_compliance",
            passed=norm_score >= 0.67,  # 2 of 3 sub-checks
            score=norm_score,
            max_score=1.0,
            details=f"{int(structure_score)}/{int(max_structure)} structure checks passed"
            + (f" — {'; '.join(structure_issues)}" if structure_issues else ""),
        ))

        # --- Check 3: fp_compliance ---
        fp_issues = []
        fp_score = 0.0
        max_fp = 4.0  # 4 sub-checks

        # 3a: no console.log
        if "console.log" not in script and "console.warn" not in script:
            fp_score += 1.0
        else:
            fp_issues.append("contains console.log/warn (side effect)")

        # 3b: no direct mutation of input parameters
        # Check for common mutation patterns — .push(), .splice(), .shift(), .pop() on non-new arrays
        # We allow mutations on locally-created arrays, so check for patterns like param.push()
        mutation_patterns = re.findall(
            r"(?:input|data|items|records|configuration)\s*[\.\[].*(\.push|\.splice|\.shift|\.unshift|\.pop)\(",
            script,
        )
        if not mutation_patterns:
            fp_score += 1.0
        else:
            fp_issues.append(f"potential input mutation: {len(mutation_patterns)} pattern(s)")

        # 3c: no imperative for/while loops (prefer .map, .filter, .reduce)
        imperative_loops = re.findall(r"\bfor\s*\(", script)
        while_loops = re.findall(r"\bwhile\s*\(", script)
        if not imperative_loops and not while_loops:
            fp_score += 1.0
        else:
            count = len(imperative_loops) + len(while_loops)
            fp_issues.append(f"{count} imperative loop(s) — use .map/.filter/.reduce")

        # 3d: no inline function definitions inside exports.step body
        step_body = _extract_exports_step_body(script)
        if step_body is not None:
            inline_funcs = re.findall(
                r"(?:const|let|var)\s+\w+\s*=\s*(?:function|\([^)]*\)\s*=>|\w+\s*=>)",
                step_body,
            )
            if not inline_funcs:
                fp_score += 1.0
            else:
                fp_issues.append(f"{len(inline_funcs)} inline function(s) in exports.step")
        else:
            fp_score += 1.0  # can't check without step body

        norm_fp = fp_score / max_fp
        checks.append(CheckResult(
            name="fp_compliance",
            passed=norm_fp >= 1.0,  # all 4 sub-checks required (hard rules from SKILL.md)
            score=norm_fp,
            max_score=1.0,
            details=f"{int(fp_score)}/{int(max_fp)} FP checks passed"
            + (f" — {'; '.join(fp_issues)}" if fp_issues else ""),
        ))

        # --- Check 4: library_compliance ---
        requires = set(re.findall(r"require\(\s*['\"](.+?)['\"]\s*\)", script))
        imports = set(re.findall(r"import\s+.+?\s+from\s+['\"](.+?)['\"]", script))
        all_libs = requires | imports
        invalid_libs = all_libs - AVAILABLE_LIBS
        lib_ok = len(invalid_libs) == 0
        checks.append(CheckResult(
            name="library_compliance",
            passed=lib_ok,
            score=1.0 if lib_ok else 0.0,
            max_score=1.0,
            details="All libraries available in Tray runtime"
            if lib_ok
            else f"Unavailable libraries: {', '.join(sorted(invalid_libs))}",
        ))

        # --- Check 5: sf_url_encoding (conditional) ---
        if expected.get("requires_url_encoding", False):
            has_encode = "encodeURIComponent" in script
            checks.append(CheckResult(
                name="sf_url_encoding",
                passed=has_encode,
                score=1.0 if has_encode else 0.0,
                max_score=1.0,
                details="encodeURIComponent present for external IDs"
                if has_encode
                else "Missing encodeURIComponent — SF external IDs must be URL-encoded",
            ))

        # --- Check 6: error_handling (conditional) ---
        if expected.get("requires_error_handling", False):
            error_indicators = [
                bool(re.search(r"error|Error", script)),
                bool(re.search(r"try\s*\{", script)) or bool(re.search(r"statusCode", script)),
                bool(re.search(r"retryable|retryStrategy|ERROR_TYPES", script)),
            ]
            error_score = sum(error_indicators) / len(error_indicators)
            checks.append(CheckResult(
                name="error_handling",
                passed=error_score >= 0.67,
                score=error_score,
                max_score=1.0,
                details=f"{sum(error_indicators)}/{len(error_indicators)} error handling indicators present",
            ))

        return checks


def _find_exports_step_pos(script: str) -> int | None:
    """Find the character position of exports.step in the script."""
    match = re.search(r"exports\.step\s*=", script)
    return match.start() if match else None


def _extract_exports_step_body(script: str) -> str | None:
    """Extract the body of exports.step function (between first { and matching })."""
    match = re.search(r"exports\.step\s*=\s*function\s*\([^)]*\)\s*\{", script)
    if not match:
        return None

    start = match.end() - 1  # position of opening {
    depth = 0
    for i in range(start, len(script)):
        if script[i] == "{":
            depth += 1
        elif script[i] == "}":
            depth -= 1
            if depth == 0:
                return script[start + 1 : i]
    return None
