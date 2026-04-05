---
name: test-script
description: >
  Run Tray script tester with automatic environment validation, dependency
  installation, and execution of node run.js in a script directory.
  TRIGGER when: user wants to test a Tray.io script, run a script tester,
  validate script output, or execute run.js against input.json.
---

# Test Tray Script

Execute the script tester for a Tray integration script with automatic environment validation and setup.

## Arguments

Optional path to script directory (defaults to current directory).

## Execution Steps

1. **Determine target directory**
   - If argument provided, use that path
   - Otherwise, use current working directory

2. **Validate environment**
   - Check for required files: `script.js`, `input.json`, `run.js`, `package.json`
   - If any are missing, report error with clear guidance

3. **Install dependencies**
   - Check if `node_modules/` directory exists
   - If missing, run `npm install` and report progress
   - Capture any installation errors

4. **Execute script tester**
   - Run `node run.js` in the script directory
   - Capture both stdout and stderr
   - Measure execution time

5. **Format results**
   - Display script output with syntax highlighting
   - Detect and highlight errors (red) vs. success (green)
   - Show execution time
   - If errors detected, parse error messages and suggest fixes

## Examples

- "Run the tests for my order transform script" -- validate environment, install deps, execute `node run.js`, and report pass/fail
- "Test this script with the sample input" -- check for `script.js` and `input.json`, run the tester, highlight any errors
- "My Tray script is throwing an error, help me debug it" -- execute the script, parse the stack trace, and suggest fixes

## Delegation

Do not trigger this skill for:
- Writing or generating new Tray scripts from scratch -- delegate to `tray-script-generator`
- Debugging Tray error patterns or retry logic -- delegate to `tray-errors`
- Deploying scripts to Tray.io -- delegate to `deploy-prep`

## Error Handling

- **Missing required files**: List which files are missing and suggest creating them from template
- **npm install failures**: Show error message and check for common issues (Node version, permissions)
- **Script execution errors**: Parse error stack trace, identify file:line, suggest functional pattern fixes
- **Missing input.json**: Prompt to create empty object `{}` or generate from workflow context
