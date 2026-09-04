---
name: vdm-next-integration
description: Create the configuration definition for a new VDM Next (Visual Data Mapper) destination. Registers the destination, defines capabilities, and sets up authentication.
argument-hint: <destination-name> <auth-type:oauth|apikey>
---

# VDM Next — Configuration Definition

**Objective:** Create the configuration files that register a new VDM Next destination in the RudderStack system.

## Inputs

- **Destination name**: `$ARGUMENTS[0]` (lowercase, e.g., `zoho`, `salesforce`)
- **Auth type**: `$ARGUMENTS[1]` — `oauth` or `apikey`

## Context

This is Step 1 in building a VDM Next integration.

## File Structure

```
src/configurations/destinations/<dest_name>/
├── db-config.json
├── ui-config.json
├── schema.json
└── accounts/<dest_name>_<auth_type>/
    ├── db-config.json
    ├── ui-config.json
    └── schema.json
```

Refer src/schemas/destinations/, src/schemas/account for adding any additional needed fields in the definition.

## Reference

[`CONVENTIONS.md`](../../../CONVENTIONS.md) is the repo-wide source of truth — read it first. The sections that bite here are [account definition naming](../../../CONVENTIONS.md#accountdefinition-naming-accountdefinitionname), [where account credential fields live](../../../CONVENTIONS.md#where-account-credential-fields-live), [string `pattern` / `regex`](../../../CONVENTIONS.md#string-pattern-and-regex), and [optional fields must accept the empty string](../../../CONVENTIONS.md#optional-fields-must-accept-the-empty-string).

Find existing VDM destinations by searching for `supportsVisualMapper: true` in `src/configurations/destinations/*/db-config.json`. Read their complete config (db-config, ui-config, schema, and accounts/) for patterns. **Copy their shape, not their rules** — most predate `CONVENTIONS.md`, so they will carry the deprecated `{{ }}` / `env.` regex prefix and other patterns the conventions now forbid. Where the two disagree, `CONVENTIONS.md` is current.

Also read the account definition schemas for structural rules:

- `src/schemas/account/account-db-config-schema.json`
- `src/schemas/account/account-schema-schema.json`
- `src/schemas/account/account-ui-config-schema.json`

## VDM Mandatory Fields in db-config.json

Every VDM Next destination **must** include:

```json
{
  "name": "<DEST_NAME_UPPER>",
  "displayName": "<Display Name>",
  "version": "1.0",
  "config": {
    "supportsVisualMapper": true,
    "disableJsonMapper": true,
    "supportedSourceTypes": ["warehouse"],
    "supportedMessageTypes": { "cloud": ["record"] },
    "transformAtV1": "router",
    "syncBehaviours": ["mirror"],
    "supportedConnectionModes": { "warehouse": ["cloud"] },
    "destConfig": {
      "defaultConfig": [""]
    }
  }
}
```

**For API Key auth:** change `auth.type` to `"custom"` and remove `rudderScopes`.

## Account Definition (Optional)

### OAuth pattern:

- `authenticationType: "oauth"`, `refreshOAuthToken: true`
- `optionFields`: non-secret config (e.g., `["region"]`)
- Name format: `DESTINATION_<DEST_NAME_UPPER>_OAUTH`
- **Requires** corresponding implementation in `rudder-auth` repo

### API Key pattern:

- `authenticationType: "custom"`
- `secretFields`: encrypted credentials (e.g., `["apiKey"]`)
- `optionFields`: non-secret config
- Name format: `DESTINATION_<DEST_NAME_UPPER>_APIKEY`

## Steps

1. Create `src/configurations/destinations/<dest_name>/`
2. Create `db-config.json` using the VDM template above — update name, displayName, auth, account definitions
3. Create `accounts/<dest_name>_<auth_type>/` with db-config.json, ui-config.json, schema.json (use existing VDM destination as template)
4. Create root `ui-config.json` — must include `accountManagementInput` field, connection mode, consent settings
5. Create root `schema.json` — must validate `rudderAccountId` and consent management
6. Declare the account fields in the destination `db-config.json` per [CONVENTIONS.md](../../../CONVENTIONS.md#where-account-credential-fields-live). The API Key pattern below is `authenticationType: "custom"`, so — unlike OAuth — it **is** subject to that check.
7. Run validation:

```bash
npm test -- --testPathPattern="<dest_name>"
python3 scripts/validate_account_definitions.py <dest_name>
```

CI runs the second one too, on any PR that touches `db-config.json` or `accounts/**` — but no npm
script or hook does, so run it locally rather than waiting for the build.

## Critical Rules

- `disableJsonMapper: true` is mandatory — without it, JSON mapper UI shows instead of visual mapper
- `transformAtV1: "router"` is required — VDM always uses router path
- `version: "1.0"` is required on every destination db-config (major.minor); start new destinations at `"1.0"`
- `supportedSourceTypes` must include `"warehouse"`
- `supportedMessageTypes` must be `{ cloud: ["record"] }`
- Account definition name format: `DESTINATION_{DEST_NAME_UPPER}_{AUTH_TYPE_UPPER}`
- For OAuth: the `rudder-auth` repo must have a matching passport strategy and refresh token implementation
