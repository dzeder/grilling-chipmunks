---
name: deprecation
description: |
  Manages deprecation and migration. Use when removing old systems, APIs, or integrations.
  Use when migrating consumers from one implementation to another. Use when deciding
  whether to maintain or sunset existing code, Tray connectors, or SF customizations.
learned_from:
  - repo: addyosmani/agent-skills
    file: skills/deprecation-and-migration/SKILL.md
    adapted: "2026-04-09"
---

# Deprecation & Migration

Systematic approach to removing code, systems, and integrations that no longer earn their keep — and safely migrating consumers to replacements.

## When to Use

- Replacing an old system, API, or library with a new one
- Sunsetting a feature or integration that's no longer needed
- Consolidating duplicate implementations
- Removing dead code that nobody owns but everybody depends on
- Planning the lifecycle of a new system (deprecation planning starts at design time)
- Deciding whether to maintain a legacy system or invest in migration

## Ohanafy Context

This skill directly applies to:
- **Tray:** Retiring old connectors, migrating workflows to new patterns, sunsetting deprecated integration projects
- **Salesforce:** Removing old validation rules, formula fields, custom objects, or CPQ configs
- **AWS:** Decommissioning Lambda functions, retiring old API Gateway endpoints
- **Third-party:** Sunsetting deprecated logistics APIs, old payment gateways, legacy auth flows

## Core Principles

### Code Is a Liability
Every line has ongoing cost: tests, documentation, security patches, dependency updates, mental overhead. When the same functionality can be provided with less complexity, the old code should go.

### Hyrum's Law Makes Removal Hard
With enough users, every observable behavior becomes depended on — including bugs and undocumented side effects. Deprecation requires active migration, not just announcement.

### Plan for Removal at Design Time
When building something new, ask: "How would we remove this in 3 years?" Clean interfaces, feature flags, and minimal surface area make future deprecation easier.

## The Deprecation Decision

Before deprecating anything, answer these five questions:

```
1. Does this system still provide unique value?
   → If yes, maintain it. If no, proceed.

2. How many consumers depend on it?
   → Quantify the migration scope.

3. Does a replacement exist?
   → If no, build the replacement first. Never deprecate without an alternative.

4. What's the migration cost for each consumer?
   → If trivially automated, do it. If manual, weigh against maintenance cost.

5. What's the ongoing cost of NOT deprecating?
   → Security risk, engineer time, opportunity cost of complexity.
```

## Compulsory vs Advisory

| Type | When to Use | Mechanism |
|------|-------------|-----------|
| **Advisory** | Migration optional, old system stable | Warnings, documentation, nudges |
| **Compulsory** | Security issues, blocks progress, unsustainable maintenance | Hard deadline + migration tooling |

Default to advisory. Use compulsory only when the cost justifies forcing migration.

## The Migration Process

### Step 1: Build the Replacement
Don't deprecate without a working alternative that covers all critical use cases and is proven in production.

### Step 2: Announce and Document

```markdown
## Deprecation Notice: [System Name]

**Status:** Deprecated as of [date]
**Replacement:** [New system] (see migration guide)
**Removal date:** Advisory / [hard date]
**Reason:** [Why the old system is being retired]

### Migration Guide
1. [Step-by-step instructions]
2. [Include concrete examples]
3. [Provide verification commands]
```

### Step 3: Migrate Incrementally
One consumer at a time:
1. Identify all touchpoints with the deprecated system
2. Update to use the replacement
3. Verify behavior matches (tests, integration checks)
4. Remove references to the old system
5. Confirm no regressions

**The Churn Rule:** If you own the infrastructure being deprecated, you are responsible for migrating your users. Don't announce deprecation and leave users to figure it out.

### Step 4: Remove the Old System
Only after all consumers have migrated:
1. Verify zero active usage (metrics, logs, dependency analysis)
2. Remove the code
3. Remove associated tests, documentation, and configuration
4. Remove the deprecation notices
5. Celebrate — removing code is an achievement

## Migration Patterns

### Strangler Pattern
Run old and new in parallel. Route traffic incrementally from old to new. When old handles 0%, remove it.

### Adapter Pattern
Create an adapter that translates calls from the old interface to the new implementation. Consumers keep using the old interface while you migrate the backend.

### Feature Flag Migration
Use feature flags to switch consumers from old to new system one at a time. Provides instant rollback if the new system has issues.

## Zombie Code

Code nobody owns but everybody depends on. Signs:
- No commits in 6+ months but active consumers exist
- No assigned maintainer
- Failing tests nobody fixes
- Dependencies with known vulnerabilities nobody updates

**Response:** Either assign an owner and maintain it, or deprecate with a migration plan. Zombie code cannot stay in limbo.

## Red Flags

- Deprecated systems with no replacement available
- Deprecation announcements with no migration tooling
- "Soft" deprecation advisory for years with no progress
- New features added to a deprecated system
- Removing code without verifying zero active consumers

## Verification

- [ ] Replacement is production-proven and covers all critical use cases
- [ ] Migration guide exists with concrete steps and examples
- [ ] All active consumers have been migrated (verified by metrics/logs)
- [ ] Old code, tests, documentation, and configuration are fully removed
- [ ] No references to the deprecated system remain in the codebase

