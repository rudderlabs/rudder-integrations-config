# DisplayName Validation

## Overview

This validation system prevents changes to `displayName` values in existing destination definitions. The `displayName` field is used by other features and systems, and changing it would impact existing connections and integrations.

## How It Works

### 1. Baseline File

- A baseline file (`test/data/displayName-baseline.json`) contains all current destination `displayName` values
- This file serves as the source of truth for what displayNames should be
- The baseline is generated from all existing destination `db-config.json` files

### 2. Pre-commit Auto-update

- **NEW**: The baseline is automatically updated during pre-commit hooks
- Only **new destinations** are added to the baseline - existing displayNames are never modified
- This ensures the baseline stays current with new destinations without breaking existing ones

### 3. Validation Test

- The test suite (`test/displayNameValidation.test.ts`) compares current displayNames against the baseline
- If any displayName has changed, the test fails with a clear error message
- The test runs as part of the CI/CD pipeline to prevent merging PRs with displayName changes

### 4. CI/CD Integration

- The validation runs automatically during the test phase
- PRs with displayName changes will fail the build
- This ensures no accidental displayName changes reach production

## Usage

### Running the Validation

```bash
# Run only the displayName validation test
npm test -- test/displayNameValidation.test.ts

# Run all tests (includes displayName validation)
npm test
```

### Updating the Baseline

The baseline is **automatically updated** during pre-commit hooks, so you typically don't need to run this manually. However, if needed:

```bash
# Safely add new destinations only (default behavior)
npm run update:displayname-baseline

# Override entire baseline (use with caution!)
npm run update:displayname-baseline:override

# Or run the script directly
node scripts/updateDisplayNameBaseline.js           # Safe mode
node scripts/updateDisplayNameBaseline.js --override # Override mode
```

**Note**: The pre-commit hook runs the safe mode automatically, so new destinations are always included in commits.

### When DisplayName Changes Are Detected

If the validation fails, you'll see an error like:

```
❌ DisplayName changes detected! DisplayNames cannot be changed as they are used by other features.
The following destinations have changed displayNames:

  • DESTINATION_NAME (directory_name/):
    Baseline: "Original Display Name"
    Current:  "Changed Display Name"

If you need to change a displayName:
1. Ensure all dependent systems can handle the change
2. Update the baseline by running: node scripts/updateDisplayNameBaseline.js
3. Coordinate with teams that depend on these displayNames
```

## Files

### Scripts

- `scripts/updateDisplayNameBaseline.js` - Updates the baseline file from current destination configs

### Tests

- `test/displayNameValidation.test.ts` - Main validation test suite

### Data

- `test/data/displayName-baseline.json` - Baseline file containing all current displayNames

## Process for Changing DisplayNames

⚠️ **Important**: DisplayName changes should be rare and carefully coordinated.

If you absolutely need to change a displayName:

1. **Coordinate with dependent teams** - Ensure all systems that use displayNames can handle the change
2. **Update documentation** - Update any documentation that references the old displayName
3. **Update the baseline** - Run `npm run update:displayname-baseline` to update the baseline
4. **Test thoroughly** - Ensure the change doesn't break existing integrations
5. **Communicate the change** - Notify all stakeholders about the displayName change

## Adding New Destinations

When adding new destinations:

1. Create the destination with the appropriate `displayName`
2. **That's it!** The pre-commit hook will automatically add the new destination to the baseline
3. The updated baseline file will be included in your commit automatically
4. No manual intervention required

## Troubleshooting

### Test Fails for New Destination

If you've added a new destination and the test is failing:

- Run `npm run update:displayname-baseline` to include the new destination in the baseline
- Commit the updated baseline file

### Baseline File Missing

If the baseline file is missing:

- Run `npm run update:displayname-baseline` to generate it
- The script will create the file with all current displayNames

### False Positives

If the test is failing but you haven't changed any displayNames:

- Check if someone else has added/removed destinations
- Regenerate the baseline with `npm run update:displayname-baseline`
- The baseline should be kept up to date in the repository
