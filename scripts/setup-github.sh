#!/bin/bash
# One-shot GitHub project setup script
# Creates labels, milestones, and project board for dzeder/pricing
# Prerequisites: gh auth refresh -s read:project -s project
set -euo pipefail

REPO="dzeder/pricing"

echo "=== Setting up GitHub project infrastructure for $REPO ==="

# ─── Delete default labels ───
echo ""
echo "--- Removing default labels ---"
for label in "bug" "documentation" "duplicate" "enhancement" "good first issue" "help wanted" "invalid" "question" "wontfix"; do
  gh label delete "$label" --repo "$REPO" --yes 2>/dev/null && echo "  Deleted: $label" || echo "  Skip (not found): $label"
done

# ─── Create labels ───
echo ""
echo "--- Creating priority labels ---"
gh label create "priority:critical" --color "b60205" --description "Blocking; must fix immediately" --repo "$REPO" 2>/dev/null || echo "  Exists: priority:critical"
gh label create "priority:high" --color "d93f0b" --description "Important; next sprint" --repo "$REPO" 2>/dev/null || echo "  Exists: priority:high"
gh label create "priority:medium" --color "e99695" --description "Normal priority" --repo "$REPO" 2>/dev/null || echo "  Exists: priority:medium"
gh label create "priority:low" --color "f9d0c4" --description "Nice to have; backlog" --repo "$REPO" 2>/dev/null || echo "  Exists: priority:low"

echo ""
echo "--- Creating type labels ---"
gh label create "type:feature" --color "0052cc" --description "New feature or capability" --repo "$REPO" 2>/dev/null || echo "  Exists: type:feature"
gh label create "type:bug" --color "d73a4a" --description "Something is broken" --repo "$REPO" 2>/dev/null || echo "  Exists: type:bug"
gh label create "type:task" --color "1d76db" --description "General task or chore" --repo "$REPO" 2>/dev/null || echo "  Exists: type:task"
gh label create "type:docs" --color "0075ca" --description "Documentation work" --repo "$REPO" 2>/dev/null || echo "  Exists: type:docs"
gh label create "type:refactor" --color "5319e7" --description "Code refactoring" --repo "$REPO" 2>/dev/null || echo "  Exists: type:refactor"
gh label create "type:test" --color "006b75" --description "Test creation or improvement" --repo "$REPO" 2>/dev/null || echo "  Exists: type:test"
gh label create "type:data-model" --color "0e8a16" --description "Data model changes" --repo "$REPO" 2>/dev/null || echo "  Exists: type:data-model"
gh label create "type:spike" --color "c5def5" --description "Research or exploration" --repo "$REPO" 2>/dev/null || echo "  Exists: type:spike"

echo ""
echo "--- Creating status labels ---"
gh label create "status:triage" --color "fbca04" --description "Needs triage and prioritization" --repo "$REPO" 2>/dev/null || echo "  Exists: status:triage"
gh label create "status:blocked" --color "b60205" --description "Blocked by dependency" --repo "$REPO" 2>/dev/null || echo "  Exists: status:blocked"
gh label create "status:in-review" --color "0e8a16" --description "Under review" --repo "$REPO" 2>/dev/null || echo "  Exists: status:in-review"
gh label create "status:ready" --color "2ea44f" --description "Ready to work on" --repo "$REPO" 2>/dev/null || echo "  Exists: status:ready"
gh label create "status:wontfix" --color "ffffff" --description "Will not be addressed" --repo "$REPO" 2>/dev/null || echo "  Exists: status:wontfix"
gh label create "status:duplicate" --color "cfd3d7" --description "Duplicate of another issue" --repo "$REPO" 2>/dev/null || echo "  Exists: status:duplicate"
gh label create "status:stale" --color "ededed" --description "No recent activity" --repo "$REPO" 2>/dev/null || echo "  Exists: status:stale"

echo ""
echo "--- Creating component labels ---"
gh label create "component:pricing-engine" --color "0e8a16" --description "Core pricing calculation logic" --repo "$REPO" 2>/dev/null || echo "  Exists: component:pricing-engine"
gh label create "component:data-model" --color "006b75" --description "Database schema and entities" --repo "$REPO" 2>/dev/null || echo "  Exists: component:data-model"
gh label create "component:api" --color "1d76db" --description "API endpoints" --repo "$REPO" 2>/dev/null || echo "  Exists: component:api"
gh label create "component:ui" --color "d4c5f9" --description "User interface" --repo "$REPO" 2>/dev/null || echo "  Exists: component:ui"
gh label create "component:docs" --color "0075ca" --description "Documentation system" --repo "$REPO" 2>/dev/null || echo "  Exists: component:docs"
gh label create "component:ci-cd" --color "e4e669" --description "CI/CD and automation" --repo "$REPO" 2>/dev/null || echo "  Exists: component:ci-cd"
gh label create "component:billback" --color "c2e0c6" --description "Billback processing" --repo "$REPO" 2>/dev/null || echo "  Exists: component:billback"
gh label create "component:promotions" --color "bfdadc" --description "Promotion programs" --repo "$REPO" 2>/dev/null || echo "  Exists: component:promotions"

