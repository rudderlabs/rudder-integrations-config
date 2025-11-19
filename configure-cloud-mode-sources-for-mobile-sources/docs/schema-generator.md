# Schema Generator V2 - Complete Reference

## Overview

`schemaGeneratorV2.py` is an improved schema generation tool that safely regenerates `schema.json` files for RudderStack integrations while preserving existing fields, formatting, and comprehensive validation patterns.

## Quick Start

```bash
# Preview changes (dry-run)
python3 schemaGeneratorV2.py -name="am" destination

# Apply changes
python3 schemaGeneratorV2.py -name="am" -update destination

# Process all destinations
python3 schemaGeneratorV2.py -all -update destination
```

## Key Features

### 1. Never Removes Fields ✅

Unlike the original generator, V2 **never removes** existing fields from schemas:

- Existing fields preserved even if not in current configs
- Only adds new fields or updates changed values
- Protects manual customizations and edge cases

**Example:**

```json
{
  "properties": {
    "existingField": { ... },      // ← Preserved
    "newField": { ... }             // ← Added
  }
}
```

### 2. Preserves Formatting ✅

Maintains original JSON structure:

- No unnecessary whitespace changes
- Preserves indentation (2 or 4 spaces)
- Keeps single-line arrays for enums
- Maintains comment-like structures
- No field reordering

**Result:** Git diffs only show actual changes, not formatting noise.

### 3. Intelligent Pattern Handling ✅

Preserves comprehensive regex patterns with environment variable support:

**Example Pattern:**

```json
{
  "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
}
```

**Logic:**

- If existing pattern includes `(^env[.].+)` → Keep it
- If existing pattern includes `\\{\\{.*\\|\\|` → Keep it
- If new pattern is simpler → Keep existing
- Only update if new pattern is more comprehensive

### 4. Conditional Field Validation ✅

Automatically detects and fixes conditional field placement issues:

**Problem:**
Fields with `preRequisites` should only appear in conditional schema blocks (`allOf`, `anyOf`, `oneOf`), NOT in root properties.

**Solution:**

- Scans for fields in conditional blocks
- Identifies duplicates in root properties
- Automatically removes from root
- Logs clear warnings

**Example:** Braze's `appKey` has prerequisites, so it should only be in `allOf` blocks:

```json
{
  "allOf": [
    {
      "if": { "properties": { "connectionMode": { "const": "device" } } },
      "then": {
        "properties": {
          "appKey": { ... }  // ← Correct location
        }
      }
    }
  ],
  "properties": {
    // "appKey" removed from here automatically
  }
}
```

### 5. Clear Change Logging ✅

Shows exactly what will change before updating:

```
5 change(s) detected for am:
  ✏️  - ADD properties.newField
  ✏️  - UPDATE properties.someField.default: false -> true
  ✏️  - ADD properties.anotherField
  ✏️  - UPDATE properties.existingField.type: string -> object
  ✏️  - MERGE required (added newRequiredField)
```

### 6. Safe by Default ✅

- Dry-run mode by default (requires `-update` flag to apply)
- Shows changes before applying
- Validates JSON after generation
- Clear confirmation needed for updates

## Comparison with Original Generator

| Feature              | Original `schemaGenerator.py`             | V2 `schemaGeneratorV2.py`        |
| -------------------- | ----------------------------------------- | -------------------------------- |
| **Formatting**       | Reformats entire file                     | Preserves original formatting    |
| **Field Removal**    | Removes fields not in configs             | Never removes existing fields    |
| **Pattern Changes**  | Simplifies patterns (removes env support) | Preserves comprehensive patterns |
| **Change Detection** | Shows warnings but hard to parse          | Clear, structured change log     |
| **Default Mode**     | Direct update                             | Dry-run (safe)                   |
| **Conditional Fix**  | N/A                                       | Auto-fixes conditional fields    |
| **Size Changes**     | -130 lines (for `am`)                     | 0 lines (for `am`)               |

## Command-Line Options

### Required Arguments

- `destination` or `source` - Type of integration to process

### Optional Arguments

