# gh CLI Commands Reference

Commands used by the github-agent skill during audits. All require `gh` to be authenticated (`gh auth status`).

## Discovery

### Repo info
```bash
gh repo view --json nameWithOwner,defaultBranchRef,hasIssuesEnabled,isPrivate,visibility
```

### Recent workflow runs
```bash
# Last 20 runs with key fields
gh run list --limit 20 --json name,status,conclusion,createdAt,headBranch,event

# Failed runs only
gh run list --limit 20 --status failure --json name,conclusion,createdAt,headBranch,databaseId

# View specific run details
gh run view {run-id}

# View failed step logs
gh run view {run-id} --log-failed
```

### Workflow list
```bash
gh workflow list --json name,state,path
```

## Repo Configuration

### Branch protection
```bash
# Full protection rules (requires admin access)
gh api repos/{owner}/{repo}/branches/{branch}/protection --jq '{
  required_reviews: .required_pull_request_reviews.required_approving_review_count,
  status_checks: .required_status_checks.contexts,
  enforce_admins: .enforce_admins.enabled,
  linear_history: .required_linear_history.enabled,
  allow_force_push: .allow_force_pushes.enabled,
  allow_deletions: .allow_deletions.enabled
}'
```

**Note:** Returns 404 if no protection rules exist, 403 if insufficient permissions. Both are valid findings. If the check fails due to permissions, score the branch protection category as N/A and note in the report — do not assume branch protection is absent.

### Code scanning
```bash
# Check if code scanning is enabled (returns alerts or error)
gh api repos/{owner}/{repo}/code-scanning/alerts --jq 'length' 2>&1
```
- Returns count: code scanning is enabled
- Returns "not enabled" error: code scanning is disabled
- Returns 403: insufficient permissions

### Secret scanning
```bash
gh api repos/{owner}/{repo}/secret-scanning/alerts --jq 'length' 2>&1
```

### Dependabot
```bash
gh api repos/{owner}/{repo}/dependabot/alerts --jq 'length' 2>&1
```

## Labels and Issues

### Check for existing labels
```bash
gh label list --json name,description
```

### Check open issues by label
```bash
gh issue list --label "{label}" --state open --json number,title
```

## Error Handling

All `gh api` calls should handle these responses:
- **200**: Success, parse the response
- **403**: Insufficient permissions — note "unable to check" in report
- **404**: Feature not enabled or resource doesn't exist — note accordingly
- **Rate limited**: Back off and retry, or note in report

Pattern:
```bash
result=$(gh api repos/{owner}/{repo}/endpoint 2>&1)
if echo "$result" | grep -q "Not Found"; then
  echo "Feature not enabled or not accessible"
elif echo "$result" | grep -q "403"; then
  echo "Insufficient permissions to check"
else
  echo "$result"
fi
```
