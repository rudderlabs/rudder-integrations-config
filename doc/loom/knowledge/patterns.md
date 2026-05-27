# Architectural Patterns

> Discovered patterns in the codebase that help agents understand how things work.
> This file is append-only - agents add discoveries, never delete.

(Add patterns as you discover them)

## Audience destination triad pattern

For any warehouse-to-audience destination that uses the accounts framework:

### Destination db-config.json required fields

```json
{
  "name": "<SCREAMING_SNAKE_CASE>",
  "displayName": "<Human Name>",
  "config": {
    "supportedAccountDefinitions": {
      "rudderAccountId": ["<ACCOUNT_NAME>"]
    },
    "transformAtV1": "router",
    "supportedSourceTypes": ["warehouse"],
    "supportedMessageTypes": { "cloud": ["record"] },
    "isAudienceSupported": true,
    "supportedConnectionModes": { "warehouse": ["cloud"] },
    "supportsBlankAudienceCreation": true,
    "disableJsonMapper": true,
    "supportsVisualMapper": true,
    "syncBehaviours": ["mirror"],
    "saveDestinationResponse": true,
    "destConfig": {
      "defaultConfig": ["rudderAccountId", "listId", "listName", "identifierMappings"],
      "warehouse": [
        "connectionMode",
        "consentManagement",
        "oneTrustCookieCategories",
        "ketchConsentPurposes"
      ]
    },
    "secretKeys": []
  },
  "options": { "isBeta": true }
}
```

**Key decisions:**

- `transformAtV1: "router"` — record-event (batch) destinations must use router, not processor
- `supportedAccountDefinitions.rudderAccountId` value is an array matching the account's `name` field exactly
- `secretKeys: []` — destination config holds no secrets; secrets are in the account triad

### Account db-config.json required fields

```json
{
  "name": "DESTINATION_<NAME>_<AUTH_TYPE>",
  "type": "<destination_name>",
  "category": "destination",
  "authenticationType": "api_key",
  "config": {
    "optionFields": ["<non-secret fields>"],
    "secretFields": ["<secret fields>"]
  }
}
```

**Key decisions:**

