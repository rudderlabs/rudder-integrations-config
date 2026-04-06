---
name: migrate-to-accounts-framework
description: Migrate a destination to the RudderStack accounts framework by adding account definitions and updating destination config, schema, UI config, and validation tests
argument-hint: <destination-name> (e.g. "amplitude" or "mixpanel")
---

## Migrate Destination to Accounts Framework

**Reference files — read all before starting:**
- `src/schemas/account/account-db-config-schema.json` — structure and field semantics for the account `db-config.json`
- `src/schemas/account/account-schema-schema.json` — structure for the account `schema.json` (`secretSchema` vs `optionsSchema`)
- `src/schemas/account/account-ui-config-schema.json` — structure for the account `ui-config.json`
- All existing account definitions under `src/configurations/destinations/*/accounts/` — read a representative sample for patterns and real examples

---

### Step 1: Gather context

- The destination name is in `$ARGUMENTS`. If not provided, ask the user.
- Read the destination's `db-config.json`, `ui-config.json`, and `schema.json`.
- Identify which fields belong at the account level:
  - **Secret fields** (`secretFields`): credentials stored encrypted — validated by `secretSchema`
  - **Option fields** (`optionFields`): non-secret account-level config — validated by `optionsSchema`
- Derive automatically — do not ask the user:
  - Auth type: infer from the credential fields (see `authenticationType` description in `account-db-config-schema.json`)
  - Account definition name: `DESTINATION_<DEST_NAME_UPPER>_<AUTH_TYPE_UPPER>`
  - Account directory name: lowercase of the above
  - Required/non-required: mirrors the destination's `schema.json` exactly
  - Field labels, placeholders, notes: copy from the destination's `ui-config.json`

**Ask the user only:** which fields should move to the account level (secret credential fields and non-secret option fields).

Do NOT proceed until confirmed.

---

### Step 2: Create the account definition directory and files

Create: `src/configurations/destinations/<destination>/accounts/<account_definition_name>/`

Use the schema files as the source of truth for structure. Use the existing account definitions under `src/configurations/destinations/*/accounts/` as reference for real-world patterns.

- **`db-config.json`** — follow `account-db-config-schema.json`; use `[]` for `optionFields` if there are none
- **`schema.json`** — follow `account-schema-schema.json`; the `required` array in both `secretSchema` and `optionsSchema` must mirror which fields are required in the destination's `schema.json`
- **`ui-config.json`** — follow `account-ui-config-schema.json`; copy labels, placeholders, and notes from the destination's `ui-config.json`

---

### Step 3: Update the destination's `db-config.json`

Add `supportedAccountDefinitions` and prepend `rudderAccountId` to `destConfig.defaultConfig`:

```json
"supportedAccountDefinitions": {
  "rudderAccountId": ["<ACCOUNT_DEFINITION_NAME>"]
}
```

```json
"destConfig": {
  "defaultConfig": ["rudderAccountId", "<existing fields...>"]
}
```

---

### Step 4: Update the destination's `ui-config.json`

Add `accountManagementInput` as the **first** field in the group containing the auth fields:

```json
{
  "type": "accountManagementInput",
  "label": "Event delivery account",
  "configKey": "rudderAccountId"
}
```

---

### Step 5: Update the destination's `schema.json`

**a)** Add `rudderAccountId` to `properties`:
```json
"rudderAccountId": {
  "type": "string",
  "pattern": "^.{1,100}$"
}
```

**b)** Replace the top-level `"required": ["<authField>"]` with a `oneOf` mutual-exclusivity constraint (place before `allOf` if present):
```json
"oneOf": [
  {
    "required": ["<authField>"],
    "not": { "required": ["rudderAccountId"] }
  },
  {
    "required": ["rudderAccountId"],
    "not": { "required": ["<authField>"] }
  }
]
```

---

### Step 6: Update validation tests

Append three test cases to `test/data/validation/destinations/<destination>.json` using the minimal valid config as the base:

```json
{
  "testTitle": "Valid config with only rudderAccountId (no <authField>)",
  "config": { "rudderAccountId": "acc123", "<other required fields>": "<values>" },
  "result": true
},
{
  "testTitle": "Invalid config with both <authField> and rudderAccountId present",
  "config": { "<authField>": "<value>", "rudderAccountId": "acc123", "<other required fields>": "<values>" },
  "result": false,
  "err": [
    " must NOT be valid",
    " must NOT be valid",
    " must match exactly one schema in oneOf"
  ]
},
{
  "testTitle": "Invalid config with neither <authField> nor rudderAccountId",
  "config": { "<other required fields>": "<values>" },
  "result": false,
  "err": [
    " must have required property '<authField>'",
    " must have required property 'rudderAccountId'",
    " must match exactly one schema in oneOf"
  ]
}
```

Error strings must match AJV output exactly.

---

### Step 7: Verify

```bash
npm test -- --testPathPattern="<destination>"
```

Fix any failures before finishing.

---

