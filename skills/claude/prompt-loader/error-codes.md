# Prompt Loader Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `PL-001` | Prompt not found | Verify prompt name exists in `skills/claude/prompts/`. |
| `PL-002` | Version not found | Check available versions for this prompt. |
| `PL-003` | Missing required variable | Provide all required template variables. |
| `PL-004` | Invalid prompt YAML | Fix YAML syntax in the prompt file. |
| `PL-005` | Prompt template is empty | Ensure the template field is non-empty. |
| `PL-006` | Version format invalid | Use semantic versioning (e.g., `1.2.0`). |
| `PL-007` | Rendered prompt exceeds token budget | Reduce variable content or use a shorter prompt version. |
| `PL-008` | Prompt directory not found | Ensure `skills/claude/prompts/` exists. |
