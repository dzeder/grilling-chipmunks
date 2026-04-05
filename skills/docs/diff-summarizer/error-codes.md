# Diff Summarizer Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `DS-001` | No diff or commit range provided | Provide either diff_text or commit_range. |
| `DS-002` | Invalid commit range | Verify that both commits exist in the repository. |
| `DS-003` | Repository path not found | Check that repo_path points to a valid git repository. |
| `DS-004` | Diff too large (>50,000 lines) | File-level summary used instead of line-level. |
| `DS-005` | Secret detected in diff | Flagged lines are redacted. Review and remove secrets from code. |
| `DS-006` | Git command failed | Check git installation and repository integrity. |
| `DS-007` | Claude API error during summarization | Check model-router configuration and API key. |
| `DS-008` | Invalid audience type | Use developer, stakeholder, or end_user. |
