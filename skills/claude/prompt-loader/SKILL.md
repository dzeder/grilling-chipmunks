# Prompt Loader Skill

## Purpose

Load and version-control prompts for Claude-based agents. All prompts at Ohanafy are semver'd and stored in `skills/claude/prompts/`. No inline prompt strings -- every prompt is loaded through this skill.

## Constraints

- **All prompts semver'd** -- every prompt has a version following semantic versioning (e.g., `1.2.0`).
- **Stored in `skills/claude/prompts/`** -- prompts live in YAML files, not inline in code.
- **Immutable versions** -- once a version is published, it cannot be modified. Create a new version instead.
- **Template variables** -- prompts support `{variable}` placeholder syntax.
- **Validation** -- prompts are validated for required variables before rendering.
- **Audit trail** -- every prompt load is logged with version, agent, and timestamp.

## Prompt File Format

```yaml
name: order-classification
version: 1.2.0
description: Classify incoming orders by priority.
template: |
  You are an order classifier for {company}.
  Classify the following order as {categories}.
  Order: {order_text}
variables:
  - company
  - categories
  - order_text
```

## Inputs

- `prompt_name`: Name of the prompt to load.
- `version`: Specific version or `latest`.
- `variables`: Dictionary of template variables to render.

## Outputs

- `rendered_prompt`: The fully rendered prompt string.
- `prompt_version`: The version that was loaded.
- `token_estimate`: Estimated token count for the rendered prompt.

## Error Handling

Missing variables cause a validation error before rendering. Unknown prompt names return a clear error. See `error-codes.md` for all codes.

## Dependencies

- Prompt files in `skills/claude/prompts/`.
- `context-manager` skill for token budget tracking.
