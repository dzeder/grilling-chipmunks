---
globs: []
---

# Skill Discovery Protocol

When unsure which skill handles a request — or when the CLAUDE.md quick-ref doesn't match — use this protocol.

## When to Use

- User's request doesn't match any CLAUDE.md routing pattern
- A skill needs to hand off but the routing matrix has no entry
- User asks "which skill does X?" or "what can handle Y?"
- You're routing a multi-domain request and need to identify all relevant skills

## Lookup Procedure

1. Read `docs/skill-index.yaml` (the machine-readable index of all 109+ skills)
2. Search the `triggers` fields for keyword matches against the user's request
3. Filter OUT any skills whose `anti_triggers` match the request
4. If multiple candidates remain:
   - Prefer the skill whose `pillar` matches the active workspace domain (from `.context/workspace.md`)
   - Prefer skills with more specific triggers over generic ones
   - If still tied, present the top 2-3 candidates to the user with a one-line summary each
5. Check the matched skill's `delegates_to` list — it may chain to related skills

## Skill Chain Lookup

If the task is multi-step, also check `docs/skill-chains.yaml`:
1. Match the request against `trigger_phrases` for each chain
2. If a chain matches, suggest executing it: "This looks like a [chain-name] workflow"
3. Present the chain steps and ask for confirmation

## Knowledge Discovery

If the task needs domain knowledge:
1. Check `knowledge-base/INDEX.yaml` for the domain
2. Load files whose `relevant_skills` include the active skill
3. Load at most 3 knowledge files per task to stay within context budget

## Dependency Awareness

When a skill has `depends_on` in its frontmatter:
- Verify the prerequisite skill has been run (or its output is available)
- If not, suggest running the prerequisite first

When a skill has `chains_to`:
- After the skill completes, suggest the natural next step
- Don't auto-invoke — always confirm with the user