- `-name="<name>"` - Process specific integration (e.g., `am`, `ga4_v2`)
- `-all` - Process all integrations under the selector
- `-update` - Apply changes (default is dry-run)
- `-v` or `--verbose` - Show detailed logging

### Examples

```bash
# Destinations
python3 schemaGeneratorV2.py -name="am" destination                    # Dry-run
python3 schemaGeneratorV2.py -name="am" -update destination            # Update
python3 schemaGeneratorV2.py -name="am" -v destination                 # Verbose
python3 schemaGeneratorV2.py -all -update destination                  # All destinations

# Sources
python3 schemaGeneratorV2.py -name="android" source                    # Dry-run
python3 schemaGeneratorV2.py -name="android" -update source            # Update
python3 schemaGeneratorV2.py -all -update source                       # All sources
```

## Output Examples

### No Changes Needed

```
🔍 DRY RUN MODE - No files will be modified
⚠️  Add -update flag to apply changes

============================================================
ℹ️  Processing am (destination)
============================================================
ℹ️  Generating schema for am...
ℹ️  Merging with existing schema for am...
ℹ️  Preserving existing pattern at properties.apiKey.pattern (more comprehensive)
ℹ️  Preserving existing pattern at properties.userProvidedPageEventString.pattern (more comprehensive)
✅ No changes needed for am
✨ Done!
```

### Changes Detected (Dry-Run)

```
🔍 DRY RUN MODE - No files will be modified
⚠️  Add -update flag to apply changes

============================================================
ℹ️  Processing segment (destination)
============================================================
ℹ️  Generating schema for segment...
ℹ️  Merging with existing schema for segment...

✏️  Adding new field: properties.newSetting
✏️  Updated properties.existingSetting.default: false -> true

5 change(s) detected for segment:
  ✏️  - ADD properties.newSetting
  ✏️  - UPDATE properties.existingSetting.default: false -> true
  ✏️  - ADD properties.anotherSetting
  ✏️  - UPDATE properties.oldSetting.type: string -> object
  ✏️  - MERGE required (added newRequiredField)

[DRY RUN] Would update src/configurations/destinations/segment/schema.json
⚠️  Run with -update flag to apply changes
```

### Conditional Field Issues Detected

```
============================================================
ℹ️  Processing braze (destination)
============================================================
ℹ️  Generating schema for braze...
✏️  Adding new field: properties.appKey
✏️  Adding new field: properties.restApiKey

2 change(s) detected for braze:
  ✏️  - ADD properties.appKey
  ✏️  - ADD properties.restApiKey

⚠️  Field 'appKey' appears in both root properties AND conditional blocks (allOf/anyOf).
    It should only be in conditionals.
⚠️  Field 'restApiKey' appears in both root properties AND conditional blocks (allOf/anyOf).
    It should only be in conditionals.

⚠️  Found 2 conditional field(s) incorrectly in root properties:
    - appKey (has preRequisites)
    - restApiKey (has preRequisites)
✏️  Cleaned: Removed 2 conditional field(s) from root properties

============================================================
⚠️  VALIDATION ISSUES FOUND FOR BRAZE
============================================================
  • Field 'appKey' appears in both root properties AND conditional blocks
  • Field 'restApiKey' appears in both root properties AND conditional blocks

💡 These fields were automatically cleaned from root properties.
   They will only appear in conditional (allOf/anyOf) blocks.
============================================================

✅ No content changes for braze (skipping to preserve formatting)
```

**Explanation:** The generator tried to add `appKey` and `restApiKey` to root properties, but detected they also exist in `allOf` blocks (because they have `preRequisites`). It automatically removed them from root, and since the cleaned schema matched the existing one, no update was needed.

### Update Mode (Changes Applied)

```
============================================================
ℹ️  Processing ga4 (destination)
============================================================
ℹ️  Generating schema for ga4...
ℹ️  Merging with existing schema for ga4...

✏️  Adding new field: properties.measurementId

1 change(s) detected for ga4:
  ✏️  - ADD properties.measurementId

✅ Updated src/configurations/destinations/ga4/schema.json
✨ Done!
```

