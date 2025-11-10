# DisplayName Validation

## Overview

This validation system prevents changes to `displayName` values in existing destination definitions. The `displayName` field is used by other features and systems, and changing it would impact existing connections and integrations.

## How It Works

### Git Diff-Based Validation

The validation uses **git diff** to detect displayName changes, making it:

- ✅ **No baseline file needed** - Works directly with git history
- ✅ **Accurate** - Only catches actual modifications, not additions
- ✅ **Fast** - No file parsing or comparisons needed
- ✅ **Works everywhere** - Same script for pre-commit and CI/CD

### 1. Pre-commit Hook

- Automatically runs when you commit changes
- Checks **staged changes** for displayName modifications
- Blocks the commit if displayName changes are detected
- Located in `.husky/pre-commit`

### 2. GitHub Workflow

- Runs on every Pull Request
- Checks the **PR diff** against the base branch
- Fails the PR check if displayName changes are detected
- Located in `.github/workflows/validate-displayname.yml`

### 3. How It Detects Changes

The script:

1. Gets git diff for `src/configurations/destinations/*/db-config.json` files
2. Parses the diff to find lines with `"displayName":`
3. Compares removed vs. added displayName values
4. Ignores new destinations (only `+` lines, no `-` lines)
5. Reports an error if existing displayNames were modified

## Usage

### Running Validation Manually

```bash
# Check all uncommitted changes
npm run validate:displayname

# Check staged changes (for pre-commit)
npm run validate:displayname:staged

# Or run the script directly
node scripts/validateDisplayNameChanges.js

# Check staged changes
node scripts/validateDisplayNameChanges.js --staged

# Compare against a specific branch
node scripts/validateDisplayNameChanges.js --compare origin/main
```

### When DisplayName Changes Are Detected

If the validation fails, you'll see an error like:

```
❌ DisplayName changes detected!
═══════════════════════════════════════════════════════════════

DisplayNames cannot be changed as they are used by other features
and changing them will break existing connections.

The following displayName changes were found:

1. google_adwords_enhanced_conversions (src/configurations/destinations/google_adwords_enhanced_conversions/db-config.json)
   Old: "Google Ads Enhanced Conversions"
   New: "Google Ads Enhanced Conversions TEST"

═══════════════════════════════════════════════════════════════

What to do:
  1. Revert the displayName changes in the files listed above
  2. If you must change a displayName:
     - Coordinate with all dependent teams
     - Update all systems that use these displayNames
     - Document the change thoroughly
     - Get approval from tech leads
```

## Files

### Scripts

- `scripts/validateDisplayNameChanges.js` - Git diff-based validation script

### CI/CD

- `.github/workflows/validate-displayname.yml` - GitHub workflow for PR validation
- `.husky/pre-commit` - Pre-commit hook configuration

## Process for Changing DisplayNames

⚠️ **Important**: DisplayName changes should be rare and carefully coordinated.

If you absolutely need to change a displayName:

1. **Coordinate with dependent teams** - Ensure all systems that use displayNames can handle the change
2. **Update documentation** - Update any documentation that references the old displayName
3. **Test thoroughly** - Ensure the change doesn't break existing integrations
4. **Get approval** - Obtain approval from tech leads and stakeholders
5. **Communicate the change** - Notify all stakeholders about the displayName change
6. **Make the change** - Update the displayName in the db-config.json file
7. **The validation will fail** - This is expected and intentional
8. **Override the check** - Work with maintainers to merge the PR with proper approvals

## Adding New Destinations

When adding new destinations:

1. Create the destination with the appropriate `displayName`
2. The validation will **NOT** block new destinations
3. Only modifications to existing displayNames are blocked
4. Commit and push as normal

## How to Bypass (Emergency Only)

If you need to bypass the validation in an emergency (with proper approvals):

### Local Pre-commit

```bash
# Skip pre-commit hooks
git commit --no-verify -m "Emergency displayName change"
```

### GitHub PR

- The workflow must be manually overridden by repository administrators
- Requires proper approvals and documentation
- Should be treated as an exceptional case

## Troubleshooting

### Validation Fails But I Didn't Change displayName

- Check the git diff: `git diff HEAD -- src/configurations/destinations/*/db-config.json`
- Look for accidental whitespace or formatting changes to the displayName line
- Ensure your JSON formatting matches the original

### Validation Doesn't Detect My Change

- Make sure the change is in a `db-config.json` file under `src/configurations/destinations/`
- Verify the file is tracked by git
- Check that the diff shows both `-` and `+` lines for displayName

### Pre-commit Hook Not Running

- Ensure husky is installed: `npm install`
- Check that `.husky/pre-commit` exists and is executable
- Verify you're committing in the repository root

## Technical Details

### Script Capabilities

- Parses git diff output for destination config files
- Extracts displayName values from removed and added lines
- Filters out new destinations (no removed displayName)
- Provides clear error messages with file paths and changed values
- Supports multiple modes: staged, compare, and default

### Exit Codes

- `0` - No displayName changes detected (success)
- `1` - DisplayName changes detected (blocking)
- `2` - Script error (should not happen)

### Performance

- Very fast: Only processes git diff, not entire files
- Scales well: Performance independent of repository size
- No external dependencies: Uses only Node.js built-ins
