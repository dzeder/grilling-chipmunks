# Tray.io Project Architecture Standards

**Purpose**: Define the structural organization of Tray.io projects in the repository
**Audience**: Developers working with Tray.io project exports and local modifications
**Related**: `@../CLAUDE.md` - Main Tray.io development guide

---

## Overview

Tray.io projects in this repository follow a strict 4-level hierarchical structure that mirrors the Tray.io platform organization. Understanding this hierarchy is critical for maintaining project integrity during local development and sync operations.

---

## 4-Level Hierarchy

### Level 1: Workspaces

**Definition**: Top-level organizational containers in Tray.io platform

**Structure**:
```
01-tray/
├── Embedded/              # Embedded workspace
├── Payments/              # Payments workspace
└── [WorkspaceName]/       # Other workspaces
```

**Characteristics**:
- Represent different Tray.io workspace environments
- Contain multiple related projects
- Often correspond to business units or functional areas

### Level 2: Projects

**Definition**: Individual integration projects within a workspace

**Structure**:
```
Embedded/
├── CSV_Upload_v1/                    # Project name
├── EDI_OpenTextTBM/                  # Another project
└── [ProjectName]_[UUID]/             # UUID-based naming
```

**Characteristics**:
- Each project has a unique UUID identifier
- Directory name format: `ProjectName_UUID`
- Contains project metadata and version history
- **CRITICAL**: Never modify project directory names

### Level 3: Versions

**Definition**: Versioned snapshots of project configuration

**Structure**:
```
CSV_Upload_v1/
├── versions/
│   ├── current/          # Active development version
│   ├── 1.0/              # Specific version
│   ├── 1.1/              # Newer version
│   └── [version]/
└── project-metadata.json # Sync-managed, DO NOT EDIT
```

**Characteristics**:
- `current/` typically points to latest stable version
- Version numbers follow semantic versioning (1.0, 1.1, 2.0)
- Each version is complete, standalone snapshot
- Work happens within version directories

### Level 4: Components

**Definition**: Individual workflow scripts, diagrams, documentation within a version

**Structure**:
```
versions/current/
├── scripts/                        # Workflow scripts
│   ├── 01_Main/
│   │   ├── 1-execute_script/
│   │   │   ├── script.js          # Actual script code
│   │   │   ├── input.json         # Test data
│   │   │   ├── output.json        # Expected output
│   │   │   └── metadata.json      # Script metadata
│   │   └── workflow-metadata.json
│   └── [workflow-name]/
├── diagrams/                       # Mermaid diagrams
│   ├── project-overview.json
│   └── workflow-details/
├── documentation/                  # Project docs
│   ├── README.md
│   ├── CHANGELOG.md
│   └── API.md
└── raw-exports/                    # Full Tray export data
    └── export-data.json
```

**Characteristics**:
- Scripts contain actual integration logic
- Each script has test data and metadata
- Diagrams provide visual documentation
- Raw exports preserve full Tray configuration

---

## Critical Directory Standards

### UUID Preservation (MANDATORY)

**Rule**: **NEVER** modify UUID-based directory naming

**Why**:
- UUIDs link local repository to Tray.io platform projects
- Changing UUIDs breaks sync between local and cloud
- Project identification relies on UUID consistency

**Examples**:
- ✅ `CSV_Upload_v1_a1b2c3d4-e5f6-7890-abcd-ef1234567890/`
- ❌ `CSV_Upload_v1/` (UUID removed - sync will fail)
- ❌ `CSV_Upload_v2_a1b2c3d4-e5f6-7890-abcd-ef1234567890/` (renamed - sync breaks)

### Project Metadata (SYNC-MANAGED)

**Rule**: **NEVER modify** `project-metadata.json` files manually

**Why**:
- Managed by `tray-sync.js` automation
- Contains sync state, timestamps, version mappings
- Manual edits cause sync conflicts and data loss

