# Diff Summarizer Examples

## Summarize a git diff

```python
from skills.docs.diff_summarizer.skill import run
from skills.docs.diff_summarizer.schema import DiffSummarizerInput

diff = """
diff --git a/src/orders.py b/src/orders.py
--- a/src/orders.py
+++ b/src/orders.py
@@ -10,6 +10,10 @@
+def cancel_order(order_id: str) -> bool:
+    \"\"\"Cancel an order by ID.\"\"\"
+    order = get_order(order_id)
+    return order.cancel()
"""

result = await run(DiffSummarizerInput(
    diff_text=diff,
    audience="developer",
    format="markdown",
))
print(result.summary)
print(f"Files: {result.files_changed}, +{result.lines_added}, -{result.lines_removed}")
```

## Summarize a commit range

```python
result = await run(DiffSummarizerInput(
    commit_range="v1.0.0..v1.1.0",
    audience="stakeholder",
    format="markdown",
    operation="summarize_commits",
    repo_path="/path/to/repo",
))
```

## Generate release notes

```python
result = await run(DiffSummarizerInput(
    commit_range="v1.1.0..v1.2.0",
    audience="end_user",
    format="markdown",
    operation="generate_release_notes",
    repo_path="/path/to/repo",
))
```

## Detect breaking changes

```python
result = await run(DiffSummarizerInput(
    commit_range="v1.0.0..v2.0.0",
    operation="detect_breaking_changes",
    repo_path="/path/to/repo",
))
for change in result.breaking_changes:
    print(f"BREAKING: {change}")
```
