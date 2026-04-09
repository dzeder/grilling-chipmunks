---
globs:
  - "integrations/patterns/*.js"
  - "integrations/tray/**/*"
---

# Integration Development Rules

- Always use `script-scaffold.js` as the starting template for new scripts
- Follow the validate → transform → batch → output flow
- Use existing patterns from `integrations/patterns/` — never duplicate modules
- Test with `/test-script` skill before committing
- Built artifacts (Tray exports) go to `dzeder/daniels-ohanafy-artifacts`, never this repo

## Tray-First Rule

Ohanafy has extensive existing Tray workflows. Before building anything new:
1. Check existing Tray workflows for overlap
2. Never duplicate — extend or reference existing workflows
3. Tray webhooks must validate HMAC signatures
