# Update Destination Script - Complete Reference

## Overview

`update_destination.py` is an interactive automation tool for adding `androidKotlin` and `iosSwift` cloud mode support to destination integrations. It provides safe, resumable, batch processing of 171 destinations with automatic validation and state management.

## Quick Start

```bash
# Preview changes for a destination (dry-run)
python3 update_destination.py --destination am --dry-run

# Update a specific destination
python3 update_destination.py --destination am --update

# Process next destination from tracking list
python3 update_destination.py --next --update

# Resume from last processed destination
python3 update_destination.py --resume --update
```

## Features

### Core Features

- **Interactive Processing** - Manual review and confirmation after each destination
- **Resume Capability** - Interrupt and resume anytime using state file
- **Batch Tracking** - Automatic prompts every 20 destinations for commits
- **Dry-Run Mode** - Preview changes without modifying files
- **State Management** - Persistent progress tracking in `.migration-state.json`
- **Automatic Validation** - JSON structure validation and npm test execution
- **Tracking Updates** - Automatic updates to `destinations-tracking.md`

### Safety Features

- **Backup Creation** - Automatic backup before modifications
- **Revert on Failure** - Automatic rollback if validation fails
- **Change Preview** - Clear summary of all changes before applying
- **Format Preservation** - Maintains original JSON formatting

## Command-Line Options

### Required Arguments

One of the following must be specified:

- `--destination <name>` or `-d <name>` - Process a specific destination
- `--next` or `-n` - Process next destination from tracking file
- `--resume` or `-r` - Resume from last processed destination

### Optional Arguments

- `--update` or `-u` - Apply changes (without this, runs in dry-run mode)
- `--dry-run` - Explicitly run in preview mode (default if --update not specified)
- `--verbose` or `-v` - Show detailed logging output

### Examples

```bash
# Dry-run specific destination
python3 update_destination.py -d segment --dry-run

# Update with verbose output
python3 update_destination.py -d am -u -v

# Process next destination
python3 update_destination.py -n -u

# Resume after interruption
python3 update_destination.py -r -u
```

## What It Does

### 1. db-config.json Updates

Adds cloud-only support for new mobile sources:

```json
{
  "config": {
    "supportedSourceTypes": [
      "android",
      "androidKotlin",    // ← Added after android
      "ios",
      "iosSwift",         // ← Added after ios
      ...
    ],
    "supportedConnectionModes": {
      "android": ["cloud", "device"],
      "androidKotlin": ["cloud"],    // ← Added (cloud only)
      "ios": ["cloud", "device"],
      "iosSwift": ["cloud"],         // ← Added (cloud only)
      ...
    },
    "destConfig": {
      "android": [...],
      "androidKotlin": [              // ← Added with minimal config
        "connectionMode",
        "consentManagement"
      ],
      "ios": [...],
      "iosSwift": [                   // ← Added with minimal config
        "connectionMode",
        "consentManagement"
      ],
      ...
    }
  }
}
```

**Changes Made:**

- Inserts `androidKotlin` immediately after `android` in `supportedSourceTypes`
- Inserts `iosSwift` immediately after `ios` in `supportedSourceTypes`
- Adds `androidKotlin: ["cloud"]` to `supportedConnectionModes`
- Adds `iosSwift: ["cloud"]` to `supportedConnectionModes`
- Adds minimal `destConfig` entries with `["connectionMode", "consentManagement"]`

**Preservation:**

- Original JSON formatting preserved (indentation, spacing)
- Existing comments preserved
- No reordering of other fields

### 2. ui-config.json Updates (Conditional)

Updates only if cloud mode prerequisites exist:

```json
{
  "preRequisites": {
    "fields": [
      { "configKey": "connectionMode.android", "value": "cloud" },
      { "configKey": "connectionMode.androidKotlin", "value": "cloud" },  // ← Added
      { "configKey": "connectionMode.ios", "value": "cloud" },
      { "configKey": "connectionMode.iosSwift", "value": "cloud" },       // ← Added
      ...
    ]
  }
}
```

**Logic:**

- Finds prerequisites with `connectionMode.android` and `value: "cloud"`
- Inserts `connectionMode.androidKotlin` with `value: "cloud"` immediately after
- Finds prerequisites with `connectionMode.ios` and `value: "cloud"`
- Inserts `connectionMode.iosSwift` with `value: "cloud"` immediately after
- **Skips** device and hybrid mode prerequisites (cloud-only migration)
- **Skips** destinations with no ui-config.json or no cloud mode prerequisites

