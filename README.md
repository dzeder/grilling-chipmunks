# daniels-ohanafy

Unified monorepo for Ohanafy development — combines [gstack](https://github.com/garrytan/gstack) (general-purpose workflow skills) with Salesforce-specific domain skills, agents, and project workspaces.

## Structure

```
.claude/skills/gstack/    # gstack — planning, review, ship, QA, browser automation
skills/                    # 33 Salesforce domain skills (Apex, Flow, LWC, SOQL, etc.)
agents/                    # 7 specialist agents (FDE + PS team roles)
shared/                    # Hook validators, LSP engine, code analyzer
tools/                     # Installer and hygiene checker
tests/                     # Validator and registry contract tests
scripts/                   # Deployment and credential configuration
docs/                      # Whitepaper and architecture diagrams
projects/                  # Integration project workspaces
```

## Setup

```bash
# 1. Clone
git clone git@github.com:dzeder/daniels-ohanafy.git
cd daniels-ohanafy

# 2. Build gstack browser binary
cd .claude/skills/gstack && ./setup && cd ../../..

# 3. Install Salesforce skills + hooks into ~/.claude/
bash tools/install.sh
```

## Adding new domain skills

Create a new directory under `skills/` with the appropriate prefix:

| Prefix | Domain |
|--------|--------|
| `sf-*` | Salesforce |
| `tray-*` | Tray.io |
| `ns-*` | NetSuite |
| `qbo-*` | QuickBooks Online |
| `xero-*` | Xero |
| `gs-*` | Google Stack |

Each skill needs a `SKILL.md` with YAML frontmatter (name, description) and trigger rules.

## License

MIT
