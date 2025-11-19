# AndroidKotlin/iOSSwift Cloud Mode Migration

Automation tools for adding cloud mode support for `androidKotlin` and `iosSwift` mobile sources to 171 RudderStack destination integrations.

## Overview

This project provides automated tooling to safely migrate destination configurations to support the new mobile SDK sources in cloud mode:

- **androidKotlin** - New Android SDK (Kotlin-based)
- **iosSwift** - New iOS SDK (Swift-based)

### What Gets Updated

For each destination:

1. **`db-config.json`** - Adds source types, connection modes (cloud only), and minimal destConfig
2. **`ui-config.json`** - Adds cloud mode prerequisites (if applicable)
3. **`schema.json`** - Regenerates with preserved formatting and fields

### Migration Status

- **Total Destinations:** 171
- **Already Configured:** 6 (adj, af, braze, fb, firebase, webhook)
- **To Migrate:** 165
- **Current Progress:** See [docs/README.md](./docs/README.md) for tracking files

## Quick Start

### Prerequisites

```bash
# Install Python dependencies (if needed)
pip3 install -r scripts/requirements.txt

# From repository root
cd /Users/abhishekpandey/Documents/Abhishek/workspace/rudder-integrations-config
```

### Update a Single Destination

```bash
# Preview changes (dry-run)
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --destination am --dry-run

# Apply changes
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --destination am --update
```

### Process All Destinations

```bash
# Start from first destination
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --next --update

# Script will:
# - Process one destination at a time
# - Show changes and wait for confirmation
# - Prompt every 20 destinations for batch commits
# - Save state for resume capability

# If interrupted, resume with:
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --resume --update
```

## Tools

### 1. Update Destination Script

Interactive automation for processing destinations one at a time.

**Features:**

- Dry-run mode for previewing changes
- Interactive confirmation after each destination
- Resume capability with state management
- Automatic validation (JSON + npm tests)
- Batch tracking every 20 destinations
- Automatic tracking document updates

**Documentation:** [docs/update-destination-script.md](./docs/update-destination-script.md)

### 2. Schema Generator V2

Safe schema.json regeneration with field preservation.

**Features:**

- Never removes existing fields
- Preserves original JSON formatting
- Intelligent pattern handling (keeps env variable support)
- Auto-fixes conditional field validation issues
- Clear change logging

**Documentation:** [docs/schema-generator.md](./docs/schema-generator.md)

## Workflow

### Step 1: Test with One Destination

```bash
# 1. Preview changes
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --destination clevertap --dry-run

# 2. Apply changes
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --destination clevertap --update

# 3. Review changes in files and test in UI

# 4. When prompted:
#    y - Mark complete and continue
#    n - Revert changes
#    s - Skip this destination
#    q - Save state and quit
```

### Step 2: Process in Batches

```bash
# Start processing from tracking file
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --next --update

# After every 20 destinations:
# - Review changes: git status, git diff
# - Run tests: npm run test:ci
# - Create commit: git commit -m "feat: add androidKotlin/iosSwift support (batch 1-20)"
# - Continue with next batch
```

### Step 3: Resume if Interrupted

```bash
python3 configure-cloud-mode-sources-for-mobile-sources/scripts/update_destination.py \
  --resume --update
```

## Configuration Patterns

### db-config.json

```json
{
  "config": {
    "supportedSourceTypes": [
      "android",
      "androidKotlin",    // ← Added
      "ios",
      "iosSwift",         // ← Added
      ...
    ],
    "supportedConnectionModes": {
      "androidKotlin": ["cloud"],    // ← Cloud only
      "iosSwift": ["cloud"],         // ← Cloud only
      ...
    },
    "destConfig": {
      "androidKotlin": ["connectionMode", "consentManagement"],  // ← Minimal
      "iosSwift": ["connectionMode", "consentManagement"],       // ← Minimal
      ...
    }
  }
}
```

### ui-config.json (Cloud Mode Prerequisites)

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

**Note:** Only cloud mode prerequisites are updated. Device and hybrid mode are not modified.

## Files and Structure

