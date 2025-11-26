# Destinations Tracking - Prerequisites

**Destinations with Android/iOS Cloud Mode Prerequisites** (9 total)

**Note**: These destinations have prerequisites for Android or iOS cloud mode configuration in their `ui-config.json` files. They are tracked separately from the regular destinations for easier management.

**Excluded destinations** (already configured): adj, af, braze, fb, firebase, webhook - these are NOT tracked in any file.

Legend:

- ⬜ Not Started
- 🟨 In Progress
- ✅ Completed

| Status | Destination          | db-config.json | schema.json | ui-config.json | Notes |
| ------ | -------------------- | -------------- | ----------- | -------------- | ----- |
| ⬜     | facebook_pixel       |                |             |                |       |
| ⬜     | fullstory            |                |             |                |       |
| ⬜     | ga4                  |                |             |                |       |
| ⬜     | ga4_v2               |                |             |                |       |
| ⬜     | intercom_v2          |                |             |                |       |
| ⬜     | iterable             |                |             |                |       |
| ⬜     | ninetailed           |                |             |                |       |
| ⬜     | optimizely_fullstack |                |             |                |       |
| ⬜     | sprig                |                |             |                |       |

## How to Update This File

### Column Checkmarks

Add checkmarks (✓) in the appropriate columns as each step is completed:

- **db-config.json**: After adding androidKotlin and iosSwift to supportedSourceTypes
- **schema.json**: After regenerating with the schema generator
- **ui-config.json**: After updating source-specific fields (if applicable)

### Notes Column

Use for:

- Issues encountered
- Special configurations needed
- Dependencies or blockers
