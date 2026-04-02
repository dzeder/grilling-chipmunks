---
name: deploy-prep
description: Validate Tray scripts against functional programming patterns, check Salesforce API compliance, validate CSV output format, run tests, and generate a deployment checklist.
---

# Deployment Preparation

Validate a Tray script against functional programming patterns and generate a comprehensive deployment checklist.

## Arguments

Script name or path to validate (defaults to `./script.js`).

## Execution Steps

1. **Locate script file**
   - If argument is a path, use directly
   - If argument is a name, search for `script.js` in current directory
   - Default to `./script.js` if no argument provided

2. **Validate functional patterns**
   - No inline arrow functions in `exports.step`
   - No direct mutation (check for `push()`, `splice()` without spread)
   - No `console.log` statements in production code
   - Proper destructuring patterns
   - Pure functions (no side effects)
   - Immutable data transformations

3. **Check Salesforce API compliance** (if applicable)
   - URL encoding on field values
   - Composite request structure follows standard
   - Proper error handling for API responses

4. **Validate CSV output format** (if applicable)
   - Headers match expected format
   - Proper escaping and quoting
   - No malformed rows

5. **Run available tests**
   - Check for `package.json` test script
   - Execute `npm test` if available
   - Report test results with pass/fail counts

6. **Generate deployment checklist**
   - Create markdown checklist with ✓/✗ for each validation
   - Include file:line references for any issues found
   - Provide specific fix recommendations

## Validation Rules

### Functional Pattern Violations
- **Inline arrow functions**: `exports.step = (input, config) => { ... }` → Extract to named function
- **Direct mutation**: `array.push(item)` → Use `[...array, item]`
- **Console logging**: `console.log(...)` → Remove before deployment
- **Impure functions**: Side effects detected → Refactor to pure function

### Salesforce API Issues
- **Missing URL encoding**: Field values must be encoded
- **Invalid composite structure**: Must follow standard request format
- **No error handling**: Add try/catch for API calls

### CSV Format Issues
- **Missing headers**: First row must contain column names
- **Improper escaping**: Quotes and commas must be escaped
- **Inconsistent columns**: All rows must have same number of columns
