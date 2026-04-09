---
name: simplify
description: |
  Simplifies code for clarity without changing behavior. Use when refactoring code for
  readability, when code works but is harder to maintain than it should be, or when
  reviewing code that has accumulated unnecessary complexity.
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/code-simplification/SKILL.md
    adapted: "2026-04-09"
---

# Simplify

Reduce code complexity while preserving exact behavior. The goal is not fewer lines — it's code that is easier to read, understand, modify, and debug.

## When to Use

- After a feature is working and tests pass, but the implementation feels heavier than it needs to be
- During code review when readability or complexity issues are flagged
- When you encounter deeply nested logic, long functions, or unclear names
- When consolidating related logic scattered across files
- After merging changes that introduced duplication or inconsistency

**When NOT to use:**
- Code is already clean and readable
- You don't understand what the code does yet — comprehend before you simplify
- The code is performance-critical and the "simpler" version would be measurably slower
- You're about to rewrite the module entirely

## The Five Principles

### 1. Preserve Behavior Exactly

Don't change what the code does — only how it expresses it. All inputs, outputs, side effects, error behavior, and edge cases must remain identical.

```
ASK BEFORE EVERY CHANGE:
- Does this produce the same output for every input?
- Does this maintain the same error behavior?
- Does this preserve the same side effects and ordering?
- Do all existing tests still pass without modification?
```

### 2. Follow Project Conventions

Simplification means making code more consistent with the codebase, not imposing external preferences. Study how neighboring code handles similar patterns first.

Simplification that breaks project consistency is not simplification — it's churn.

### 3. Prefer Clarity Over Cleverness

Explicit code is better than compact code when the compact version requires a mental pause to parse. A 1-line nested ternary is not simpler than a 5-line if/else.

### 4. Maintain Balance

Watch for over-simplification traps:
- **Inlining too aggressively** — removing a helper that gave a concept a name
- **Combining unrelated logic** — two simple functions merged into one complex function
- **Removing "unnecessary" abstraction** — some exist for extensibility or testability
- **Optimizing for line count** — fewer lines is not the goal

### 5. Scope to What Changed

Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code unless explicitly asked. Unscoped simplification creates noise in diffs and risks regressions.

## Process

### Step 1: Understand Before Touching (Chesterton's Fence)

Before changing or removing anything, understand why it exists. If you see a fence across a road and don't understand why it's there, don't tear it down.

```
BEFORE SIMPLIFYING, ANSWER:
- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that define the expected behavior?
- Why might it have been written this way?
- Check git blame: what was the original context?
```

If you can't answer these, you're not ready to simplify.

### Step 2: Identify Opportunities

**Structural complexity:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Deep nesting (3+ levels) | Hard to follow control flow | Guard clauses or helper functions |
| Long functions (50+ lines) | Multiple responsibilities | Split into focused functions |
| Nested ternaries | Requires mental stack | if/else or lookup objects |
| Repeated conditionals | Same check in multiple places | Extract to predicate function |

**Naming:**

| Pattern | Simplification |
|---------|----------------|
| Generic names (`data`, `result`, `temp`) | Rename to describe content |
| Comments explaining "what" | Delete — the code is clear enough |
| Comments explaining "why" | Keep — they carry intent the code can't |

**Redundancy:**

| Pattern | Simplification |
|---------|----------------|
| Duplicated logic (5+ lines) | Extract to shared function |
| Dead code, unreachable branches | Remove (after confirming truly dead) |
| Unnecessary abstractions | Inline the wrapper |
| Over-engineered patterns | Replace with direct approach |

### Step 3: Apply Incrementally

One simplification at a time. Run tests after each change. Submit refactoring changes separately from feature or bug fix changes.

```
FOR EACH SIMPLIFICATION:
1. Make the change
2. Run the test suite
3. If tests pass → commit
4. If tests fail → revert and reconsider
```

### Step 4: Verify

```
COMPARE BEFORE AND AFTER:
- Is the simplified version genuinely easier to understand?
- Did you introduce any new patterns inconsistent with the codebase?
- Is the diff clean and reviewable?
```

If the "simplified" version is harder to understand, revert.

## Red Flags

- Simplification that requires modifying tests to pass (you likely changed behavior)
- "Simplified" code that is longer and harder to follow than the original
- Renaming things to match your preferences rather than project conventions
- Removing error handling because "it makes the code cleaner"
- Simplifying code you don't fully understand
- Batching many simplifications into one large commit

## Verification

- [ ] All existing tests pass without modification
- [ ] Build succeeds with no new warnings
- [ ] Each simplification is a reviewable, incremental change
- [ ] Simplified code follows project conventions
- [ ] No error handling was removed or weakened
- [ ] No dead code was left behind

