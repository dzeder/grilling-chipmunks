---
name: tray-architecture
description: Tray.io project architecture — workspace→project→version→step hierarchy, UUID preservation, version management, and directory structure compliance.
---

# Tray.io Project Architecture Expert

## Description
Expert knowledge of Tray.io project structure, UUID preservation, version management, and directory navigation. Use when working with Tray.io project exports, navigating workspaces/projects/versions, or ensuring proper directory structure compliance.

## When to Use
Invoke this skill when:
- Navigating Tray.io project directories (workspace/project/version hierarchy)
- Questions about UUID preservation or project-metadata.json
- Need to understand 4-level hierarchy (Workspace → Project → Version → Component)
- Validating directory structure before modifications
- Setting up new Tray.io project exports
- Troubleshooting sync issues with tray-sync.js
- Keywords: "workspace", "version", "UUID", "metadata", "project structure", "hierarchy"

## Reference Files
- `architecture-reference.md` - Complete architecture documentation

## Quick Reference

### 4-Level Hierarchy
```
Workspace → Project → Version → Component
01-tray/Embedded/CSV_Upload_v1_[UUID]/versions/current/scripts/
```

### Critical Rules
1. **NEVER modify UUID-based directory names** (breaks sync)
2. **NEVER edit project-metadata.json manually** (sync-managed)
3. **ALWAYS work within version directories** (current/ or 1.0/)
4. **ALWAYS verify path before modifications** (pwd check)

### Correct Navigation Pattern
```bash
cd 01-tray/[Workspace]/[Project_UUID]/versions/current/scripts/
```

### Common Pitfalls
- ❌ Working at project root instead of version directory
- ❌ Renaming directories with UUIDs
- ❌ Manual metadata.json edits
- ✅ Use tray-sync.js for all sync operations