### 3. schema.json Regeneration

Automatically runs schema generator after config updates:

```bash
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/schemaGeneratorV2.py \
  -name="<destination>" -update destination
```

**Benefits:**

- Uses V2 generator (preserves formatting and existing fields)
- Automatic validation after generation
- Integrated into workflow (no manual step needed)

## Interactive Workflow

### Step-by-Step Process

1. **Script Processes Destination**

   - Updates db-config.json
   - Updates ui-config.json (if applicable)
   - Regenerates schema.json
   - Shows summary of changes

2. **Tracking Updated** (⬜ → 🟨)

   - Status changes to "in progress" in destinations-tracking.md

3. **User Reviews Changes**

   - Check updated files in editor
   - Test functionality in UI if needed
   - Verify validation results

4. **Prompt for Action**

   ```
   Run validation checks? (y/n):
   ```

   - `y` - Runs JSON and npm validation
   - `n` - Skips validation

5. **Final Decision**

   ```
   Options:
     y - Mark complete and continue to next
     n - Revert changes and continue to next
     s - Skip this destination
     q - Save state and quit

   Your choice:
   ```

6. **Outcome Actions**
   - **Complete (y)**: Tracking updated (🟨 → ✅), backup removed, continue
   - **Revert (n)**: Changes reverted, tracking updated (🟨 → ⬜), continue
   - **Skip (s)**: Changes reverted, tracking updated (🟨 → ⬜), continue
   - **Quit (q)**: State saved, can resume later

### Batch Checkpoints

Every 20 destinations:

```
🎉 Batch of 20 completed! (20 total)
Consider creating a commit for this batch.
Continue to next destination? (y/n):
```

**Recommended Actions:**

1. Review all changes: `git status`, `git diff`
2. Run tests: `npm run test:ci`
3. Create commit: `git add . && git commit -m "feat: add androidKotlin/iosSwift support (batch 1-20)"`
4. Push if desired: `git push`
5. Continue with `y` or quit with `n`

## State Management

### State File: `.migration-state.json`

Automatically maintained state file:

```json
{
  "last_processed": "am",
  "completed": ["segment", "ga4", "am"],
  "skipped": ["destination_with_issues"],
  "failed": [
    {
      "destination": "problem_dest",
      "error": "Schema generation failed"
    }
  ],
  "count": 3
}
```

### State Operations

**Automatic Save:**

- After each destination completes
- After each skip
- After each failure
- On quit

**Resume Behavior:**

- `--resume` continues from `last_processed + 1`
- If no `last_processed`, starts from first destination
- If all processed, reports completion

**Manual Management:**

```bash
# View current state
cat .migration-state.json

# Reset state (start over)
rm .migration-state.json

# Edit state (advanced)
vim .migration-state.json
```

## Validation

### JSON Structure Validation

Checks performed automatically:

**db-config.json:**

- ✅ `androidKotlin` in `supportedSourceTypes` at correct position (after android)
- ✅ `iosSwift` in `supportedSourceTypes` at correct position (after ios)
- ✅ `androidKotlin` in `supportedConnectionModes` with value `["cloud"]`
- ✅ `iosSwift` in `supportedConnectionModes` with value `["cloud"]`
- ✅ `androidKotlin` in `destConfig` with value `["connectionMode", "consentManagement"]`
- ✅ `iosSwift` in `destConfig` with value `["connectionMode", "consentManagement"]`

**ui-config.json:**

- ✅ Cloud mode prerequisites added correctly (if applicable)
- ✅ Prerequisites properly formatted

**schema.json:**

- ✅ Valid JSON
- ✅ Successfully regenerated

### npm Test Validation

Runs full validation test suite:

```bash
npx jest test/validation.test.ts --coverage=false --silent
```

**Tests Run:**

- All destination validation tests (3,258 tests)
- Source definition validation
- Account definition validation
- Core validation logic

**Note:** Coverage checks disabled to avoid false failures.

## Excluded Destinations

Already configured (automatically skipped):

- `adj` - Adjust
- `af` - AppsFlyer
- `braze` - Braze
- `fb` - Facebook App Events
- `firebase` - Firebase
- `webhook` - Webhook (reference destination)

## Troubleshooting

### Schema Generation Fails

**Symptom:** Schema regeneration returns non-zero exit code

**Solutions:**

1. Check db-config.json is valid JSON: `python3 -m json.tool db-config.json`
2. Check ui-config.json is valid JSON: `python3 -m json.tool ui-config.json`
3. Run schema generator manually with verbose output:
   ```bash
   python3 configure-cloud-mode-sources-for-mobile-sources/scripts/schemaGeneratorV2.py \
     -name="<destination>" -v destination
   ```