```
configure-cloud-mode-sources-for-mobile-sources/
├── README.md                          # This file
├── CLAUDE.md                          # AI assistant context
├── docs/                              # Comprehensive documentation
│   ├── README.md                      # Index of tracking files
│   ├── migration-overview.md          # Migration requirements & validation
│   ├── destinations-tracking-01.md    # Destinations 1-20
│   ├── destinations-tracking-02.md    # Destinations 21-40
│   ├── ...                            # (9 files total, 20 destinations each)
│   ├── destinations-tracking-09.md    # Destinations 161-171
│   ├── update-destination-script.md   # Update script reference
│   └── schema-generator.md            # Schema generator reference
├── plan.md                            # Master migration plan
├── rought-plan.md                     # Initial planning notes
└── scripts/
    ├── update_destination.py         # Main automation script
    ├── schemaGeneratorV2.py          # Schema generation tool
    └── .migration-state.json         # Auto-generated state file
```

## Validation

Each destination update includes automatic validation:

✅ **db-config.json structure**

- Source types in correct positions
- Cloud-only connection modes
- Minimal destConfig entries

✅ **ui-config.json** (if applicable)

- Cloud mode prerequisites correctly added

✅ **schema.json**

- Valid JSON
- Successfully regenerated

✅ **npm tests**

- Full validation test suite (3,258 tests)

## State Management

Progress is automatically tracked in `.migration-state.json`:

```json
{
  "last_processed": "am",
  "completed": ["clevertap", "ga4", "am"],
  "skipped": [],
  "failed": [],
  "count": 3
}
```

You can safely quit anytime and resume later.

## Progress Tracking

Track migration progress in the split tracking files:

- [Part 1](./docs/destinations-tracking-01.md) - Destinations 1-20
- [Part 2](./docs/destinations-tracking-02.md) - Destinations 21-40
- [Part 3](./docs/destinations-tracking-03.md) - Destinations 41-60
- [Part 4](./docs/destinations-tracking-04.md) - Destinations 61-80
- [Part 5](./docs/destinations-tracking-05.md) - Destinations 81-100
- [Part 6](./docs/destinations-tracking-06.md) - Destinations 101-120
- [Part 7](./docs/destinations-tracking-07.md) - Destinations 121-140
- [Part 8](./docs/destinations-tracking-08.md) - Destinations 141-160
- [Part 9](./docs/destinations-tracking-09.md) - Destinations 161-171

See [docs/README.md](./docs/README.md) for the complete index.

**Status Legend:**

- ⬜ Not started
- 🟨 In progress
- ✅ Completed

## Excluded Destinations

These destinations already support the new sources (automatically skipped):

- `adj` (Adjust)
- `af` (AppsFlyer)
- `braze` (Braze)
- `fb` (Facebook App Events)
- `firebase` (Firebase)
- `webhook` (Webhook - reference destination)

## Documentation

### Quick Reference

- **Quick Start:** This README
- **Tracking Files:** [docs/README.md](./docs/README.md)
- **Migration Overview:** [docs/migration-overview.md](./docs/migration-overview.md)
- **Update Script:** [docs/update-destination-script.md](./docs/update-destination-script.md)
- **Schema Generator:** [docs/schema-generator.md](./docs/schema-generator.md)

## Best Practices

1. **Always dry-run first** - Preview changes before applying
2. **Test in batches** - Process 20 destinations at a time
3. **Review changes** - Check git diff after each destination
4. **Test in UI** - Manually verify functionality
5. **Commit regularly** - Batch commits every 20 destinations
6. **Monitor tracking** - Keep `destinations-tracking.md` updated
7. **Save state** - Use quit option to pause safely

## Success Criteria

For each destination:

- ✅ db-config.json has cloud-only support for new sources
- ✅ ui-config.json has cloud mode prerequisites (if applicable)
- ✅ schema.json successfully regenerated
- ✅ Validation tests pass
- ✅ No linting errors
- ✅ Manual UI testing confirms functionality

## Support

For questions or issues:

1. Check comprehensive docs in `docs/` folder
2. Review examples in webhook destination
3. Check troubleshooting sections in docs
4. Review `plan.md` for context

## Timeline

- **Phase 1:** Tool development ✅ Complete
- **Phase 2:** Tool testing ✅ Complete
- **Phase 3:** Full migration - In progress (0/165 destinations)

Estimated time: 8-12 hours with manual UI testing per batch.
