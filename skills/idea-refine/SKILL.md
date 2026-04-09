---
name: idea-refine
description: |
  Refines ideas through structured divergent and convergent thinking. Use when scoping
  a new feature, brainstorming solutions, evaluating competing approaches, or
  stress-testing a plan before implementation. Trigger with "ideate" or "refine this idea".
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/idea-refine/SKILL.md
    adapted: "2026-04-09"
---

# Idea Refine

Refine raw ideas into sharp, actionable concepts through structured divergent and convergent thinking. An interactive dialogue skill — invoke it with an idea.

## When to Use

- Scoping a new feature or product direction
- Brainstorming solutions to a customer problem
- Evaluating competing approaches before committing
- Stress-testing a plan before implementation
- Generating variations on a concept to find the strongest version

## How It Works

Three phases, each doing one thing well:

1. **Understand & Expand (Divergent):** Restate, question, generate variations
2. **Evaluate & Converge:** Cluster, stress-test, surface assumptions
3. **Sharpen & Ship:** Produce a concrete one-pager

## Process

### Phase 1: Understand & Expand

**Goal:** Take the raw idea and open it up.

1. **Restate the idea** as a crisp "How Might We" problem statement
2. **Ask 3-5 sharpening questions** (no more):
   - Who is this for, specifically?
   - What does success look like?
   - What are the real constraints?
   - What's been tried before?
   - Why now?
3. **Generate 5-8 idea variations** using these lenses:
   - **Inversion:** What if we did the opposite?
   - **Constraint removal:** What if budget/time/tech weren't factors?
   - **Audience shift:** What if this were for a different user?
   - **Combination:** What if we merged this with an adjacent idea?
   - **Simplification:** What's the version that's 10x simpler?
   - **10x version:** What would this look like at massive scale?
   - **Expert lens:** What would domain experts find obvious?

**If running inside a codebase:** Use Glob, Grep, and Read to scan for existing architecture, patterns, and constraints. Ground variations in what actually exists.

### Phase 2: Evaluate & Converge

After the user reacts (indicates which ideas resonate, pushes back, adds context):

1. **Cluster** resonant ideas into 2-3 distinct directions
2. **Stress-test** each against:
   - **User value:** Painkiller or vitamin?
   - **Feasibility:** Technical and resource cost? Hardest part?
   - **Differentiation:** Would someone switch from their current solution?
3. **Surface hidden assumptions** for each direction:
   - What you're betting is true (but haven't validated)
   - What could kill this idea
   - What you're choosing to ignore (and why that's okay for now)

**Be honest, not supportive.** Push back on weak ideas with specificity and kindness.

### Phase 3: Sharpen & Ship

Produce a markdown one-pager:

```markdown
# [Idea Name]

## Problem Statement
[One-sentence "How Might We" framing]

## Recommended Direction
[The chosen direction and why — 2-3 paragraphs max]

## Key Assumptions to Validate
- [ ] [Assumption 1 — how to test it]
- [ ] [Assumption 2 — how to test it]

## MVP Scope
[The minimum version that tests the core assumption]

## Not Doing (and Why)
- [Thing 1] — [reason]
- [Thing 2] — [reason]

## Open Questions
- [Questions that need answering before building]
```

The "Not Doing" list is arguably the most valuable part. Focus is about saying no to good ideas.

Save to `docs/ideas/[idea-name].md` after user confirmation.

## Philosophy

- Simplicity is the ultimate sophistication. Push toward the simplest version that solves the real problem.
- Start with the user experience, work backwards to technology.
- Say no to 1,000 things. Focus beats breadth.
- Challenge every assumption. "How it's usually done" is not a reason.

## Anti-Patterns

- Generating 20+ shallow variations instead of 5-8 considered ones
- Skipping "who is this for"
- Being a yes-machine instead of pushing back on weak ideas
- Producing a plan without surfacing assumptions
- Jumping straight to output without running phases 1 and 2
- Ignoring existing codebase constraints when ideating inside a project

## Red Flags

- No clear "How Might We" problem statement
- No target user or success criteria defined
- Only one direction explored
- Hidden assumptions not surfaced
- No "Not Doing" list
- Output is conversation, not a concrete artifact

## Verification

- [ ] A clear problem statement exists
- [ ] Target user and success criteria are defined
- [ ] Multiple directions were explored
- [ ] Hidden assumptions are listed with validation strategies
- [ ] Trade-offs are explicit in a "Not Doing" list
- [ ] Output is a markdown one-pager, not just conversation
- [ ] User confirmed the direction before any implementation