- `authenticationType: "api_key"` is a literal allowed value in `account-db-config-schema.json` (the VDM-next skill's suggestion of "custom" is superseded)
- `secretFields` lists field names that must be encrypted at rest — typically just `apiKey`
- `optionFields` lists non-secret config fields (e.g., `dataCenter`, `projectType`)

### Destination ↔ account cross-reference

The binding chain:

1. `destination/db-config.json` → `config.supportedAccountDefinitions.rudderAccountId: ["<ACCOUNT_NAME>"]`
2. `account/db-config.json` → `name: "<ACCOUNT_NAME>"` (must match exactly, character-for-character)

### UI wiring: accountManagementInput

The **first field** in the destination's `uiConfig.baseTemplate[0].sections[0].groups[0].fields` array MUST be:

```json
{
  "type": "accountManagementInput",
  "label": "<Platform> account",
  "configKey": "rudderAccountId"
}
```

This renders the account selector in the dashboard. Placing it elsewhere breaks the UI flow.

### Secret handling pattern

Two layers:

1. `account/db-config.json` → `config.secretFields: ["apiKey"]` — tells platform which fields are secrets
2. `account/ui-config.json` → textField with `"secret": true` — tells dashboard to mask the field

The platform uses the db-config classification; `options.<secretName>` path is shared with optionFields but separated by the platform based on db-config classification. Confirmed identical pattern in `fb_custom_audience/fb_custom_audience_access_token`.

## identifierMappings schema pattern (Iterable-style)

When the UI conditionally shows different identifier fields based on a `projectType` account option:

- The AJV `schema.json` is kept **permissive** on cardinality constraints (does not enforce min/max items)
- Per-row constraints (e.g., "email-based projects must have exactly one email mapping") are enforced at the transformer's Zod layer
- `identifierMappings` items use `iterableField: enum ["email", "userId"]` + `warehouseColumn: string`
- UI reads `accountOptions.projectType` via `preRequisites.fields[].configKey` to show/hide the right picker

## Iterable Audience actual config (post-simplification, 2026-05-27)

The `iterable_audience` destination was simplified after initial implementation via two commits:
- `02099d9d` removed `listId` and `listName` from `destConfig.defaultConfig`
- `827f2415` removed consent management fields (`consentManagement`, `oneTrustCookieCategories`, `ketchConsentPurposes`) from the `warehouse` destConfig key

**Actual current `db-config.json`:**

```json
{
  "name": "ITERABLE_AUDIENCE",
  "displayName": "Iterable Audience",
  "config": {
    "supportedAccountDefinitions": {
      "rudderAccountId": ["DESTINATION_ITERABLE_AUDIENCE_API_KEY"]
    },
    "supportsBlankAudienceCreation": true,
    "disableJsonMapper": true,
    "supportsVisualMapper": true,
    "syncBehaviours": ["mirror"],
    "transformAtV1": "router",
    "saveDestinationResponse": true,
    "supportedSourceTypes": ["warehouse"],
    "supportedMessageTypes": { "cloud": ["record"] },
    "isAudienceSupported": true,
    "supportedConnectionModes": { "warehouse": ["cloud"] },
    "destConfig": {
      "defaultConfig": ["rudderAccountId", "apiKey", "dataCenter", "projectType", "identifierMappings"],
      "warehouse": ["connectionMode"]
    },
    "secretKeys": ["apiKey"]
  },
  "options": { "isBeta": true }
}
```

**Key divergences from the general audience triad template (documented above):**

- `listId` and `listName` NOT in `defaultConfig` — list selection is handled by the VDM v2 form before the connection config is persisted
- Account fields (`apiKey`, `dataCenter`, `projectType`) ARE in `defaultConfig` — this is how the transformer receives account options and secrets as metadata. The `secretKeys: ["apiKey"]` entry ensures the platform passes the secret to the transformer.
- `warehouse` destConfig only has `["connectionMode"]` — no consent management fields for M1 (deferred to later)

**Actual current `schema.json`:**

```json
{
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["rudderAccountId", "identifierMappings"],
    "properties": {
      "rudderAccountId": { "type": "string", "pattern": "^.{1,100}$" },
      "identifierMappings": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "iterableField": { "type": "string", "enum": ["email", "userId"] },
            "warehouseColumn": { "type": "string" }
          }
        }
      },
      "connectionMode": {
        "type": "object",
        "properties": { "warehouse": { "type": "string", "enum": ["cloud"] } }
      }
    }
  }
}
```

Required: `rudderAccountId` + `identifierMappings` only. No `listId` (removed).

## Identifier mapping ui-config pattern (dot-notation configKeys)

The `iterable_audience` ui-config uses dot-notation paths as `configKey` to target array items directly:

```json
{
  "type": "textInput",
  "configKey": "identifierMappings.0.warehouseColumn",
  "preRequisites": {
    "fields": [
      { "configKey": "rudderAccountId", "exists": true },
      { "configKey": "accountOptions.projectType", "value": "email-based" }
    ],
    "condition": "and"
  }
},
{
  "type": "textInput",
  "configKey": "identifierMappings.1.warehouseColumn",
  "preRequisites": {
    "fields": [
      { "configKey": "rudderAccountId", "exists": true },
      { "configKey": "accountOptions.projectType", "value": "hybrid" }
    ],
    "condition": "and"
  }
}
```

**Key rules:**
- `accountOptions.projectType` in preRequisites reads from the linked account's option fields — NOT from the destination config
- `identifierMappings.N.warehouseColumn` as configKey writes directly to the Nth array item's `warehouseColumn` property
- The `iterableField` value for each index is NOT written by the UI — it must be pre-populated via the static form structure or inferred by position
- `schemaGenerator.py` will warn about path mismatches for these dot-notation configKeys — this is a known advisory (not a bug)

**Hybrid project pattern:** Two separate textInput fields both visible when `accountOptions.projectType === "hybrid"`. Index 0 → email column, index 1 → userId column. The ordering is load-bearing — transformer reads `identifierMappings[0]` and `identifierMappings[1]` by position.
