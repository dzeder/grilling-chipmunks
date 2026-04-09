---
globs:
  - "*.cls"
  - "*.trigger"
  - "*.flow-meta.xml"
  - "lwc/**/*.js"
  - "lwc/**/*.html"
  - "*.soql"
  - "*.agent"
  - "*.object-meta.xml"
  - "*.field-meta.xml"
  - "*.namedCredential-meta.xml"
---

# Salesforce Skill Routing

When editing Salesforce files, invoke the matching skill FIRST:

| File Pattern | Skill |
|-------------|-------|
| `.cls`, `.trigger` | sf-apex |
| `.flow-meta.xml` | sf-flow |
| `lwc/**/*.js`, `lwc/**/*.html` | sf-lwc |
| `.soql` | sf-soql |
| `.agent` | sf-ai-agentscript |
| `.object-meta.xml`, `.field-meta.xml` | sf-metadata |
| `.namedCredential-meta.xml` | sf-integration |

For Excel/CSV data imports, use the data-harmonizer skill.

Full routing matrix: `docs/SKILL_ROUTING_MATRIX.md`