4. Check error messages in schema generator output
5. Compare with webhook (reference destination)

### Validation Errors

**Symptom:** JSON validation fails

**Solutions:**

1. Run with verbose mode: `--verbose`
2. Check specific error messages
3. Manually inspect configuration files
4. Compare with similar destination
5. Review the configuration patterns section

### npm Tests Fail

**Symptom:** npm test validation fails even though changes look correct

**Possible Causes:**

- Other unrelated tests failing
- Coverage thresholds (already disabled in script)
- Test data missing for destination

**Solutions:**

1. Run tests manually to see full output:
   ```bash
   npx jest test/validation.test.ts --coverage=false
   ```
2. Check if it's a new failure or pre-existing
3. Run all tests: `npm test`
4. Check linting: `npm run check:lint`

### State File Corruption

**Symptom:** Script crashes or behaves unexpectedly

**Solutions:**

1. Backup state file: `cp .migration-state.json .migration-state.json.backup`
2. Inspect state file: `cat .migration-state.json`
3. Manually fix JSON errors
4. Or delete and restart: `rm .migration-state.json`
5. Restart from specific destination: `--destination <name>`

### Tracking Document Not Updating

**Symptom:** `destinations-tracking.md` not showing updated status

**Solutions:**

1. Check file exists and is writable
2. Check file format hasn't changed
3. Manually update if needed
4. Re-run script for that destination

## Advanced Usage

### Testing Strategy

**Phase 1: Test with 5 Destinations**

```bash
# Dry-run first
for dest in am segment customerio heap slack; do
  python3 update_destination.py --destination $dest --dry-run
done

# Then update one by one
python3 update_destination.py --destination am --update
# Review and test in UI
# If good, continue with others
```

**Phase 2: Process Batch of 20**

```bash
python3 update_destination.py --next --update
# Follow prompts, create commit after 20
```

**Phase 3: Complete All 171**

```bash
# Resume as needed
python3 update_destination.py --resume --update
# Continue until all processed
```

### Skipping Problematic Destinations

If a destination has issues:

1. Choose `s` to skip during interactive prompt
2. Document the issue
3. Continue with others
4. Return later to fix manually

### Batch Commits

Recommended commit strategy:

```bash
# After each batch of 20
git add .
git commit -m "feat: add androidKotlin/iosSwift support (batch 1-20)

- Updated db-config.json for all destinations
- Updated ui-config.json where applicable
- Regenerated schema.json files
- All validations passing"

git push
```

## Performance

**Per Destination:**

- Dry-run: ~1-2 seconds
- Update mode: ~3-5 seconds
- With validation: ~15-20 seconds (npm tests)

**Full Migration (171 destinations):**

- Without testing: ~15-20 minutes
- With validation: ~45-60 minutes
- With manual UI testing: Several hours (recommended)

## Best Practices

1. **Always Dry-Run First** - Preview changes before applying
2. **Test in Batches** - Don't process all 171 at once
3. **Review Changes** - Check git diff after each destination
4. **Test in UI** - Verify functionality works correctly
5. **Commit Regularly** - Batch commits every 20 destinations
6. **Keep State Safe** - Backup `.migration-state.json` periodically
7. **Monitor Tracking** - Check `destinations-tracking.md` for progress
8. **Document Issues** - Note any problems for later review

## Integration

### Used By

- Manual migration workflow
- Batch processing scripts
- CI/CD pipelines (with --update flag)

### Calls

- `schemaGeneratorV2.py` - For schema regeneration
- `npm test` - For validation
- Updates `destinations-tracking.md` automatically

### Input Files

- `destinations-tracking.md` - List of destinations to process
- `src/configurations/destinations/*/db-config.json`
- `src/configurations/destinations/*/ui-config.json`

### Output Files

- `.migration-state.json` - Progress state
- Updated destination configuration files
- Updated `destinations-tracking.md`

## Reference

**Script Location:**

```
configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py
```

**Related Documentation:**

- [Schema Generator](./schema-generator.md) - Schema regeneration tool
- `../plan.md` - Overall migration plan
- `../destinations-tracking.md` - Progress tracking
- Reference destination: `src/configurations/destinations/webhook/`

**Related Commands:**

```bash
# Run from repo root
cd /Users/abhishekpandey/Documents/Abhishek/workspace/rudder-integrations-config

# View full command path
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py --help
```
