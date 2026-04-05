# Diff Summarizer Skill

## Purpose

Summarize git diffs into human-readable changelogs. This skill takes raw git diffs and produces clear, categorized summaries suitable for release notes, PR descriptions, and team updates.

## Constraints

- **Input**: Raw git diff output or commit range.
- **Output categories**: Features, bug fixes, refactoring, documentation, tests, dependencies.
- **Audience-aware**: Summaries are tailored to the target audience (developer, stakeholder, end-user).
- **No secrets**: Diffs containing secrets or credentials are flagged and redacted.
- **Max diff size**: Diffs larger than 50,000 lines are summarized by file-level changes only.
- **Conventional commits**: If the repo uses conventional commits, categories are derived from commit prefixes.

## Supported Operations

- `summarize_diff` -- Summarize a git diff into a changelog.
- `summarize_commits` -- Summarize a range of commits.
- `generate_release_notes` -- Generate formatted release notes.
- `detect_breaking_changes` -- Identify breaking changes in the diff.

## Inputs

- `diff_text`: Raw git diff string (for summarize_diff).
- `commit_range`: Git commit range like `v1.0.0..v1.1.0` (for summarize_commits).
- `audience`: Target audience (developer, stakeholder, end_user).
- `format`: Output format (markdown, plaintext).
- `repo_path`: Path to the git repository.

## Outputs

- `summary`: The generated summary text.
- `categories`: Breakdown of changes by category.
- `breaking_changes`: List of breaking changes (if any).
- `files_changed`: Number of files changed.
- `lines_added`: Total lines added.
- `lines_removed`: Total lines removed.

## Dependencies

- `model-router` skill for Claude API calls (summarization uses Sonnet).
- Git CLI for commit range operations.
