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
      "warehouse": ["connectionMode", "consentManagement", "oneTrustCookieCategories", "ketchConsentPurposes"]
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
