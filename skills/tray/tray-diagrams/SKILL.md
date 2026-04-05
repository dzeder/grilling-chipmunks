---
name: tray-diagrams
description: >
  Mermaid diagram generation for Tray.io workflows — flow direction standards,
  arrow styles, node naming conventions, architecture diagrams, and sequence diagrams.
  TRIGGER when: user asks for a Tray workflow diagram, Mermaid visualization,
  flowchart of an integration, or visual documentation of Tray workflows.
---

# Tray.io Mermaid Diagram Expert

## Description
Expert knowledge of creating Mermaid diagrams for Tray.io workflows. Knows flow direction standards (vertical for main workflows, horizontal for callables), arrow styles (solid, dotted), and node naming conventions. Use when creating visual documentation for Tray workflows.

## When to Use
Invoke this skill when:
- Creating Mermaid diagrams for Tray.io workflows
- Documenting workflow visual architecture
- Need to understand arrow styles (`-.->` for fire-and-forget)
- Questions about diagram flow direction (vertical vs horizontal)
- Need diagram storage location guidance
- Keywords: "diagram", "mermaid", "visualization", "flowchart", "workflow diagram", "visual"

## Reference Files
- `diagram-patterns.md` - Complete Mermaid diagram standards

## Quick Reference

### Flow Direction Rules
- **Main workflows**: Vertical (top-down) with solid arrows `-->`
- **Callable workflows**: Horizontal extension with dotted arrows `-.->`
- **Fire-and-forget**: Dotted arrow `-.->` (continues without waiting)
- **Fire-and-wait**: Bi-directional dotted arrows (waits for response)

### Node Naming Pattern
```
[Component Type: Action Description]
```

Examples:
- `[Trigger: Webhook]`
- `[Script: Transform Data]`
- `[Salesforce: Upsert Records]`
- `[Callable: Error Handler]`

### Common Component Types
- Trigger, Script, Salesforce, Callable, Email, HTTP, Conditional

### Storage Locations
- Project diagrams: `versions/current/diagrams/`
- Documentation: `versions/current/documentation/README.md`

## Delegation

Do not trigger this skill for:
- General Tray.io questions or workflow design -- delegate to `tray-expert`
- Salesforce-specific Mermaid diagrams (ERDs, flow charts) -- delegate to `sf-diagram-mermaid`
- Tray script generation or debugging -- delegate to `tray-script-generator` or `tray-errors`
- Tray usage metrics and analytics -- delegate to `tray-insights`