## Merge Strategy

The V2 generator uses intelligent deep-merge logic:

### Field-Level Decisions

1. **Field exists in schema but not generated** → **KEEP IT** (never remove)
2. **Field exists in generated but not schema** → **ADD IT**
3. **Field exists in both** → Recursively merge with these rules:

### Data Type Rules

| Type                | Strategy                   | Example                        |
| ------------------- | -------------------------- | ------------------------------ |
| **Dictionary**      | Recursive merge            | Merge nested objects           |
| **List (required)** | Union                      | `["a"] + ["b"]` → `["a", "b"]` |
| **List (enum)**     | Use generated              | `["x", "y"]` → Use new values  |
| **Pattern**         | Keep if more comprehensive | Preserve env variable patterns |
| **Primitive**       | Use generated              | Use new value                  |

### Pattern Comprehensiveness

A pattern is considered **more comprehensive** if it includes:

- **Environment variable support:** `(^env[.].+)`
- **Template support:** `(^\\{\\{.*\\|\\|(.*)\\}\\}$)`
- **Longer pattern length** (as proxy for complexity)

**Example:**

```python
# Simple pattern (generated)
"^(.{0,100})$"

# Comprehensive pattern (existing, preserved)
"(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
```

## Conditional Field Validation

### The Problem

When fields have `preRequisites` in ui-config.json, they should ONLY appear in conditional schema blocks, not in root properties.

**Bad Schema:**

```json
{
  "properties": {
    "appKey": { ... }  // ← WRONG: Also in conditionals
  },
  "allOf": [
    {
      "if": { ... },
      "then": {
        "properties": {
          "appKey": { ... }  // ← Correct location
        }
      }
    }
  ]
}
```

**Good Schema:**

```json
{
  "properties": {
    // appKey removed from here
  },
  "allOf": [
    {
      "if": { ... },
      "then": {
        "properties": {
          "appKey": { ... }  // ← Only location
        }
      }
    }
  ]
}
```

### The Solution

V2 automatically:

1. **Scans conditional blocks** - Recursively finds all fields in `allOf`/`anyOf`/`oneOf`
2. **Checks root properties** - Identifies fields in both places
3. **Auto-cleans** - Removes duplicates from root
4. **Logs warnings** - Shows which fields were cleaned and why

### Example: Braze

**ui-config.json:**

```json
{
  "configKey": "appKey",
  "preRequisites": {
    "fields": [{ "configKey": "connectionMode.android", "value": "device" }]
  }
}
```

**Result:**

- `appKey` automatically removed from root properties
- `appKey` only appears in `allOf` block with `connectionMode.android = device` condition
- Clear warning logged for transparency

## Use Cases

### Use V2 When:

- ✅ Updating existing schemas safely
- ✅ Preserving manual customizations
- ✅ Maintaining formatting consistency
- ✅ Need to see changes before applying
- ✅ Working with production configs
- ✅ Updating schemas with environment variable patterns
- ✅ Processing multiple destinations/sources

### Use Original When:

- Creating brand new integration from scratch
- Want to completely regenerate schema (destructive)
- Debugging differences between configs and schema
- Don't care about preserving existing fields

## Workflow Integration

### Called By

- `update_destination.py` - Automatic call after config updates
- Manual execution for schema-only updates
- Batch processing scripts

### Input Files

- `src/configurations/destinations/*/db-config.json`
- `src/configurations/destinations/*/ui-config.json`
- `src/configurations/destinations/*/schema.json` (existing)

### Output Files

- `src/configurations/destinations/*/schema.json` (updated)

### Process Flow

```
1. Read db-config.json and ui-config.json
2. Generate new schema using original generator
3. Read existing schema.json
4. Deep-merge generated with existing (preserve fields)
5. Scan for conditional field issues
6. Auto-clean conditional fields from root
7. Compare merged vs existing
8. Show changes
9. Update if -update flag provided
```

## Best Practices

### Always Dry-Run First