**Location**: `[ProjectName_UUID]/project-metadata.json`

**When to modify**: Never directly. Use `tray-sync.js` commands instead:
```bash
cd /Users/derekhsquires/Documents/Ohanafy/Integrations/04-utilities/tools/sync-tools/
node src/tray-sync.js export <project-id>      # Updates metadata automatically
node src/tray-sync.js import <local-path>      # Uses metadata for sync
```

### Version Directory Workflow

**Rule**: Always work within version directories

**Correct workflow**:
```bash
# Navigate to version directory
cd 01-tray/Embedded/CSV_Upload_v1/versions/current/

# Modify scripts
vim scripts/01_Main/1-execute_script/script.js

# Test locally
cd scripts/01_Main/1-execute_script/
run  # Uses input.json, outputs to output.json

# Sync back to Tray when ready
cd /Users/derekhsquires/Documents/Ohanafy/Integrations/04-utilities/tools/sync-tools/
node src/tray-sync.js import /Users/derekhsquires/Documents/Ohanafy/Integrations/01-tray/Embedded/CSV_Upload_v1/
```

**Incorrect workflow**:
```bash
# ❌ Modifying at project root level
cd 01-tray/Embedded/CSV_Upload_v1/
vim project-metadata.json  # NEVER DO THIS

# ❌ Working outside version directories
cd 01-tray/Embedded/CSV_Upload_v1/
vim some-script.js  # Wrong location
```

---

## Directory Navigation Best Practices

### Finding the Right Version

1. **Identify the project**:
   ```bash
   cd 01-tray/Embedded/
   ls  # Shows all projects in workspace
   ```

2. **Navigate to project**:
   ```bash
   cd CSV_Upload_v1/
   ```

3. **Check available versions**:
   ```bash
   cd versions/
   ls  # Shows: current/, 1.0/, 1.1/, etc.
   ```

4. **Work in appropriate version**:
   ```bash
   cd current/  # For active development
   ```

### Understanding Version Selection

**Use `current/`** for:
- Active development and new features
- Bug fixes for production workflows
- Testing new integration patterns

**Use specific versions** (1.0, 1.1) for:
- Historical reference
- Rollback scenarios
- Comparing changes between versions

---

## Project Structure Validation

Before making changes, verify you're in the correct location:

```bash
# Expected path structure
pwd
# Should show: .../01-tray/[Workspace]/[ProjectName_UUID]/versions/[version]/

# Verify project metadata exists (one level up from version)
ls ../../project-metadata.json
# Should exist and be sync-managed

# Verify script structure
ls scripts/
# Should show numbered workflow directories
```

---

## Common Pitfalls

### 1. Working at Wrong Hierarchy Level

**Problem**: Modifying files outside version directories
```bash
# ❌ Wrong
cd 01-tray/Embedded/CSV_Upload_v1/
vim script.js  # No script.js at this level!
```

**Solution**: Always navigate to version directory first
```bash
# ✅ Correct
cd 01-tray/Embedded/CSV_Upload_v1/versions/current/scripts/01_Main/1-execute_script/
vim script.js
```

### 2. UUID Modification

**Problem**: Renaming project directories removes UUID
```bash
# ❌ Wrong
mv CSV_Upload_v1_abc123/ CSV_Upload_v2/
```

**Solution**: Never rename UUID-based directories. Use Tray.io platform to version projects.

### 3. Manual Metadata Edits

**Problem**: Editing project-metadata.json manually
```bash
# ❌ Wrong
vim CSV_Upload_v1/project-metadata.json
```

**Solution**: Use tray-sync.js automation for all metadata operations.

---

## See Also

- `@../CLAUDE.md` - Main Tray.io development guide
- `@tray-diagrams.md` - Mermaid diagram standards
- `@../../../04-utilities/tools/sync-tools/README.md` - Tray sync documentation
- `@../.claude/rules/git-workflow.md` - Git workflow for Tray projects