echo ""
echo "--- Creating agent labels ---"
gh label create "agent:pr-review" --color "7057ff" --description "Touched by PR Review Agent" --repo "$REPO" 2>/dev/null || echo "  Exists: agent:pr-review"
gh label create "agent:qa" --color "8b5cf6" --description "Touched by QA Agent" --repo "$REPO" 2>/dev/null || echo "  Exists: agent:qa"
gh label create "agent:docs" --color "a855f7" --description "Touched by Docs Agent" --repo "$REPO" 2>/dev/null || echo "  Exists: agent:docs"
gh label create "agent:security" --color "6d28d9" --description "Touched by Security Agent" --repo "$REPO" 2>/dev/null || echo "  Exists: agent:security"
gh label create "agent:auto-labeled" --color "c084fc" --description "Label applied by automation" --repo "$REPO" 2>/dev/null || echo "  Exists: agent:auto-labeled"

echo ""
echo "--- Creating effort labels ---"
gh label create "effort:xs" --color "bfd4f2" --description "Extra small (< 1 hour)" --repo "$REPO" 2>/dev/null || echo "  Exists: effort:xs"
gh label create "effort:s" --color "c5def5" --description "Small (1-4 hours)" --repo "$REPO" 2>/dev/null || echo "  Exists: effort:s"
gh label create "effort:m" --color "bfdadc" --description "Medium (4-8 hours)" --repo "$REPO" 2>/dev/null || echo "  Exists: effort:m"
gh label create "effort:l" --color "d4c5f9" --description "Large (1-3 days)" --repo "$REPO" 2>/dev/null || echo "  Exists: effort:l"
gh label create "effort:xl" --color "e99695" --description "Extra large (> 3 days)" --repo "$REPO" 2>/dev/null || echo "  Exists: effort:xl"

echo ""
echo "--- Creating meta labels ---"
gh label create "good-first-issue" --color "7057ff" --description "Good for newcomers" --repo "$REPO" 2>/dev/null || echo "  Exists: good-first-issue"
gh label create "help-wanted" --color "008672" --description "Extra attention needed" --repo "$REPO" 2>/dev/null || echo "  Exists: help-wanted"
gh label create "ai-generated" --color "ededed" --description "Created or substantially done by AI" --repo "$REPO" 2>/dev/null || echo "  Exists: ai-generated"

# ─── Create milestones ───
echo ""
echo "--- Creating milestones ---"
gh api repos/$REPO/milestones -f title="M0: Project Infrastructure" \
  -f description="Repository setup, CI/CD, templates, labels, project board" \
  -f due_on="2026-03-27T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M0" || echo "  Exists: M0"

gh api repos/$REPO/milestones -f title="M1: Data Model Foundation" \
  -f description="Core data model: promotion_program, pricing_group, pricing_group_rule, scopes" \
  -f due_on="2026-04-03T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M1" || echo "  Exists: M1"

gh api repos/$REPO/milestones -f title="M2: Red Bull Use Case" \
  -f description="End-to-end Red Bull tier pricing with on-invoice discounts and billbacks" \
  -f due_on="2026-04-10T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M2" || echo "  Exists: M2"

gh api repos/$REPO/milestones -f title="M3: Pricing Engine MVP" \
  -f description="Working pricing calculation engine with API" \
  -f due_on="2026-04-17T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M3" || echo "  Exists: M3"

gh api repos/$REPO/milestones -f title="M4: Analytics & Reporting" \
  -f description="Reporting, analytics dashboards, billback reconciliation" \
  -f due_on="2026-04-24T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M4" || echo "  Exists: M4"

gh api repos/$REPO/milestones -f title="M5: Production Release" \
  -f description="Production-ready release with full documentation" \
  -f due_on="2026-05-01T00:00:00Z" -f state="open" 2>/dev/null && echo "  Created: M5" || echo "  Exists: M5"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Labels: $(gh label list --repo $REPO --json name --jq 'length') created"
echo "Milestones: $(gh api repos/$REPO/milestones --jq 'length') created"
echo ""
echo "Next steps:"
echo "  1. Run: gh auth refresh -s read:project -s project"
echo "  2. Run: gh project create --owner dzeder --title 'Ohanafy Promo Pricing Redesign'"
echo "  3. Add custom fields to the project via GitHub web UI"