```bash
# Preview changes
python3 schemaGeneratorV2.py -name="am" destination

# Review output

# Apply if satisfied
python3 schemaGeneratorV2.py -name="am" -update destination
```

### Verify Changes

```bash
# After update, check diff
git diff src/configurations/destinations/am/schema.json

# Ensure only expected changes
```

### Use Verbose Mode for Debugging

```bash
python3 schemaGeneratorV2.py -name="am" -v destination
```

### Batch Processing

```bash
# Test all first (dry-run)
python3 schemaGeneratorV2.py -all destination

# Review output for any issues

# Apply to all
python3 schemaGeneratorV2.py -all -update destination

# Review git diff
git diff src/configurations/destinations/
```

## Troubleshooting

### Generation Fails

**Symptoms:** Script exits with error

**Common Causes:**

- Invalid JSON in db-config.json or ui-config.json
- Missing required fields in configs
- Python syntax errors

**Solutions:**

1. Validate JSON files: `python3 -m json.tool db-config.json`
2. Check for syntax errors in configs
3. Run with verbose: `-v`
4. Check original generator works: Try original `schemaGenerator.py`

### No Changes When Expected

**Symptoms:** Shows "No changes needed" but you added new fields

**Common Causes:**

- New fields already exist in schema
- Merge logic preserving existing values

**Solutions:**

1. Check existing schema.json for the field
2. Run with verbose to see merge decisions: `-v`
3. Verify db-config.json and ui-config.json have the new field

### Unexpected Changes

**Symptoms:** Changes shown that you didn't expect

**Common Causes:**

- Schema out of sync with configs
- Manual edits to schema being corrected
- Required fields updated

**Solutions:**

1. Review change log carefully
2. Compare with configs to understand why
3. Check if it's a correction of an inconsistency
4. Use verbose mode for details

### Formatting Changes

**Symptoms:** Large diffs with formatting changes

**Common Causes:**

- Schema has unusual formatting
- Mixed indentation

**Solutions:**

1. V2 should preserve formatting - if not, report issue
2. Check if original schema has consistent formatting
3. May need to accept one-time formatting fix

## Performance

**Per Destination:**

- Dry-run: ~0.5-1 second
- Update mode: ~1-2 seconds

**All Destinations (190+):**

- Dry-run: ~2-3 minutes
- Update mode: ~3-5 minutes

## Technical Details

### Dependencies

- Python 3.6+
- Original `schemaGenerator.py` (for core generation)
- `json` module (standard library)
- `re` module (for pattern analysis)

### File Locations

**Script:**

```
configure-cloud-mode-sources-for-mobile-sources/schemaGenerator/schemaGeneratorV2.py
```

**Destination Configs:**

```
src/configurations/destinations/<name>/
  ├── db-config.json
  ├── ui-config.json
  └── schema.json
```

**Source Configs:**

```
src/configurations/sources/<name>/
  ├── db-config.json
  ├── ui-config.json
  └── schema.json
```

## Known Limitations

1. **Depends on Original Generator** - Still uses original generator for initial schema creation
2. **No Field Validation** - Doesn't validate if preserved fields should actually exist
3. **Pattern Heuristic** - Pattern comprehensiveness check is heuristic-based

## Future Improvements

Potential enhancements:

- [ ] Standalone implementation (remove dependency on original)
- [ ] Validation of preserved fields against db-config
- [ ] Better diff visualization (side-by-side)
- [ ] Schema validation after generation
- [ ] Support for custom merge rules per field type
- [ ] Interactive mode for ambiguous merge decisions
- [ ] Integration with validation test suite

## Reference

**Script Location:**

```
configure-cloud-mode-sources-for-mobile-sources/scripts/schemaGeneratorV2.py
```

**Related Documentation:**

- [Update Destination Script](./update-destination-script.md) - Migration automation
- `../plan.md` - Overall migration plan
- Original generator: `scripts/schemaGenerator.py`

**Related Commands:**

```bash
# Run from repo root
cd /Users/abhishekpandey/Documents/Abhishek/workspace/rudder-integrations-config

# Full command path
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/schemaGeneratorV2.py -name="am" destination
```
